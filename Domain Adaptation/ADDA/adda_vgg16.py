# adda_vgg16.py
# Self-contained ADDA (VGG16-BN) for ImageFolder datasets
# Usage example (CLI args at bottom)

import os
import argparse
import random
import shutil
from pathlib import Path
from tqdm import tqdm

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import transforms, datasets, models
from torch.utils.data import DataLoader

from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


from torch.utils.data import Dataset
from PIL import Image
import glob

# --- custom unlabeled dataset ---
class UnlabeledImageFolder(Dataset):
    def __init__(self, root, transform=None):
        self.root = root
        self.transform = transform
        # gather all jpg/png/jpeg files
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
        if self.transform: img = self.transform(img)
        return img, -1  # dummy label
    
# ----------------------------
# Utilities
# ----------------------------
def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

# Small focal loss (optional)
class FocalLoss(nn.Module):
    def __init__(self, gamma=2.0, alpha=0.25, reduction='mean', from_logits=True):
        super().__init__()
        self.gamma = gamma
        self.alpha = alpha
        self.reduction = reduction
        self.from_logits = from_logits

    def forward(self, inputs, targets):
        # inputs: raw logits [B, C]; targets: long labels [B]
        if self.from_logits:
            prob = torch.softmax(inputs, dim=1)
        else:
            prob = inputs.clamp(1e-8, 1-1e-8)
        B = inputs.size(0)
        targets_onehot = torch.zeros_like(inputs).scatter(1, targets.view(-1,1), 1.0).to(inputs.device)
        pt = (prob * targets_onehot).sum(dim=1)  # p_t
        w = self.alpha * (1-pt)**self.gamma
        ce = - (targets_onehot * torch.log(prob + 1e-12)).sum(dim=1)
        loss = w * ce
        if self.reduction == 'mean':
            return loss.mean()
        elif self.reduction == 'sum':
            return loss.sum()
        else:
            return loss

# ----------------------------
# Model components
# ----------------------------
def get_vgg16_encoder(pretrained=True, pool_output_size=1):
    vgg = models.vgg16_bn(pretrained=pretrained)
    features = vgg.features  # Sequential
    # We'll convert features -> AdaptiveAvgPool2d((1,1)) -> flatten to get 512-d vector
    pool = nn.AdaptiveAvgPool2d((pool_output_size, pool_output_size))
    def forward_features(x):
        x = features(x)
        x = pool(x)
        x = torch.flatten(x, 1)
        return x
    # We create a small module wrapper
    class Encoder(nn.Module):
        def __init__(self, feats, pool):
            super().__init__()
            self.feats = feats
            self.pool = pool
        def forward(self, x):
            x = self.feats(x)
            x = self.pool(x)
            x = torch.flatten(x, 1)
            return x
    encoder = Encoder(features, pool)
    return encoder, 512  # features dim

class ClassifierHead(nn.Module):
    def __init__(self, feat_dim, num_classes):
        super().__init__()
        self.fc = nn.Linear(feat_dim, num_classes)
    def forward(self, x):
        return self.fc(x)

class Discriminator(nn.Module):
    def __init__(self, in_dim=512, hidden=1024):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(hidden, hidden//2),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(hidden//2, 1)
        )
    def forward(self, x):
        return self.net(x).view(-1,1)

# ----------------------------
# Data loaders
# ----------------------------
def make_dataloaders(source_dir, target_dir, test_dir, batch_size=16, img_size=224, num_workers=4):
    # transforms
    train_tfm = transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225]),
    ])
    val_tfm = transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225]),
    ])

    src_ds = datasets.ImageFolder(source_dir, transform=train_tfm)
    if len(os.listdir(target_dir)) > 0 and os.path.isdir(os.path.join(target_dir, os.listdir(target_dir)[0])):
        # labeled target (has subfolders)
        tgt_ds = datasets.ImageFolder(target_dir, transform=train_tfm)
    else:
        # unlabeled flat folder
        tgt_ds = UnlabeledImageFolder(target_dir, transform=train_tfm)
    test_ds = datasets.ImageFolder(test_dir, transform=val_tfm)

    src_loader = DataLoader(src_ds, batch_size=batch_size, shuffle=True, num_workers=num_workers, drop_last=True)
    tgt_loader = DataLoader(tgt_ds, batch_size=batch_size, shuffle=True, num_workers=num_workers, drop_last=True)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False, num_workers=num_workers)
    return src_loader, tgt_loader, test_loader, src_ds.classes

# ----------------------------
# Training / Adaptation / Evaluation
# ----------------------------
def pretrain_source(encoder, classifier, src_loader, device, epochs, lr, weight_decay, save_path, use_focal=False):
    encoder.to(device); classifier.to(device)
    params = list(encoder.parameters()) + list(classifier.parameters())
    opt = optim.Adam(params, lr=lr, weight_decay=weight_decay)
    if use_focal:
        criterion = FocalLoss(gamma=2.0, alpha=0.25, from_logits=True)
    else:
        criterion = nn.CrossEntropyLoss()
    for ep in range(epochs):
        encoder.train(); classifier.train()
        pbar = tqdm(src_loader, desc=f"Pretrain Ep {ep+1}/{epochs}")
        running_loss = 0.0
        correct = total = 0
        for imgs, labels in pbar:
            imgs = imgs.to(device); labels = labels.to(device)
            feats = encoder(imgs)  # [B, feat_dim]
            logits = classifier(feats)
            loss = criterion(logits, labels)
            opt.zero_grad(); loss.backward(); opt.step()
            running_loss += loss.item()*imgs.size(0)
            preds = logits.argmax(dim=1)
            correct += (preds==labels).sum().item()
            total += labels.size(0)
            pbar.set_postfix(loss=loss.item(), acc=correct/total)
        print(f"Pretrain epoch {ep+1} loss={running_loss/total:.4f} acc={correct/total:.4f}")
        torch.save({'encoder':encoder.state_dict(), 'classifier':classifier.state_dict()}, save_path)

def adapt_target_ADDA(encoder_s, classifier_s, encoder_t, discriminator, src_loader, tgt_loader, device,
                      epochs, lr_d, lr_g, weight_decay, iters_per_epoch=None, save_path=None):
    encoder_s.to(device); classifier_s.to(device)
    encoder_t.to(device); discriminator.to(device)
    # freeze source encoder & classifier
    encoder_s.eval()
    for p in encoder_s.parameters(): p.requires_grad = False
    classifier_s.eval()
    for p in classifier_s.parameters(): p.requires_grad = False

    opt_d = optim.Adam(discriminator.parameters(), lr=lr_d, weight_decay=weight_decay)
    opt_g = optim.Adam(encoder_t.parameters(), lr=lr_g, weight_decay=weight_decay)

    bce = nn.BCEWithLogitsLoss()
    src_iter = iter(src_loader)
    tgt_iter = iter(tgt_loader)

    if iters_per_epoch is None:
        iters = min(len(src_loader), len(tgt_loader))
    else:
        iters = iters_per_epoch

    best = {'acc':0.0}
    for ep in range(epochs):
        discriminator.train(); encoder_t.train()
        pbar = tqdm(range(iters), desc=f"Adapt Ep {ep+1}/{epochs}")
        for i in pbar:
            try:
                xs, _ = next(src_iter)
            except StopIteration:
                src_iter = iter(src_loader); xs, _ = next(src_iter)
            try:
                xt, _ = next(tgt_iter)
            except StopIteration:
                tgt_iter = iter(tgt_loader); xt, _ = next(tgt_iter)

            xs = xs.to(device); xt = xt.to(device)
            # --- train D ---
            with torch.no_grad():
                feat_s = encoder_s(xs)   # [B, D]
            feat_t_det = encoder_t(xt).detach()
            pred_s = discriminator(feat_s)
            pred_t = discriminator(feat_t_det)
            label_s = torch.ones(pred_s.size(), device=device)
            label_t = torch.zeros(pred_t.size(), device=device)
            loss_d = bce(pred_s, label_s) + bce(pred_t, label_t)
            opt_d.zero_grad(); loss_d.backward(); opt_d.step()

            # --- train G (target encoder) to fool D ---
            feat_t = encoder_t(xt)
            pred_t2 = discriminator(feat_t)
            # want D(pred_t2) -> 1 (source), so label=1
            loss_g = bce(pred_t2, torch.ones_like(pred_t2, device=device))
            opt_g.zero_grad(); loss_g.backward(); opt_g.step()

            pbar.set_postfix(loss_d=loss_d.item(), loss_g=loss_g.item())

        # Optionally evaluate after each epoch if you have labeled target test
        if save_path is not None:
            torch.save({'encoder_t':encoder_t.state_dict(), 'discriminator':discriminator.state_dict()}, save_path)

def evaluate_model(encoder, classifier, test_loader, device, classes, save_csv=None, cm_path=None):
    encoder.eval(); classifier.eval()
    all_preds = []; all_probs = []; all_labels = []
    with torch.no_grad():
        for x, y in tqdm(test_loader, desc="Evaluating"):
            x = x.to(device)
            feats = encoder(x)
            logits = classifier(feats)
            probs = torch.softmax(logits, dim=1).cpu().numpy()
            preds = logits.argmax(dim=1).cpu().numpy()
            all_probs.append(probs)
            all_preds.extend(preds.tolist())
            all_labels.extend(y.numpy().tolist())
    all_probs = np.vstack(all_probs)
    # classification report
    report = classification_report(all_labels, all_preds, target_names=classes, output_dict=True)
    df = pd.DataFrame(report).transpose()
    if save_csv:
        df.to_csv(save_csv, index=True)
        print("Saved classification report to", save_csv)
    # confusion matrix
    cm = confusion_matrix(all_labels, all_preds)
    if cm_path:
        plt.figure(figsize=(8,6))
        sns.heatmap(cm, annot=True, fmt='d', xticklabels=classes, yticklabels=classes, cmap='Blues')
        plt.xlabel('Predicted'); plt.ylabel('True'); plt.title('Confusion Matrix')
        plt.tight_layout()
        plt.savefig(cm_path)
        plt.close()
        print("Saved confusion matrix to", cm_path)
    return df, cm

# ----------------------------
# CLI
# ----------------------------
def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source-dir', required=True, help='ImageFolder source root (class subfolders)')
    p.add_argument('--target-dir', required=True, help='ImageFolder target root (can be unlabeled, e.g., one folder)')
    p.add_argument('--test-dir', required=True, help='Labeled target test folder (ImageFolder)')
    p.add_argument('--out-dir', default='outputs/adda', help='output folder')
    p.add_argument('--img-size', type=int, default=224)
    p.add_argument('--batch-size', type=int, default=16)
    p.add_argument('--pretrain-epochs', type=int, default=15)
    p.add_argument('--adapt-epochs', type=int, default=30)
    p.add_argument('--lr-src', type=float, default=1e-4)
    p.add_argument('--lr-d', type=float, default=1e-4)
    p.add_argument('--lr-g', type=float, default=1e-4)
    p.add_argument('--weight-decay', type=float, default=5e-4)
    p.add_argument('--num-workers', type=int, default=4)
    p.add_argument('--seed', type=int, default=42)
    p.add_argument('--use-focal', action='store_true', help='Use focal loss for pretrain')
    p.add_argument('--device', default='cuda', help='cuda or cpu')
    args = p.parse_args()

    set_seed(args.seed)
    os.makedirs(args.out_dir, exist_ok=True)
    device = torch.device(args.device if torch.cuda.is_available() and args.device.startswith('cuda') else 'cpu')

    src_loader, tgt_loader, test_loader, classes = make_dataloaders(
        args.source_dir, args.target_dir, args.test_dir,
        batch_size=args.batch_size, img_size=args.img_size, num_workers=args.num_workers)

    # build models
    encoder_s, feat_dim = get_vgg16_encoder(pretrained=True)
    classifier_s = ClassifierHead(feat_dim, len(classes))
    encoder_t, _ = get_vgg16_encoder(pretrained=True)
    encoder_t.load_state_dict(encoder_s.state_dict())  # init target with source weights
    discriminator = Discriminator(in_dim=feat_dim, hidden=1024)

    # Pretrain
    pretrain_ckpt = os.path.join(args.out_dir, 'source_pretrain.pth')
    print(">>> Pretraining source encoder + classifier")
    pretrain_source(encoder_s, classifier_s, src_loader, device, args.pretrain_epochs,
                    args.lr_src, args.weight_decay, pretrain_ckpt, use_focal=args.use_focal)

    # load pretrain to set in memory (and also copy to target)
    ck = torch.load(pretrain_ckpt, map_location='cpu')
    encoder_s.load_state_dict(ck['encoder'])
    classifier_s.load_state_dict(ck['classifier'])
    encoder_t.load_state_dict(ck['encoder'])  # ensure target starts from same weights

    # Adaptation
    print(">>> Adapting target encoder via ADDA")
    adapt_ckpt = os.path.join(args.out_dir, 'adapted.pth')
    adapt_target_ADDA(encoder_s, classifier_s, encoder_t, discriminator, src_loader, tgt_loader, device,
                      args.adapt_epochs, args.lr_d, args.lr_g, args.weight_decay, save_path=adapt_ckpt)

    # Evaluation on labeled target test set (use target encoder + source classifier)
    print(">>> Evaluating adapted model on labeled target test")
    eval_csv = os.path.join(args.out_dir, 'classification_report.csv')
    cm_path = os.path.join(args.out_dir, 'confusion_matrix.png')
    df, cm = evaluate_model(encoder_t, classifier_s, test_loader, device, classes, save_csv=eval_csv, cm_path=cm_path)
    print(df)

if __name__ == '__main__':
    main()
