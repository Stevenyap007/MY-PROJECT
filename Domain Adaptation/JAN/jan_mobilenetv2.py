import os
import json
import csv
import time
from typing import Dict

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models

from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix


# =========================================================
# 1. Utilities
# =========================================================

def set_seed(seed=42):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def save_checkpoint(state, filename):
    torch.save(state, filename)


# =========================================================
# 2. JMMD IMPLEMENTATION
# =========================================================

class GaussianKernel(nn.Module):
    def __init__(self, sigma=None):
        super().__init__()
        self.sigma = sigma

    def forward(self, x, y):
        dist = torch.cdist(x, y, p=2) ** 2
        if self.sigma is None:
            self.sigma = dist.mean().detach()
        return torch.exp(-dist / (2 * self.sigma))


class JointMMD(nn.Module):
    """
    JMMD( (f_s, y_s), (f_t, y_t) )
    """
    def __init__(self):
        super().__init__()
        self.k_feat = GaussianKernel()
        self.k_pred = GaussianKernel()

    def forward(self, source, target):
        f_s, y_s = source
        f_t, y_t = target

        K_ss = self.k_feat(f_s, f_s) * self.k_pred(y_s, y_s)
        K_tt = self.k_feat(f_t, f_t) * self.k_pred(y_t, y_t)
        K_st = self.k_feat(f_s, f_t) * self.k_pred(y_s, y_t)

        loss = K_ss.mean() + K_tt.mean() - 2 * K_st.mean()
        return loss


# =========================================================
# 3. JAN MODEL (MobileNetV2)
# =========================================================

class JANMobileNetV2(nn.Module):
    def __init__(self, num_classes=7, pretrained=True):
        super().__init__()
        base = models.mobilenet_v2(pretrained=pretrained)

        self.features = base.features
        self.pool = nn.AdaptiveAvgPool2d((1, 1))

        self.bottleneck = nn.Sequential(
            nn.Linear(1280, 256),
            nn.BatchNorm1d(256),
            nn.ReLU()
        )

        self.classifier = nn.Linear(256, num_classes)

    def forward(self, x):
        x = self.features(x)
        x = self.pool(x)
        x = x.view(x.size(0), -1)

        feat = self.bottleneck(x)
        logits = self.classifier(feat)

        return logits, feat


# =========================================================
# 4. DATA LOADERS
# =========================================================

def build_dataloaders(
    isic_root,
    fitz_unlabeled_root,
    fitz_labeled_root=None,
    batch_size=16,
    num_workers=2
) -> Dict[str, DataLoader]:

    transform_train = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor()
    ])

    transform_test = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor()
    ])

    source_ds = datasets.ImageFolder(isic_root, transform=transform_train)
    target_ds = datasets.ImageFolder(fitz_unlabeled_root, transform=transform_train)

    source_loader = DataLoader(
        source_ds, batch_size=batch_size, shuffle=True,
        num_workers=num_workers, drop_last=True
    )

    target_loader = DataLoader(
        target_ds, batch_size=batch_size, shuffle=True,
        num_workers=num_workers, drop_last=True
    )

    loaders = {
        "source": source_loader,
        "target": target_loader
    }

    if fitz_labeled_root is not None:
        test_ds = datasets.ImageFolder(fitz_labeled_root, transform=transform_test)
        test_loader = DataLoader(
            test_ds, batch_size=batch_size,
            shuffle=False, num_workers=num_workers
        )
        loaders["test"] = test_loader

    return loaders


# =========================================================
# 5. TRAINING LOOP
# =========================================================

def train_jan(
    model,
    loaders,
    device,
    epochs=30,
    lambda_jmmd=0.3,
    lr=1e-4,
    save_dir="./checkpoints"
):

    os.makedirs(save_dir, exist_ok=True)

    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    jmmd = JointMMD().to(device)

    log_path = os.path.join(save_dir, "training_log.csv")
    with open(log_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["epoch", "cls_loss", "jmmd_loss", "total_loss"])

    model.to(device)

    for epoch in range(1, epochs + 1):
        model.train()

        total_cls, total_jmmd = 0.0, 0.0
        n_batches = min(len(loaders["source"]), len(loaders["target"]))

        src_iter = iter(loaders["source"])
        tgt_iter = iter(loaders["target"])

        for _ in range(n_batches):
            x_s, y_s = next(src_iter)
            x_t, _ = next(tgt_iter)

            x_s, y_s = x_s.to(device), y_s.to(device)
            x_t = x_t.to(device)

            x = torch.cat([x_s, x_t], dim=0)
            logits, feats = model(x)

            y_s_pred, y_t_pred = logits.chunk(2)
            f_s, f_t = feats.chunk(2)

            cls_loss = F.cross_entropy(y_s_pred, y_s)
            jmmd_loss = jmmd(
                (f_s, F.softmax(y_s_pred, dim=1)),
                (f_t, F.softmax(y_t_pred, dim=1))
            )

            loss = cls_loss + lambda_jmmd * jmmd_loss

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_cls += cls_loss.item()
            total_jmmd += jmmd_loss.item()

        avg_cls = total_cls / n_batches
        avg_jmmd = total_jmmd / n_batches

        print(
            f"Epoch [{epoch}/{epochs}] | "
            f"Cls: {avg_cls:.4f} | JMMD: {avg_jmmd:.4f}"
        )

        with open(log_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([epoch, avg_cls, avg_jmmd, avg_cls + lambda_jmmd * avg_jmmd])

        save_checkpoint(
            {"epoch": epoch, "model": model.state_dict()},
            os.path.join(save_dir, "last_model.pt")
        )


# =========================================================
# 6. EVALUATION (OPTIONAL, LABELED FITZ)
# =========================================================

@torch.no_grad()
def evaluate(model, loader, device):
    model.eval()
    y_true, y_pred = [], []

    for x, y in loader:
        x = x.to(device)
        logits, _ = model(x)
        preds = logits.argmax(1).cpu().numpy()

        y_true.extend(y.numpy())
        y_pred.extend(preds)

    acc = accuracy_score(y_true, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="macro"
    )
    cm = confusion_matrix(y_true, y_pred)

    return acc, precision, recall, f1, cm
