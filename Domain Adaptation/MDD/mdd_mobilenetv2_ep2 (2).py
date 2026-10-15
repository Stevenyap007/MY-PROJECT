import os
import argparse
import numpy as np
from collections import Counter

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from torchvision.datasets import ImageFolder
from torchvision.models import mobilenet_v2, MobileNet_V2_Weights

from PIL import Image
from sklearn.metrics import accuracy_score, f1_score
from tqdm import tqdm


# =========================================================
# 1. DATASET FOR UNLABELED TARGET 
# =========================================================
class UnlabeledFolderDataset(Dataset):
    def __init__(self, root, transform=None):
        self.transform = transform
        self.images = []

        for r, _, files in os.walk(root):
            for f in files:
                if f.lower().endswith((".jpg", ".png", ".jpeg")):
                    self.images.append(os.path.join(r, f))

        assert len(self.images) > 0, "Target merged folder is empty!"
        print(f"[INFO] Unlabeled target images: {len(self.images)}")

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        img = Image.open(self.images[idx]).convert("RGB")
        if self.transform:
            img = self.transform(img)
        return img


# =========================================================
# 2. MDD MODEL (MobileNetV2)
# =========================================================
class MDDMobileNet(nn.Module):
    def __init__(self, num_classes):
        super().__init__()
        base = mobilenet_v2(weights=MobileNet_V2_Weights.IMAGENET1K_V1)
        self.backbone = base.features
        self.pool = nn.AdaptiveAvgPool2d(1)

        self.classifier = nn.Linear(1280, num_classes)       # f
        self.classifier_adv = nn.Linear(1280, num_classes)   # f'

    def forward(self, x):
        feat = self.backbone(x)
        feat = self.pool(feat).flatten(1)
        y = self.classifier(feat)
        y_adv = self.classifier_adv(feat)
        return y, y_adv


# =========================================================
# 3. MDD MARGIN DISPARITY 
# =========================================================
class MarginDisparityDiscrepancy(nn.Module):
    def __init__(self, margin=2.0):
        super().__init__()
        self.margin = margin

    def forward(self, y, y_adv):
        y = F.log_softmax(y, dim=1)
        y_adv = F.log_softmax(y_adv, dim=1)
        return torch.mean(F.relu(self.margin - y + y_adv))


# =========================================================
# 4. EVALUATION
# =========================================================
@torch.no_grad()
def evaluate(model, loader, device):
    model.eval()
    all_preds, all_labels = [], []

    for x, y in loader:
        x = x.to(device)
        y = y.to(device)
        logits, _ = model(x)
        preds = logits.argmax(1)
        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(y.cpu().numpy())

    acc = accuracy_score(all_labels, all_preds)
    f1 = f1_score(all_labels, all_preds, average="macro")
    return acc, f1


# =========================================================
# 5. MAIN TRAINING LOOP 
# =========================================================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--src_root", type=str, required=True)
    parser.add_argument("--tgt_train_root", type=str, required=True)
    parser.add_argument("--tgt_eval_root", type=str, required=True)
    parser.add_argument("--save_dir", type=str, default="checkpoints")

    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-4)

    parser.add_argument("--trade_off", type=float, default=0.05)
    parser.add_argument("--margin", type=float, default=2.0)
    parser.add_argument("--warmup", type=int, default=5)

    args = parser.parse_args()

    os.makedirs(args.save_dir, exist_ok=True)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Transforms
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor()
    ])

    # Datasets
    src_dataset = ImageFolder(args.src_root, transform=transform)
    tgt_dataset = UnlabeledFolderDataset(args.tgt_train_root, transform=transform)
    tgt_eval_dataset = ImageFolder(args.tgt_eval_root, transform=transform)

    print("Source classes:", src_dataset.class_to_idx)
    print("Target classes:", tgt_eval_dataset.class_to_idx)

    src_loader = DataLoader(src_dataset, batch_size=args.batch_size,
                            shuffle=True, drop_last=True)
    tgt_loader = DataLoader(tgt_dataset, batch_size=args.batch_size,
                            shuffle=True, drop_last=True)
    tgt_eval_loader = DataLoader(tgt_eval_dataset, batch_size=args.batch_size,
                                 shuffle=False)

    model = MDDMobileNet(num_classes=len(src_dataset.classes)).to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)

    # Class-balanced CE 
    counts = Counter(src_dataset.targets)
    total = sum(counts.values())
    weights = torch.tensor(
        [total / counts[i] for i in range(len(counts))],
        dtype=torch.float
    ).to(device)

    ce_loss = nn.CrossEntropyLoss(weight=weights)
    mdd_loss_fn = MarginDisparityDiscrepancy(args.margin)

    best_f1 = 0.0

    # =====================================================
    # TRAIN
    # =====================================================
    for epoch in range(1, args.epochs + 1):
        model.train()
        total_loss = 0.0

        for (xs, ys), xt in zip(src_loader, tgt_loader):
            xs, ys = xs.to(device), ys.to(device)
            xt = xt.to(device)

            y_s, y_s_adv = model(xs)
            y_t, y_t_adv = model(xt)

            cls_loss = ce_loss(y_s, ys)

            if epoch <= args.warmup:
                loss = cls_loss
            else:
                # TRUE MDD: maximize discrepancy w.r.t f'
                src_disp = mdd_loss_fn(y_s, y_s_adv)
                tgt_disp = mdd_loss_fn(y_t, y_t_adv)
                transfer_loss = tgt_disp - src_disp
                loss = cls_loss + args.trade_off * transfer_loss

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        acc, f1 = evaluate(model, tgt_eval_loader, device)

        print(f"Epoch [{epoch}/{args.epochs}] "
              f"| Loss: {total_loss:.4f} "
              f"| Target Acc: {acc:.4f} "
              f"| F1: {f1:.4f}")

        if f1 > best_f1:
            best_f1 = f1
            torch.save(model.state_dict(),
                       os.path.join(args.save_dir, "mdd_best.pth"))

    print("Training complete")


if __name__ == "__main__":
    main()
