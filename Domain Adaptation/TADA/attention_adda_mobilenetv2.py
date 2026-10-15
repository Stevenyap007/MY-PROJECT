# adda_mobilenetV2_tada.py
# ADDA with Transferable Attention (TADA) style local + global attention
# Based on your original adda_mobilenetV2.py (modified)

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
import math

# ----------------------------
# Unlabeled dataset (same as yours)
# ----------------------------
class UnlabeledImageFolder(Dataset):
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
        if self.transform: img = self.transform(img)
        return img, -1

# ----------------------------
# Utils
# ----------------------------
def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

# small focal loss (optional)
class FocalLoss(nn.Module):
    def __init__(self, gamma=2.0, alpha=0.25, reduction='mean', from_logits=True):
        super().__init__()
        self.gamma = gamma
        self.alpha = alpha
        self.reduction = reduction
        self.from_logits = from_logits
    def forward(self, inputs, targets):
        if self.from_logits:
            prob = torch.softmax(inputs, dim=1)
        else:
            prob = inputs.clamp(1e-8, 1-1e-8)
        B = inputs.size(0)
        targets_onehot = torch.zeros_like(inputs).scatter(1, targets.view(-1,1), 1.0).to(inputs.device)
        pt = (prob * targets_onehot).sum(dim=1)
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
# Encoder (returns conv feature map + pooled vector)
# ----------------------------
def get_mobilenetv2_encoder(pretrained=True):
    mobilenet = models.mobilenet_v2(pretrained=pretrained)
    features = mobilenet.features  # conv body
    feat_dim = mobilenet.last_channel  # 1280 for MobileNetV2

    class Encoder(nn.Module):
        def __init__(self, feats):
            super().__init__()
            self.feats = feats
            # NOTE: we keep adaptive pool but also preserve conv feature map
            self.pool = nn.AdaptiveAvgPool2d((1, 1))
        def forward(self, x, return_map=False):
            """
            returns:
              if return_map=False -> pooled flat feature [B, C]
              if return_map=True  -> (feat_map [B,C,H,W], pooled_flat [B,C])
            """
            fmap = self.feats(x)  # [B, C, H, W]
            pooled = self.pool(fmap)
            pooled = torch.flatten(pooled, 1)
            if return_map:
                return fmap, pooled
            else:
                return pooled

    encoder = Encoder(features)
    return encoder, feat_dim

# ----------------------------
# Classifier head
# ----------------------------
class ClassifierHead(nn.Module):
    def __init__(self, feat_dim, num_classes):
        super().__init__()
        self.fc = nn.Linear(feat_dim, num_classes)
    def forward(self, x):
        return self.fc(x)

# ----------------------------
# Global Discriminator (same idea as before)
# ----------------------------
class GlobalDiscriminator(nn.Module):
    def __init__(self, in_dim=1280, hidden=1024):
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
# Local Discriminator (convolutional head that returns per-spatial logits)
# We'll produce a single conv head that maps C->1 and keeps spatial shape.
# ----------------------------
class LocalDiscriminator(nn.Module):
    def __init__(self, in_channels, hidden_channels=512):
        super().__init__()
        # Simple conv head
        self.net = nn.Sequential(
            nn.Conv2d(in_channels, hidden_channels, kernel_size=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(hidden_channels, hidden_channels//2, kernel_size=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(hidden_channels//2, 1, kernel_size=1)  # logits per spatial cell
        )
    def forward(self, fmap):
        # fmap: B x C x H x W -> out: B x 1 x H x W (logits)
        return self.net(fmap)  # logits, not activated

# ----------------------------
# Dataloaders (kept from your file)
# ----------------------------
def make_dataloaders(source_dir, target_dir, test_dir, batch_size=16, img_size=224, num_workers=4):
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
        tgt_ds = datasets.ImageFolder(target_dir, transform=train_tfm)
    else:
        tgt_ds = UnlabeledImageFolder(target_dir, transform=train_tfm)
    test_ds = datasets.ImageFolder(test_dir, transform=val_tfm)

    src_loader = DataLoader(src_ds, batch_size=batch_size, shuffle=True, num_workers=num_workers, drop_last=True)
    tgt_loader = DataLoader(tgt_ds, batch_size=batch_size, shuffle=True, num_workers=num_workers, drop_last=True)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False, num_workers=num_workers)
    return src_loader, tgt_loader, test_loader, src_ds.classes

# ----------------------------
# Helper: binary entropy for probabilities
# ----------------------------
def binary_entropy_from_logits(logits, dim=None, eps=1e-8):
    # logits -> prob via sigmoid
    p = torch.sigmoid(logits)
    p = p.clamp(eps, 1-eps)
    h = - (p * torch.log(p) + (1-p) * torch.log(1-p))
    if dim is not None:
        return h.sum(dim=dim)
    return h

# ----------------------------
# Training: pretrain source (unchanged except encoder forward signature)
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
            _, feats = encoder(imgs, return_map=True)  # pooled feature
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

# ----------------------------
# Adaptation: ADDA with local+global attention
# ----------------------------
def adapt_target_ADDA_TADA(encoder_s, classifier_s, encoder_t,
                           globalD, localD,
                           src_loader, tgt_loader, device,
                           epochs, lr_d, lr_g, weight_decay,
                           lambda_adv=1.0, gamma_ent=0.1, iters_per_epoch=None, save_path=None):
    """
    encoder_s, classifier_s: pretrained source models (frozen)
    encoder_t: target encoder to train
    globalD: global discriminator for pooled features
    localD: local discriminator for conv feature maps (per-cell logits)
    lambda_adv: weight for adversarial losses (you can keep 1.0)
    gamma_ent: weight for attentive entropy (paper uses small 0.1)
    """
    encoder_s.to(device); classifier_s.to(device)
    encoder_t.to(device); globalD.to(device); localD.to(device)

    # freeze source encoder & classifier
    encoder_s.eval()
    for p in encoder_s.parameters(): p.requires_grad = False
    classifier_s.eval()
    for p in classifier_s.parameters(): p.requires_grad = False

    # optimizers
    opt_d = optim.Adam(list(globalD.parameters()) + list(localD.parameters()), lr=lr_d, weight_decay=weight_decay)
    opt_g = optim.Adam(encoder_t.parameters(), lr=lr_g, weight_decay=weight_decay)

    # losses
    bce = nn.BCEWithLogitsLoss()
    ce = nn.CrossEntropyLoss()  # not used for unsupervised target, but kept

    src_iter = iter(src_loader)
    tgt_iter = iter(tgt_loader)

    if iters_per_epoch is None:
        iters = min(len(src_loader), len(tgt_loader))
    else:
        iters = iters_per_epoch

    for ep in range(epochs):
        globalD.train(); localD.train(); encoder_t.train()
        pbar = tqdm(range(iters), desc=f"Adapt Ep {ep+1}/{epochs}")
        for i in pbar:
            # fetch batches
            try:
                xs, _ = next(src_iter)
            except StopIteration:
                src_iter = iter(src_loader); xs, _ = next(src_iter)
            try:
                xt, _ = next(tgt_iter)
            except StopIteration:
                tgt_iter = iter(tgt_loader); xt, _ = next(tgt_iter)

            xs = xs.to(device); xt = xt.to(device)

            # -----------------------
            # (A) Train discriminators (global + local)
            # -----------------------
            # global: pooled features
            with torch.no_grad():
                _, feat_s_pool = encoder_s(xs, return_map=True)  # pooled source
            # from target (detach) get conv map and pooled
            fmap_t_det, feat_t_pool_det = encoder_t(xt, return_map=True)
            feat_t_pool_det = feat_t_pool_det.detach()
            # global preds
            pred_s_global = globalD(feat_s_pool)
            pred_t_global = globalD(feat_t_pool_det)
            label_s = torch.ones_like(pred_s_global, device=device)
            label_t = torch.zeros_like(pred_t_global, device=device)
            loss_d_global = bce(pred_s_global, label_s) + bce(pred_t_global, label_t)

            # local discriminator: use conv maps (detach)
            # source conv map
            with torch.no_grad():
                fmap_s, _ = encoder_s(xs, return_map=True)
            fmap_t_det = fmap_t_det.detach()
            logits_s_local = localD(fmap_s)   # B x 1 x H x W (logits)
            logits_t_local = localD(fmap_t_det)
            # expand labels to spatial shape
            label_s_local = torch.ones_like(logits_s_local, device=device)
            label_t_local = torch.zeros_like(logits_t_local, device=device)
            loss_d_local = bce(logits_s_local, label_s_local) + bce(logits_t_local, label_t_local)

            loss_d = (loss_d_global + loss_d_local) * 0.5  # combine (you can tune weighting)
            opt_d.zero_grad(); loss_d.backward(); opt_d.step()

            # -----------------------
            # (B) Train target encoder (generator) to fool D and apply attentive entropy
            # -----------------------
            # forward pass (no detach) for target
            fmap_t, feat_t_pool = encoder_t(xt, return_map=True)
            # --- global adversarial loss: want D(feat_t_pool) -> 1
            pred_tg = globalD(feat_t_pool)
            loss_g_global = bce(pred_tg, torch.ones_like(pred_tg, device=device))

            # --- local adversarial loss: want localD(fmap_t) -> 1 per cell
            logits_local_t = localD(fmap_t)  # logits per cell
            # reshape to (B, -1) to compute BCE
            label_local_target = torch.ones_like(logits_local_t, device=device)
            loss_g_local = bce(logits_local_t, label_local_target)

            # --- prepare local attention weights (wki) from local discriminator outputs
            # convert logits to probs and compute entropy per spatial cell
            with torch.no_grad():
                probs_local_t = torch.sigmoid(logits_local_t)  # B x 1 x H x W
                # compute binary entropy per cell
                eps = 1e-8
                p = probs_local_t.clamp(eps, 1-eps)
                h_cell = - (p * torch.log(p) + (1-p) * torch.log(1-p))  # B x1 x H x W
                w_cell = 1.0 - h_cell  # higher when cell is more transferable
                # ensure shape B x 1 x H x W
            # Apply residual attention to fmap_t: hki = (1 + wki) * fki
            # broadcast w_cell over channel dim
            fmap_att = (1.0 + w_cell) * fmap_t  # B x C x H x W  (w_cell will broadcast)

            # pool the attended fmap -> new pooled feature
            import torch.nn.functional as F

            pooled_att = F.adaptive_avg_pool2d(fmap_att, (1,1))
            pooled_att = torch.flatten(pooled_att, 1)


            # --- classifier predictions on pooled_att (use source classifier)
            logits_target = classifier_s(pooled_att)
            prob_target = torch.softmax(logits_target, dim=1)
            # attentive entropy: weight sample entropies with global attention from globalD's output
            # compute global discriminator probability (feed feat_t_pool through globalD to get d_hat)
            with torch.no_grad():
                d_hat_image = torch.sigmoid(globalD(feat_t_pool))  # B x 1
                d_hat_image = d_hat_image.clamp(1e-8, 1-1e-8)
                # binary entropy of d_hat_image
                h_image = - (d_hat_image * torch.log(d_hat_image) + (1-d_hat_image) * torch.log(1-d_hat_image))  # B x 1
                m_i = 1.0 + h_image  # B x 1 (global attention)
            # compute per-sample entropy of classifier (sum_j p_ij log p_ij)
            eps = 1e-8
            p = prob_target.clamp(eps, 1.0)
            ent_sample = - (p * torch.log(p)).sum(dim=1, keepdim=True)  # B x 1
            # attentive entropy loss (we only apply to target samples here)
            loss_att_ent = (m_i * ent_sample).mean()  # scalar

            # combine generator losses
            # We want to fool both discriminators, and also apply attentive entropy minimization (paper uses -gamma*Lh in objective for minimization; we add gamma * Lh)
            loss_g = lambda_adv * (loss_g_global + loss_g_local) + gamma_ent * loss_att_ent

            opt_g.zero_grad(); loss_g.backward(); opt_g.step()

            pbar.set_postfix(loss_d=loss_d.item(), loss_g=loss_g.item(),
                             loss_g_global=loss_g_global.item(), loss_g_local=loss_g_local.item(),
                             loss_att_ent=loss_att_ent.item())

        # Optionally save checkpoints
        if save_path is not None:
            torch.save({'encoder_t':encoder_t.state_dict(), 'globalD':globalD.state_dict(), 'localD':localD.state_dict()}, save_path)

# ----------------------------
# Evaluation (uses encoder(x, return_map=False) for pooled)
# ----------------------------
def evaluate_model(encoder, classifier, test_loader, device, classes, save_csv=None, cm_path=None):
    encoder.eval(); classifier.eval()
    all_preds = []; all_probs = []; all_labels = []
    with torch.no_grad():
        for x, y in tqdm(test_loader, desc="Evaluating"):
            x = x.to(device)
            # get pooled feature
            _, feats = encoder(x, return_map=True)
            logits = classifier(feats)
            probs = torch.softmax(logits, dim=1).cpu().numpy()
            preds = logits.argmax(dim=1).cpu().numpy()
            all_probs.append(probs)
            all_preds.extend(preds.tolist())
            all_labels.extend(y.numpy().tolist())
    all_probs = np.vstack(all_probs)
    report = classification_report(all_labels, all_preds, target_names=classes, output_dict=True)
    df = pd.DataFrame(report).transpose()
    if save_csv:
        df.to_csv(save_csv, index=True)
        print("Saved classification report to", save_csv)
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
# CLI main
# ----------------------------
def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source-dir', required=True, help='ImageFolder source root (class subfolders)')
    p.add_argument('--target-dir', required=True, help='ImageFolder target root (can be unlabeled, e.g., one folder)')
    p.add_argument('--test-dir', required=True, help='Labeled target test folder (ImageFolder)')
    p.add_argument('--out-dir', default='outputs/adda_tada', help='output folder')
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
    # TADA hyperparams
    p.add_argument('--lambda-adv', type=float, default=1.0, help='weight for adversarial loss')
    p.add_argument('--gamma-ent', type=float, default=0.1, help='weight for attentive entropy loss')
    args = p.parse_args()

    set_seed(args.seed)
    os.makedirs(args.out_dir, exist_ok=True)
    device = torch.device(args.device if torch.cuda.is_available() and args.device.startswith('cuda') else 'cpu')

    src_loader, tgt_loader, test_loader, classes = make_dataloaders(
        args.source_dir, args.target_dir, args.test_dir,
        batch_size=args.batch_size, img_size=args.img_size, num_workers=args.num_workers)

    # build models
    encoder_s, feat_dim = get_mobilenetv2_encoder(pretrained=True)
    classifier_s = ClassifierHead(feat_dim, len(classes))
    encoder_t, _ = get_mobilenetv2_encoder(pretrained=True)
    encoder_t.load_state_dict(encoder_s.state_dict())  # init target with source weights

    globalD = GlobalDiscriminator(in_dim=feat_dim, hidden=1024)
    localD = LocalDiscriminator(in_channels=feat_dim, hidden_channels=512)

    # Pretrain source
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
    print(">>> Adapting target encoder via ADDA + TADA")
    adapt_ckpt = os.path.join(args.out_dir, 'adapted_tada.pth')
    adapt_target_ADDA_TADA(encoder_s, classifier_s, encoder_t, globalD, localD,
                           src_loader, tgt_loader, device,
                           args.adapt_epochs, args.lr_d, args.lr_g, args.weight_decay,
                           lambda_adv=args.lambda_adv, gamma_ent=args.gamma_ent,
                           save_path=adapt_ckpt)

    # Evaluation on labeled target test set (use target encoder + source classifier)
    print(">>> Evaluating adapted model on labeled target test")
    eval_csv = os.path.join(args.out_dir, 'classification_report.csv')
    cm_path = os.path.join(args.out_dir, 'confusion_matrix.png')
    df, cm = evaluate_model(encoder_t, classifier_s, test_loader, device, classes, save_csv=eval_csv, cm_path=cm_path)
    print(df)

if __name__ == '__main__':
    main()
