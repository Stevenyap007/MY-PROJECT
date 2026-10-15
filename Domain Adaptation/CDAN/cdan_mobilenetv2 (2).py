import argparse
import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as T
import torchvision.models as models
from torch.utils.data import DataLoader
from torchvision.datasets import ImageFolder
from tqdm import tqdm

# =========================
# Gradient Reversal Layer
# =========================
class GradReverse(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x, lambd):
        ctx.lambd = lambd
        return x.view_as(x)

    @staticmethod
    def backward(ctx, grad_output):
        return -ctx.lambd * grad_output, None


def grad_reverse(x, lambd=1.0):
    return GradReverse.apply(x, lambd)


# =========================
# Backbone + Classifier
# =========================
class MobileNetV2CDAN(nn.Module):
    def __init__(self, num_classes):
        super().__init__()
        backbone = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.IMAGENET1K_V1)
        self.features = backbone.features
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.feat_dim = 1280
        self.classifier = nn.Linear(self.feat_dim, num_classes)

    def forward(self, x):
        f = self.features(x)
        f = self.pool(f).view(x.size(0), -1)
        y = self.classifier(f)
        return y, f


# =========================
# Domain Discriminator
# =========================
class DomainDiscriminator(nn.Module):
    def __init__(self, in_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, 1024),
            nn.ReLU(),
            nn.Linear(1024, 1)
        )

    def forward(self, x):
        return self.net(x)


# =========================
# CDAN Feature Construction
# =========================
def cdan_features(f, y):
    """
    f: (B, D)
    y: (B, C)
    returns: (B, D*C)
    """
    y = F.softmax(y, dim=1)
    return torch.bmm(
        y.unsqueeze(2),
        f.unsqueeze(1)
    ).view(f.size(0), -1)


# =========================
# Training Function
# =========================
def train_one_epoch(
    model,
    domain_discriminator,
    source_loader,
    target_loader,
    optimizer,
    device,
    epoch,
    alpha
):
    model.train()
    domain_discriminator.train()

    total_loss = 0
    cls_loss_total = 0
    adv_loss_total = 0

    tgt_iter = iter(target_loader)

    for x_s, y_s in tqdm(source_loader, desc=f"Epoch {epoch}"):
        try:
            x_t, _ = next(tgt_iter)
        except StopIteration:
            tgt_iter = iter(target_loader)
            x_t, _ = next(tgt_iter)

        x_s, y_s = x_s.to(device), y_s.to(device)
        x_t = x_t.to(device)

        # Forward
        y_s_pred, f_s = model(x_s)
        y_t_pred, f_t = model(x_t)

        # Classification loss
        cls_loss = F.cross_entropy(y_s_pred, y_s)

        # CDAN features
        cdan_s = cdan_features(f_s, y_s_pred)
        cdan_t = cdan_features(f_t, y_t_pred)

        cdan_all = torch.cat([cdan_s, cdan_t], dim=0)
        cdan_all = grad_reverse(cdan_all, alpha)

        domain_labels = torch.cat([
            torch.ones(cdan_s.size(0)),
            torch.zeros(cdan_t.size(0))
        ]).to(device)

        domain_preds = domain_discriminator(cdan_all).squeeze()
        adv_loss = F.binary_cross_entropy_with_logits(domain_preds, domain_labels)

        loss = cls_loss + adv_loss

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        cls_loss_total += cls_loss.item()
        adv_loss_total += adv_loss.item()

    n = len(source_loader)
    return total_loss / n, cls_loss_total / n, adv_loss_total / n


# =========================
# Main
# =========================
def main(args):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    transform = T.Compose([
        T.Resize((224, 224)),
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225])
    ])

    source_dataset = ImageFolder(args.source, transform=transform)
    target_dataset = ImageFolder(args.target, transform=transform)

    num_classes = len(source_dataset.classes)
    print("Number of classes:", num_classes)

    source_loader = DataLoader(
        source_dataset, batch_size=args.batch_size,
        shuffle=True, num_workers=2, drop_last=True
    )
    target_loader = DataLoader(
        target_dataset, batch_size=args.batch_size,
        shuffle=True, num_workers=2, drop_last=True
    )

    model = MobileNetV2CDAN(num_classes).to(device)

    cdan_dim = model.feat_dim * num_classes
    domain_discriminator = DomainDiscriminator(cdan_dim).to(device)

    optimizer = torch.optim.Adam(
        list(model.parameters()) + list(domain_discriminator.parameters()),
        lr=args.lr
    )

    print("Start training...")
    for epoch in range(1, args.epochs + 1):
        alpha = min(1.0, epoch / args.epochs)
        loss, cls_loss, adv_loss = train_one_epoch(
            model, domain_discriminator,
            source_loader, target_loader,
            optimizer, device,
            epoch, alpha
        )

        print(
            f"Epoch {epoch}: "
            f"Loss={loss:.4f} "
            f"Cls={cls_loss:.4f} "
            f"Adv={adv_loss:.4f}"
        )

    torch.save(model.state_dict(), "cdan_mobilenetv2.pth")
    print("Model saved.")


# =========================
# Entry
# =========================
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=str, required=True)
    parser.add_argument("--target", type=str, required=True)
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-4)

    args = parser.parse_args()
    main(args)
