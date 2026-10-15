# dann_mobilenetv2.py
# DANN (MobileNetV2) for ImageFolder datasets (UDA: ISIC → Fitzpatrick)
# Author: Adapted from VGG16 version + save checkpoints

import os
import argparse
import random
import numpy as np
from tqdm import tqdm
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import transforms, datasets, models
from torch.utils.data import DataLoader, Dataset
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
import glob


# ----------------------------
# Dataset utilities
# ----------------------------
class UnlabeledImageFolder(Dataset):
    """For target domain without subfolders (unlabeled)."""
    def __init__(self, root, transform=None):
        self.root = root
        self.transform = transform
        self.samples = sorted(
            glob.glob(os.path.join(root, "*.jpg")) +
            glob.glob(os.path.join(root, "*.png")) +
            glob.glob(os.path.join(root, "*.jpeg"))
        )
        if len(self.samples) == 0:
            raise FileNotFoundError(f"No image files found in {root}")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path = self.samples[idx]
        img = Image.open(img_path).convert("RGB")
        if self.transform:
            img = self.transform(img)
        return img, -1


def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


# ----------------------------
# Encoder: MobileNetV2
# ----------------------------
def get_mobilenetv2_encoder(pretrained=True):
    mobilenet = models.mobilenet_v2(
        weights=models.MobileNet_V2_Weights.DEFAULT if pretrained else None
    )
    features = mobilenet.features
    pool = nn.AdaptiveAvgPool2d((1, 1))

    class Encoder(nn.Module):
        def __init__(self, features, pool):
            super().__init__()
            self.features = features
            self.pool = pool

        def forward(self, x):
            x = self.features(x)
            x = self.pool(x)
            x = torch.flatten(x, 1)
            return x

    encoder = Encoder(features, pool)
    return encoder, 1280  # MobileNetV2 feature dimension


# ----------------------------
# Classifier and Discriminator
# ----------------------------
class ClassifierHead(nn.Module):
    def __init__(self, feat_dim, num_classes):
        super().__init__()
        self.fc = nn.Linear(feat_dim, num_classes)

    def forward(self, x):
        return self.fc(x)


class DomainDiscriminator(nn.Module):
    def __init__(self, in_dim=1280, hidden=1024):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden),
            nn.ReLU(True),
            nn.Dropout(0.5),
            nn.Linear(hidden, hidden // 2),
            nn.ReLU(True),
            nn.Dropout(0.5),
            nn.Linear(hidden // 2, 1)
        )

    def forward(self, x):
        return self.net(x)


# Gradient Reversal Layer
class GradReverse(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x, lambd):
        ctx.lambd = lambd
        return x.view_as(x)

    @staticmethod
    def backward(ctx, grad_output):
        return grad_output.neg() * ctx.lambd, None


# ----------------------------
# DataLoader
# ----------------------------
def make_dataloaders(source_dir, target_dir, test_dir, batch_size=16, img_size=224, num_workers=4):
    tfm_train = transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    tfm_val = transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    src_ds = datasets.ImageFolder(source_dir, transform=tfm_train)
    if len(os.listdir(target_dir)) > 0 and os.path.isdir(os.path.join(target_dir, os.listdir(target_dir)[0])):
        tgt_ds = datasets.ImageFolder(target_dir, transform=tfm_train)
    else:
        tgt_ds = UnlabeledImageFolder(target_dir, transform=tfm_train)
    test_ds = datasets.ImageFolder(test_dir, transform=tfm_val)

    src_loader = DataLoader(src_ds, batch_size=batch_size, shuffle=True, num_workers=num_workers, drop_last=True)
    tgt_loader = DataLoader(tgt_ds, batch_size=batch_size, shuffle=True, num_workers=num_workers, drop_last=True)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False, num_workers=num_workers)
    return src_loader, tgt_loader, test_loader, src_ds.classes


# ----------------------------
# Training DANN
# ----------------------------
def train_dann(encoder, classifier, discriminator, src_loader, tgt_loader, device, epochs, lr, lambd, iters_per_epoch):
    encoder.to(device)
    classifier.to(device)
    discriminator.to(device)

    opt = optim.Adam(
        list(encoder.parameters()) + list(classifier.parameters()) + list(discriminator.parameters()), lr=lr
    )
    ce_loss = nn.CrossEntropyLoss()
    bce_loss = nn.BCEWithLogitsLoss()

    src_iter = iter(src_loader)
    tgt_iter = iter(tgt_loader)

    for epoch in range(epochs):
        encoder.train(); classifier.train(); discriminator.train()
        pbar = tqdm(range(iters_per_epoch), desc=f"DANN Train Ep {epoch+1}/{epochs}")

        for _ in pbar:
            try:
                xs, ys = next(src_iter)
            except StopIteration:
                src_iter = iter(src_loader)
                xs, ys = next(src_iter)
            try:
                xt, _ = next(tgt_iter)
            except StopIteration:
                tgt_iter = iter(tgt_loader)
                xt, _ = next(tgt_iter)

            xs, ys, xt = xs.to(device), ys.to(device), xt.to(device)
            x = torch.cat([xs, xt], dim=0)
            domain_labels = torch.cat([
                torch.ones(xs.size(0), 1),
                torch.zeros(xt.size(0), 1)
            ], dim=0).to(device)

            # Forward
            features = encoder(x)
            preds_cls = classifier(features[:xs.size(0)])
            loss_cls = ce_loss(preds_cls, ys)

            # Domain prediction with gradient reversal
            rev_features = GradReverse.apply(features, lambd)
            preds_domain = discriminator(rev_features)
            loss_domain = bce_loss(preds_domain, domain_labels)

            loss = loss_cls + loss_domain

            opt.zero_grad()
            loss.backward()
            opt.step()

            pbar.set_postfix(loss=loss.item(), cls=loss_cls.item(), dom=loss_domain.item())

    print("DANN Training Completed.")


# ----------------------------
# Evaluation
# ----------------------------
def evaluate_model(encoder, classifier, test_loader, device, classes, save_csv=None, cm_path=None):
    import pandas as pd

    encoder.eval(); classifier.eval()
    preds_all, labels_all = [], []

    with torch.no_grad():
        for x, y in tqdm(test_loader, desc="Evaluating"):
            x = x.to(device)
            y_hat = classifier(encoder(x))
            preds = y_hat.argmax(1).cpu().numpy()
            preds_all.extend(preds)
            labels_all.extend(y.numpy())

    report = classification_report(labels_all, preds_all, target_names=classes, output_dict=True)
    df = pd.DataFrame(report).transpose()
    if save_csv:
        os.makedirs(os.path.dirname(save_csv), exist_ok=True)
        df.to_csv(save_csv)
        print("Saved classification report:", save_csv)

    cm = confusion_matrix(labels_all, preds_all)
    if cm_path:
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=classes, yticklabels=classes)
        plt.xlabel('Predicted')
        plt.ylabel('True')
        plt.title('Confusion Matrix')
        plt.tight_layout()
        plt.savefig(cm_path)
        plt.close()
        print("Saved confusion matrix:", cm_path)

    return df, cm


# ----------------------------
# CLI
# ----------------------------
def main():
    p = argparse.ArgumentParser(description="DANN (MobileNetV2) for UDA")
    p.add_argument('--source-dir', required=True)
    p.add_argument('--target-dir', required=True)
    p.add_argument('--test-dir', required=True)
    p.add_argument('--out-dir', default='outputs/dann_mobilenetv2')
    p.add_argument('--img-size', type=int, default=224)
    p.add_argument('--batch-size', type=int, default=16)
    p.add_argument('--epochs', type=int, default=20)
    p.add_argument('--iters-per-epoch', type=int, default=500)
    p.add_argument('--lr', type=float, default=1e-4)
    p.add_argument('--lambda-val', type=float, default=1.0)
    p.add_argument('--num-workers', type=int, default=4)
    p.add_argument('--seed', type=int, default=42)
    p.add_argument('--device', default='cuda')
    args = p.parse_args()

    set_seed(args.seed)
    os.makedirs(args.out_dir, exist_ok=True)
    device = torch.device(args.device if torch.cuda.is_available() else 'cpu')

    print("Loading datasets...")
    src_loader, tgt_loader, test_loader, classes = make_dataloaders(
        args.source_dir, args.target_dir, args.test_dir,
        batch_size=args.batch_size, img_size=args.img_size, num_workers=args.num_workers
    )

    print("Building model...")
    encoder, feat_dim = get_mobilenetv2_encoder(pretrained=True)
    classifier = ClassifierHead(feat_dim, len(classes))
    discriminator = DomainDiscriminator(in_dim=feat_dim)

    print("Training DANN...")
    train_dann(encoder, classifier, discriminator,
               src_loader, tgt_loader, device,
               args.epochs, args.lr, args.lambda_val, args.iters_per_epoch)

    print("Saving models...")
    torch.save(encoder.state_dict(), os.path.join(args.out_dir, "encoder.pth"))
    torch.save(classifier.state_dict(), os.path.join(args.out_dir, "classifier.pth"))
    torch.save({
        "encoder": encoder.state_dict(),
        "classifier": classifier.state_dict()
    }, os.path.join(args.out_dir, "full_model.pth"))
    print(" Saved encoder.pth, classifier.pth, and full_model.pth")

    print(" Evaluating on test set...")
    eval_csv = os.path.join(args.out_dir, 'classification_report.csv')
    cm_path = os.path.join(args.out_dir, 'confusion_matrix.png')
    df, cm = evaluate_model(encoder, classifier, test_loader, device, classes, save_csv=eval_csv, cm_path=cm_path)
    print(df)


if __name__ == "__main__":
    main()
