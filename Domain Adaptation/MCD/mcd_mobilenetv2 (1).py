import os
import argparse
import itertools
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from itertools import cycle

# -----------------------------
# Argument parser
# -----------------------------
def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--isic_path', type=str, required=False,
                        help='Path to ISIC2019 labeled dataset')
    parser.add_argument('--fitz_unlab_path', type=str, required=False,
                        help='Path to Fitzpatrick unlabeled dataset')

    parser.add_argument('--fitz_test_path', type=str, default=None,
                        help='Path to Fitzpatrick LABELED test dataset')

    parser.add_argument('--epochs', type=int, default=30)
    parser.add_argument('--batch_size', type=int, default=32)
    parser.add_argument('--lr', type=float, default=1e-4)
    parser.add_argument('--k', type=int, default=4)

    parser.add_argument('--save_dir', type=str, default='./checkpoints')
    parser.add_argument('--eval_only', action='store_true',
                        help='Skip training and run evaluation only')

    return parser.parse_args()


# -----------------------------
# Models
# -----------------------------
class FeatureExtractor(nn.Module):
    def __init__(self):
        super().__init__()
        base = models.mobilenet_v2(
            weights=models.MobileNet_V2_Weights.IMAGENET1K_V1
        )
        self.features = base.features
        self.pool = nn.AdaptiveAvgPool2d(1)

    def forward(self, x):
        x = self.features(x)
        x = self.pool(x)
        return x.view(x.size(0), -1)


class Classifier(nn.Module):
    def __init__(self, in_dim, num_classes):
        super().__init__()
        self.fc = nn.Linear(in_dim, num_classes)

    def forward(self, x):
        return self.fc(x)


# -----------------------------
# Main
# -----------------------------
def main():
    args = get_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    os.makedirs(args.save_dir, exist_ok=True)

    # -----------------------------
    # Transforms
    # -----------------------------
    train_tf = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    test_tf = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])

    # -----------------------------
    # Evaluation-only mode
    # -----------------------------
    if args.eval_only:
        assert args.fitz_test_path is not None, "Provide --fitz_test_path"

        ckpt = torch.load(
            os.path.join(args.save_dir, "mcd_mobilenetv2_best.pth"),
            map_location=device
        )

        num_classes = ckpt["num_classes"]

        G = FeatureExtractor().to(device)
        F1 = Classifier(1280, num_classes).to(device)
        F2 = Classifier(1280, num_classes).to(device)

        G.load_state_dict(ckpt["G"])
        F1.load_state_dict(ckpt["F1"])
        F2.load_state_dict(ckpt["F2"])

        G.eval()
        F1.eval()
        F2.eval()

        test_set = datasets.ImageFolder(
            args.fitz_test_path, transform=test_tf
        )
        test_loader = DataLoader(
            test_set, batch_size=32, shuffle=False, num_workers=2
        )

        correct, total = 0, 0

        with torch.no_grad():
            for x, y in test_loader:
                x, y = x.to(device), y.to(device)

                feat = G(x)
                logits = (F1(feat) + F2(feat)) / 2
                preds = logits.argmax(dim=1)

                correct += (preds == y).sum().item()
                total += y.size(0)

        acc = 100.0 * correct / total
        print(f"[EVAL] Fitzpatrick Accuracy: {acc:.2f}%")
        return

    # -----------------------------
    # Training datasets
    # -----------------------------
    src_set = datasets.ImageFolder(args.isic_path, transform=train_tf)
    tgt_set = datasets.ImageFolder(args.fitz_unlab_path, transform=train_tf)

    num_classes = len(src_set.classes)
    print(f"[INFO] Number of classes: {num_classes}")

    src_loader = DataLoader(
        src_set, batch_size=args.batch_size,
        shuffle=True, drop_last=True, num_workers=2
    )
    tgt_loader = DataLoader(
        tgt_set, batch_size=args.batch_size,
        shuffle=True, drop_last=True, num_workers=2
    )

    src_iter = cycle(src_loader)
    tgt_iter = cycle(tgt_loader)

    # -----------------------------
    # Models
    # -----------------------------
    G = FeatureExtractor().to(device)
    F1 = Classifier(1280, num_classes).to(device)
    F2 = Classifier(1280, num_classes).to(device)

    criterion = nn.CrossEntropyLoss()

    opt_G = optim.Adam(G.parameters(), lr=args.lr)
    opt_F = optim.Adam(
        itertools.chain(F1.parameters(), F2.parameters()), lr=args.lr
    )

    best_loss = float("inf")

    # -----------------------------
    # Training loop (MCD)
    # -----------------------------
    for epoch in range(args.epochs):
        G.train()
        F1.train()
        F2.train()

        for step in range(len(src_loader)):
            x_s, y_s = next(src_iter)
            x_t, _ = next(tgt_iter)

            x_s, y_s = x_s.to(device), y_s.to(device)
            x_t = x_t.to(device)

            opt_G.zero_grad()
            opt_F.zero_grad()

            feat_s = G(x_s)
            out1_s = F1(feat_s)
            out2_s = F2(feat_s)

            loss_A = criterion(out1_s, y_s) + criterion(out2_s, y_s)
            loss_A.backward()
            opt_G.step()
            opt_F.step()

            opt_F.zero_grad()

            feat_t = G(x_t)
            out1_t = F1(feat_t)
            out2_t = F2(feat_t)

            loss_B = -torch.mean(
                torch.abs(
                    torch.softmax(out1_t, dim=1) -
                    torch.softmax(out2_t, dim=1)
                )
            )
            loss_B.backward()
            opt_F.step()

            for _ in range(args.k):
                opt_G.zero_grad()

                feat_t = G(x_t)
                out1_t = F1(feat_t)
                out2_t = F2(feat_t)

                loss_C = torch.mean(
                    torch.abs(
                        torch.softmax(out1_t, dim=1) -
                        torch.softmax(out2_t, dim=1)
                    )
                )
                loss_C.backward()
                opt_G.step()

            if step % 50 == 0:
                print(
                    f"Epoch [{epoch+1}/{args.epochs}] "
                    f"Step [{step}/{len(src_loader)}] "
                    f"LossA: {loss_A.item():.3f} "
                    f"LossB: {loss_B.item():.3f} "
                    f"LossC: {loss_C.item():.3f}"
                )

        if loss_A.item() < best_loss:
            best_loss = loss_A.item()

            torch.save({
                "G": G.state_dict(),
                "F1": F1.state_dict(),
                "F2": F2.state_dict(),
                "num_classes": num_classes,
                "epoch": epoch + 1
            }, os.path.join(args.save_dir, "mcd_mobilenetv2_best.pth"))

            print(f"[INFO] Best model saved at epoch {epoch+1}")

        print(f"[INFO] Finished epoch {epoch+1}")

    torch.save({
        "G": G.state_dict(),
        "F1": F1.state_dict(),
        "F2": F2.state_dict(),
        "num_classes": num_classes,
        "epoch": args.epochs
    }, os.path.join(args.save_dir, "mcd_mobilenetv2_last.pth"))

    print("[INFO] Training completed and final model saved.")


if __name__ == "__main__":
    main()
