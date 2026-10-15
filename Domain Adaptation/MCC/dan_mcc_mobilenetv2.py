import os
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
from itertools import cycle

# =========================================================
# CONFIG
# =========================================================
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

NUM_CLASSES = 7
BATCH_SIZE = 16
EPOCHS = 30
LR = 1e-4

LAMBDA_MMD = 0.5
LAMBDA_MCC = 0.3
MCC_TEMPERATURE = 2.5

BOTTLENECK_DIM = 256

SAVE_DIR = "./checkpoints_dan_mcc"
os.makedirs(SAVE_DIR, exist_ok=True)

# =========================================================
# DATA TRANSFORMS
# =========================================================
def get_transforms(train=True):
    if train:
        return transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.RandomHorizontalFlip(),
            transforms.ColorJitter(0.1, 0.1, 0.1),
            transforms.ToTensor(),
            transforms.Normalize(
                [0.485, 0.456, 0.406],
                [0.229, 0.224, 0.225]
            )
        ])
    else:
        return transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                [0.485, 0.456, 0.406],
                [0.229, 0.224, 0.225]
            )
        ])

# =========================================================
# MODEL: DAN + MobileNetV2
# =========================================================
class DANMobileNet(nn.Module):
    def __init__(self, num_classes=7, bottleneck_dim=256):
        super().__init__()

        base = models.mobilenet_v2(weights="IMAGENET1K_V1")
        self.features = base.features
        self.pool = nn.AdaptiveAvgPool2d(1)

        self.bottleneck = nn.Sequential(
            nn.Linear(1280, bottleneck_dim),
            nn.BatchNorm1d(bottleneck_dim),
            nn.ReLU(inplace=True)
        )

        self.classifier = nn.Linear(bottleneck_dim, num_classes)

    def forward(self, x):
        x = self.features(x)
        x = self.pool(x).flatten(1)
        feat = self.bottleneck(x)
        logits = self.classifier(feat)
        return logits, feat

# =========================================================
# MK-MMD LOSS
# =========================================================
class GaussianKernel(nn.Module):
    def __init__(self, sigma):
        super().__init__()
        self.sigma = sigma

    def forward(self, x, y):
        dist = torch.cdist(x, y) ** 2
        return torch.exp(-dist / (2 * self.sigma ** 2))


def mk_mmd(source, target, sigmas=(2, 4, 8)):
    loss = 0.0
    for sigma in sigmas:
        kernel = GaussianKernel(sigma).to(source.device)
        K_ss = kernel(source, source).mean()
        K_tt = kernel(target, target).mean()
        K_st = kernel(source, target).mean()
        loss += K_ss + K_tt - 2 * K_st
    return loss

# =========================================================
# MCC LOSS
# =========================================================
class MinimumClassConfusionLoss(nn.Module):
    def __init__(self, temperature=2.5):
        super().__init__()
        self.temperature = temperature

    def forward(self, logits):
        """
        logits: [B, C] target predictions
        """

        B, C = logits.size()

        # 1. Probability Rescaling
        prob = F.softmax(
            logits / self.temperature,
            dim=1
        )

        # 2. Uncertainty Reweighting
        entropy = -torch.sum(
            prob * torch.log(prob + 1e-6),
            dim=1
        )

        weight = 1.0 + torch.exp(-entropy)

        weight = (
            weight / (weight.sum() + 1e-6)
        ) * B

        # 3. Weighted Class Correlation
        weighted_prob = prob * weight.unsqueeze(1)

        C_mat = prob.t() @ weighted_prob

        # 4. Category Normalization
        C_mat = C_mat / (
            C_mat.sum(dim=1, keepdim=True) + 1e-6
        )

        # 5. Minimum Class Confusion
        off_diagonal = (
            C_mat.sum()
            - torch.diagonal(C_mat).sum()
        )

        mcc_loss = off_diagonal / C

        return mcc_loss
    
# =========================================================
# CHECKPOINT UTILS
# =========================================================
def save_checkpoint(model, optimizer, epoch, acc, filename):
    torch.save({
        "epoch": epoch,
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "accuracy": acc,
        "num_classes": NUM_CLASSES,
        "bottleneck_dim": BOTTLENECK_DIM,
        "lambda_mmd": LAMBDA_MMD,
        "lambda_mcc": LAMBDA_MCC
    }, filename)

# =========================================================
# EVALUATION
# =========================================================
@torch.no_grad()
def evaluate(model, loader):
    model.eval()
    correct, total = 0, 0

    for x, y in loader:
        x, y = x.to(DEVICE), y.to(DEVICE)
        logits, _ = model(x)
        pred = logits.argmax(1)
        correct += (pred == y).sum().item()
        total += y.size(0)

    return correct / total if total > 0 else 0.0

# =========================================================
# TRAINING FUNCTION
# =========================================================
def train_dan(
    source_root,
    target_unlabeled_root,
    target_test_root=None
):
    # -------------------------------
    # DATASETS
    # -------------------------------
    source_ds = datasets.ImageFolder(
        source_root,
        transform=get_transforms(train=True)
    )

    target_unlabeled_ds = datasets.ImageFolder(
        target_unlabeled_root,
        transform=get_transforms(train=True)
    )

    source_loader = DataLoader(
        source_ds,
        batch_size=BATCH_SIZE,
        shuffle=True,
        drop_last=True,
        num_workers=2,
        pin_memory=True
    )

    target_loader = DataLoader(
        target_unlabeled_ds,
        batch_size=BATCH_SIZE,
        shuffle=True,
        drop_last=True,
        num_workers=2,
        pin_memory=True
    )

    if target_test_root:
        target_test_ds = datasets.ImageFolder(
            target_test_root,
            transform=get_transforms(train=False)
        )

        target_test_loader = DataLoader(
            target_test_ds,
            batch_size=BATCH_SIZE,
            shuffle=False
        )
    else:
        target_test_loader = None

    # -------------------------------
    # MODEL & OPTIM
    # -------------------------------
    model = DANMobileNet(NUM_CLASSES, BOTTLENECK_DIM).to(DEVICE)
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)

    mcc_loss_fn = MinimumClassConfusionLoss(
        temperature=MCC_TEMPERATURE
    ).to(DEVICE)

    best_acc = 0.0

    # -------------------------------
    # TRAIN LOOP
    # -------------------------------
    for epoch in range(EPOCHS):
        model.train()

        total_loss = 0.0
        total_cls = 0.0
        total_mmd = 0.0
        total_mcc = 0.0

        for i, ((xs, ys), (xt, _)) in enumerate(
            zip(source_loader, cycle(target_loader))
        ):
            xs, ys = xs.to(DEVICE), ys.to(DEVICE)
            xt = xt.to(DEVICE)

            optimizer.zero_grad()

            ys_pred, fs = model(xs)
            yt_pred, ft = model(xt)

            cls_loss = F.cross_entropy(ys_pred, ys)

            if i % 5 == 0:
                mmd_loss = mk_mmd(fs, ft)
            else:
                mmd_loss = torch.tensor(0.0, device=DEVICE)

            mcc_loss = mcc_loss_fn(yt_pred)

            loss = (
                cls_loss
                + LAMBDA_MMD * mmd_loss
                + LAMBDA_MCC * mcc_loss
            )

            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            total_cls += cls_loss.item()
            total_mmd += mmd_loss.item()
            total_mcc += mcc_loss.item()

            if i % 50 == 0:
                print(
                    f"Epoch {epoch+1}/{EPOCHS} | "
                    f"Step {i}/{len(source_loader)}"
                )

        print(
            f"Epoch [{epoch+1}/{EPOCHS}] | "
            f"Loss: {total_loss:.3f} | "
            f"CLS: {total_cls:.3f} | "
            f"MMD: {total_mmd:.3f} | "
            f"MCC: {total_mcc:.3f}"
        )

        # -------------------------------
        # EVALUATION
        # -------------------------------
        acc = 0.0
        if target_test_loader:
            acc = evaluate(model, target_test_loader)
            print(f"Target Accuracy: {acc:.4f}")

            if acc > best_acc:
                best_acc = acc
                save_checkpoint(
                    model,
                    optimizer,
                    epoch,
                    acc,
                    os.path.join(SAVE_DIR, "dan_mobilenet_mcc_best.pth")
                )

        save_checkpoint(
            model,
            optimizer,
            epoch,
            acc,
            os.path.join(SAVE_DIR, "dan_mobilenet_mcc_last.pth")
        )

    return model
