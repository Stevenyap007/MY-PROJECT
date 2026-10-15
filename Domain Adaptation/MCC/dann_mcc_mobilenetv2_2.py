# DANN + MCC with MobileNetV2 (Colab-ready)
# --------------------------------------------------
# This script:
# - Accepts dataset paths from notebook/CLI
# - Saves best model
# - Reports Accuracy, Precision, Recall, F1
# - Plots Confusion Matrix

import os
import argparse
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import numpy as np

# -----------------------------
# 1. Argument parser (Colab / CLI friendly)
# -----------------------------
parser = argparse.ArgumentParser()
parser.add_argument('--source_path', type=str, required=True)
parser.add_argument('--target_unlabeled_path', type=str, required=True)
parser.add_argument('--target_labeled_path', type=str, required=True)
parser.add_argument('--save_path', type=str, default='best_model.pth')
parser.add_argument('--epochs', type=int, default=30)
args, _ = parser.parse_known_args()

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
NUM_CLASSES = 7
BATCH_SIZE = 16
LR = 1e-4
LAMBDA_ADV = 1.0
LAMBDA_MCC = 0.1
TEMPERATURE = 2.0

# -----------------------------
# 2. Transforms
# -----------------------------
train_tf = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])
])

test_tf = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])
])

# -----------------------------
# 3. Datasets & loaders
# -----------------------------
source_ds = datasets.ImageFolder(args.source_path, transform=train_tf)
target_unlabeled_ds = datasets.ImageFolder(args.target_unlabeled_path, transform=train_tf)
target_eval_ds = datasets.ImageFolder(args.target_labeled_path, transform=test_tf)

source_loader = DataLoader(source_ds, batch_size=BATCH_SIZE, shuffle=True, drop_last=True)
target_loader = DataLoader(target_unlabeled_ds, batch_size=BATCH_SIZE, shuffle=True, drop_last=True)
target_eval_loader = DataLoader(target_eval_ds, batch_size=BATCH_SIZE, shuffle=False)

class_names = target_eval_ds.classes

# -----------------------------
# 4. Gradient Reversal Layer
# -----------------------------
class GRL(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x, lambd):
        ctx.lambd = lambd
        return x.view_as(x)

    @staticmethod
    def backward(ctx, grad_output):
        return -ctx.lambd * grad_output, None

# -----------------------------
# 5. Model
# -----------------------------
class DANN_MCC(nn.Module):
    def __init__(self, num_classes):
        super().__init__()
        base = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.IMAGENET1K_V1)
        self.feature = base.features
        self.pool = nn.AdaptiveAvgPool2d((1,1))
        self.feat_dim = 1280
        self.classifier = nn.Linear(self.feat_dim, num_classes)
        self.domain = nn.Sequential(
            nn.Linear(self.feat_dim, 256), nn.ReLU(), nn.Linear(256, 2)
        )

    def forward(self, x, lambd=1.0):
        f = self.feature(x)
        f = self.pool(f).view(x.size(0), -1)
        y = self.classifier(f)
        d = self.domain(GRL.apply(f, lambd))
        return y, d

# -----------------------------
# 6. MCC loss
# -----------------------------
def mcc_loss(logits, T=2.0):
    p = torch.softmax(logits / T, dim=1)
    C = torch.matmul(p.T, p) / p.size(0)
    C = C / (C.sum(dim=1, keepdim=True) + 1e-6)
    off_diag = C - torch.diag(torch.diag(C))
    return off_diag.abs().sum() / p.size(1)

# -----------------------------
# 7. Training
# -----------------------------
model = DANN_MCC(NUM_CLASSES).to(DEVICE)
optimizer = optim.Adam(model.parameters(), lr=LR)
cls_criterion = nn.CrossEntropyLoss()
dom_criterion = nn.CrossEntropyLoss()

best_acc = 0.0

for epoch in range(args.epochs):
    model.train()
    for (xs, ys), (xt, _) in zip(source_loader, target_loader):
        xs, ys, xt = xs.to(DEVICE), ys.to(DEVICE), xt.to(DEVICE)
        x = torch.cat([xs, xt], dim=0)
        y_logits, d_logits = model(x, LAMBDA_ADV)
        y_s, y_t = y_logits.chunk(2, dim=0)
        d_s, d_t = d_logits.chunk(2, dim=0)

        cls_loss = cls_criterion(y_s, ys)
        dom_labels = torch.cat([
            torch.zeros(xs.size(0)), torch.ones(xt.size(0))
        ]).long().to(DEVICE)
        dom_loss = dom_criterion(torch.cat([d_s, d_t], dim=0), dom_labels)
        mcc = mcc_loss(y_t, TEMPERATURE)
        loss = cls_loss + LAMBDA_ADV * dom_loss + LAMBDA_MCC * mcc

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    # -------------------------
    # Validation
    # -------------------------
    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for x, y in target_eval_loader:
            x, y = x.to(DEVICE), y.to(DEVICE)
            logits, _ = model(x, 0)
            pred = logits.argmax(1)
            correct += (pred == y).sum().item()
            total += y.size(0)

    acc = correct / total
    print(f"Epoch [{epoch+1}/{args.epochs}] Target Acc: {acc:.4f}")

    if acc > best_acc:
        best_acc = acc
        torch.save(model.state_dict(), args.save_path)

# -----------------------------
# 8. Final evaluation
# -----------------------------
model.load_state_dict(torch.load(args.save_path))
model.eval()

y_true, y_pred = [], []
with torch.no_grad():
    for x, y in target_eval_loader:
        x = x.to(DEVICE)
        logits, _ = model(x, 0)
        preds = logits.argmax(1).cpu().numpy()
        y_pred.extend(preds)
        y_true.extend(y.numpy())

print("\nClassification Report:\n")
print(classification_report(y_true, y_pred, target_names=class_names, digits=4))

cm = confusion_matrix(y_true, y_pred)
plt.figure(figsize=(8,6))
plt.imshow(cm)
plt.title('Confusion Matrix')
plt.colorbar()
plt.xticks(np.arange(len(class_names)), class_names, rotation=45)
plt.yticks(np.arange(len(class_names)), class_names)
plt.xlabel('Predicted')
plt.ylabel('True')
plt.tight_layout()
plt.show()
