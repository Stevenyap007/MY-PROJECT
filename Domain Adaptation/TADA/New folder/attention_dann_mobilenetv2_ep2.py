# dann_mobilenetv2_tada.py
# DANN (MobileNetV2) for ImageFolder datasets (UDA: ISIC → Fitzpatrick)
# Added TADA-style local + global transferable attention modules
# Author: adapted from user's original dann_mobilenetv2.py + TADA (Wang et al. AAAI 2019) modules

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
# Encoder: MobileNetV2 (returns feature map + pooled vector)
# ----------------------------
def get_mobilenetv2_encoder(pretrained=True):
    mobilenet = models.mobilenet_v2(
        weights=models.MobileNet_V2_Weights.DEFAULT if pretrained else None
    )
    features = mobilenet.features  # this outputs a feature map, e.g. (B, 1280, H, W)
    pool = nn.AdaptiveAvgPool2d((1, 1))

    class Encoder(nn.Module):
        def __init__(self, features, pool):
            super().__init__()
            self.features = features
            self.pool = pool

        def forward(self, x):
            fmap = self.features(x)          # (B, C, H, W)
            pooled = self.pool(fmap)         # (B, C, 1, 1)
            pooled = torch.flatten(pooled, 1) # (B, C)
            return fmap, pooled

    encoder = Encoder(features, pool)
    return encoder, 1280  # MobileNetV2 feature dimension


# ----------------------------
# Classifier and Discriminator (global)
# ----------------------------
class ClassifierHead(nn.Module):
    def __init__(self, feat_dim, num_classes):
        super().__init__()
        self.fc = nn.Linear(feat_dim, num_classes)

    def forward(self, x):
        return self.fc(x)


class GlobalDomainDiscriminator(nn.Module):
    def __init__(self, in_dim=1280, hidden=1024):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden),
            nn.ReLU(True),
            nn.Dropout(0.5),
            nn.Linear(hidden, max(hidden // 2, 64)),
            nn.ReLU(True),
            nn.Dropout(0.5),
            nn.Linear(max(hidden // 2, 64), 1)
        )

    def forward(self, x):
        # x: (B, C)
        return self.net(x)


# ----------------------------
# Local (region-level) domain discriminator
# Applies MLP to each channel vector at each spatial location
# ----------------------------
class LocalDomainDiscriminator(nn.Module):
    def __init__(self, in_channels, hidden=512):
        super().__init__()
        # MLP that will be applied to region vectors of size in_channels
        # We implement as 1x1 conv to share parameters across spatial locations more efficiently
        # But keep a small MLP-like stack via conv1x1 + nonlinearity.
        self.net = nn.Sequential(
            nn.Conv2d(in_channels, hidden, kernel_size=1),
            nn.ReLU(True),
            nn.Dropout2d(0.3),
            nn.Conv2d(hidden, max(hidden // 2, 32), kernel_size=1),
            nn.ReLU(True),
            nn.Dropout2d(0.3),
            nn.Conv2d(max(hidden // 2, 32), 1, kernel_size=1)  # outputs (B,1,H,W) logits per region
        )

    def forward(self, fmap):
        # fmap: (B, C, H, W) -> returns logits per region (B, 1, H, W)
        return self.net(fmap)


# ----------------------------
# Gradient Reversal Layer
# ----------------------------
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
    # target may be unlabeled folder (flat) or an ImageFolder with class-subfolders
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
# Utilities: binary entropy normalized (base 2) for probabilities in (0,1)
# ----------------------------
def binary_entropy(p, eps=1e-8):
    # p: tensor of probabilities in (0,1)
    p = p.clamp(eps, 1 - eps)
    h = - (p * torch.log2(p) + (1 - p) * torch.log2(1 - p))  # bits, range [0,1]
    return h  # same shape as p


# ----------------------------
# Training DANN with optional TADA modules
# ----------------------------
entropy_start = 8 
def train_dann(encoder, classifier, global_disc, local_disc, src_loader, tgt_loader,
               device, epochs, lr, lambd, iters_per_epoch, gamma=0.1, use_tada=True):
    # place modules
    encoder.to(device)
    classifier.to(device)
    if global_disc is not None:
        global_disc.to(device)
    if local_disc is not None:
        local_disc.to(device)

    # gather parameters
    params = list(encoder.parameters()) + list(classifier.parameters())
    if global_disc is not None:
        params += list(global_disc.parameters())
    if local_disc is not None:
        params += list(local_disc.parameters())

    opt = optim.Adam(params, lr=lr)
    ce_loss = nn.CrossEntropyLoss()
    bce_loss = nn.BCEWithLogitsLoss()

    src_iter = iter(src_loader)
    tgt_iter = iter(tgt_loader)

    for epoch in range(epochs):
        encoder.train(); classifier.train()
        if global_disc is not None: global_disc.train()
        if local_disc is not None: local_disc.train()

        pbar = tqdm(range(iters_per_epoch), desc=f"DANN+TADA Train Ep {epoch+1}/{epochs}")

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
            n_src = xs.size(0)
            n_tgt = xt.size(0)
            domain_labels = torch.cat([
                torch.ones(n_src, 1),
                torch.zeros(n_tgt, 1)
            ], dim=0).to(device)

            # Forward encoder -> get spatial fmap and pooled vector
            fmap, pooled = encoder(x)  # fmap: (B, C, H, W) ; pooled: (B, C)

            # Classification (only on source samples)
            preds_src = classifier(pooled[:n_src])
            loss_cls = ce_loss(preds_src, ys)

            # ---------- Local domain discriminators (region-level) ----------
            loss_local = torch.tensor(0.0, device=device)
            # if use_tada and local_disc is not None:
            #     # Local domain logits per region (B,1,H,W)
            #     # Apply GRL before local discriminator for encoder adversarial training
            #     rev_fmap = GradReverse.apply(fmap, lambd)
            #     local_logits = local_disc(rev_fmap)  # (B,1,H,W)
            #     # Resize domain labels to (B,1,H,W)
            #     # domain_labels is (B,1) -> expand to H,W
            #     _, _, H, W = local_logits.shape
            #     domain_map = domain_labels.view(-1, 1, 1, 1).expand(-1, 1, H, W)  # (B,1,H,W)
            #     loss_local = bce_loss(local_logits, domain_map)

            #     # compute local attention weights w_k = 1 - H(d_hat_k)
            #     # where d_hat are probabilities (sigmoid of logits), compute entropy per region
            #     with torch.no_grad():
            #         local_probs = torch.sigmoid(local_logits)  # (B,1,H,W)
            #         local_entropy = binary_entropy(local_probs)  # (B,1,H,W) in bits 0..1
            #         # w = 1 - H
            #         local_w = 1.0 - local_entropy  # (B,1,H,W)
            #         # expand weight to channels to rescale fmap per spatial location
            #         local_w_chan = local_w.expand(-1, fmap.size(1), -1, -1)  # (B,C,H,W)

            #     # residual reweighting: h_k = (1 + w_k) * f_k
            #     fmap = (1.0 + local_w_chan) * fmap  # reweighted feature map

            #     # update pooled representation after reweight
            #     pooled = torch.flatten(nn.functional.adaptive_avg_pool2d(fmap, (1, 1)), 1)  # (B, C)

            # ---------- Global domain discriminator ----------
            loss_global = torch.tensor(0.0, device=device)
            global_probs = None
            if global_disc is not None:
                rev_pooled = GradReverse.apply(pooled, lambd)
                global_logits = global_disc(rev_pooled).view(-1, 1)  # (B,1)
                loss_global = bce_loss(global_logits, domain_labels)

                with torch.no_grad():
                    global_probs = torch.sigmoid(global_logits)  # (B,1)

            # ---------- Attentive entropy (global) ----------
            loss_attentive_entropy = torch.tensor(0.0, device=device)
            if use_tada and global_probs is not None and epoch >= entropy_start:
                # compute classifier predictions for all samples (source+target)
                preds_all_logits = classifier(pooled)  # (B, num_classes)
                preds_all_probs = nn.functional.softmax(preds_all_logits, dim=1)  # (B, C)
                # per-sample entropy over classes
                eps = 1e-8
                per_sample_entropy = -torch.sum(preds_all_probs * torch.log(preds_all_probs + eps), dim=1, keepdim=True)  # (B,1)
                # compute global attention mi = 1 + H(d_hat_i) as in paper (H of domain prob)
                # note: H is binary entropy of domain prob (in bits 0..1)
                with torch.no_grad():
                    global_entropy = binary_entropy(global_probs)  # (B,1)
                    mi = 1.0 + global_entropy  # (B,1)
                # attentive entropy loss: average mi * entropy
                loss_attentive_entropy = torch.mean(mi * per_sample_entropy)

            # Final loss: classification + attentive entropy + domain losses
            # (domain losses are included with GRL effect)
            loss = loss = loss_cls + loss_global + gamma * loss_attentive_entropy

            opt.zero_grad()
            loss.backward()
            opt.step()

            pbar.set_postfix(loss=loss.item(), cls=loss_cls.item(),
                             dom_global=loss_global.item() if isinstance(loss_global, torch.Tensor) else float(loss_global),
                             dom_local=loss_local.item() if isinstance(loss_local, torch.Tensor) else float(loss_local),
                             ent=loss_attentive_entropy.item() if isinstance(loss_attentive_entropy, torch.Tensor) else 0.0)

    print("DANN+TADA Training Completed.")


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
            _, pooled = encoder(x)
            y_hat = classifier(pooled)
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
    p = argparse.ArgumentParser(description="DANN (MobileNetV2) with TADA-style attention for UDA")
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
    p.add_argument('--gamma', type=float, default=0.02, help="attentive entropy weight (TADA)")
    p.add_argument('--use-tada', action='store_true', help="enable TADA local+global attention modules")
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
    # create discriminators: global always created (you can pass None if you want to disable)
    global_disc = GlobalDomainDiscriminator(in_dim=feat_dim, hidden=1024)
    local_disc = None
    # if args.use_tada:
    #     local_disc = LocalDomainDiscriminator(in_channels=feat_dim, hidden=512)

    print("Training DANN (+ TADA=%s)..." % args.use_tada)
    train_dann(encoder, classifier, global_disc, local_disc,
               src_loader, tgt_loader, device,
               args.epochs, args.lr, args.lambda_val, args.iters_per_epoch,
               gamma=args.gamma, use_tada=args.use_tada)

    print("Saving models...")
    torch.save(encoder.state_dict(), os.path.join(args.out_dir, "encoder.pth"))
    torch.save(classifier.state_dict(), os.path.join(args.out_dir, "classifier.pth"))
    torch.save({
        "encoder": encoder.state_dict(),
        "classifier": classifier.state_dict()
    }, os.path.join(args.out_dir, "full_model.pth"))
    if global_disc is not None:
        torch.save(global_disc.state_dict(), os.path.join(args.out_dir, "global_discriminator.pth"))
    if local_disc is not None:
        torch.save(local_disc.state_dict(), os.path.join(args.out_dir, "local_discriminator.pth"))
    print(" Saved encoder.pth, classifier.pth, full_model.pth and discriminator checkpoints (if present)")

    print(" Evaluating on test set...")
    eval_csv = os.path.join(args.out_dir, 'classification_report.csv')
    cm_path = os.path.join(args.out_dir, 'confusion_matrix.png')
    df, cm = evaluate_model(encoder, classifier, test_loader, device, classes, save_csv=eval_csv, cm_path=cm_path)
    print(df)


if __name__ == "__main__":
    main()
