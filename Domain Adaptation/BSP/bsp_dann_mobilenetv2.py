import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torchvision.models import mobilenet_v2
from sklearn.metrics import classification_report, confusion_matrix

# =========================
# DEVICE
# =========================
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# =========================
# HYPERPARAMS (DEFAULTS)
# =========================
BATCH_SIZE = 16
EPOCHS = 30
LR = 3e-4
LAMBDA_ADV = 1.0
LAMBDA_BSP = 2e-4
NUM_WORKERS = 2

# =========================
# TRANSFORMS
# =========================
train_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

test_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# =========================
# GRADIENT REVERSAL
# =========================
class GradientReversal(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x, lambda_):
        ctx.lambda_ = lambda_
        return x.view_as(x)

    @staticmethod
    def backward(ctx, grad_output):
        return -ctx.lambda_ * grad_output, None

# =========================
# MODELS
# =========================
class ImageClassifier(nn.Module):
    def __init__(self, num_classes):
        super().__init__()
        base = mobilenet_v2(weights="IMAGENET1K_V1")
        self.features = base.features
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.bottleneck = nn.Linear(1280, 256)
        self.classifier = nn.Linear(256, num_classes)

    def forward(self, x):
        f = self.features(x)
        f = self.pool(f).flatten(1)
        f = self.bottleneck(f)
        y = self.classifier(f)
        return y, f


class DomainDiscriminator(nn.Module):
    def __init__(self, in_dim=256):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, 1024),
            nn.ReLU(),
            nn.Linear(1024, 1)
        )

    def forward(self, x):
        return self.net(x)

# =========================
# BSP LOSS
# =========================
def bsp_loss(f_s, f_t):
    _, s_s, _ = torch.linalg.svd(f_s, full_matrices=False)
    _, s_t, _ = torch.linalg.svd(f_t, full_matrices=False)
    return torch.mean(s_s ** 2) + torch.mean(s_t ** 2)

# =========================
# CORE TRAIN FUNCTION
# =========================
def train_bsp(
    source_dir,
    target_unlabeled_dir,
    target_labeled_dir,
    num_classes=7
):
    # -------------------------
    # DATASETS
    # -------------------------
    source_ds = datasets.ImageFolder(
        source_dir, transform=train_transform
    )

    target_unlabeled_ds = datasets.ImageFolder(
        target_unlabeled_dir, transform=train_transform
    )

    target_test_ds = datasets.ImageFolder(
        target_labeled_dir, transform=test_transform
    )

    source_loader = DataLoader(
        source_ds, batch_size=BATCH_SIZE,
        shuffle=True, drop_last=True,
        num_workers=NUM_WORKERS
    )

    target_loader = DataLoader(
        target_unlabeled_ds, batch_size=BATCH_SIZE,
        shuffle=True, drop_last=True,
        num_workers=NUM_WORKERS
    )

    target_test_loader = DataLoader(
        target_test_ds, batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=NUM_WORKERS
    )

    # -------------------------
    # MODELS
    # -------------------------
    model = ImageClassifier(num_classes).to(DEVICE)
    domain_disc = DomainDiscriminator().to(DEVICE)

    optimizer = torch.optim.SGD(
        list(model.parameters()) + list(domain_disc.parameters()),
        lr=LR, momentum=0.9
    )

    # -------------------------
    # TRAINING LOOP
    # -------------------------
    for epoch in range(EPOCHS):
        model.train()
        domain_disc.train()
        total_loss = 0.0

        for (xs, ys), (xt, _) in zip(source_loader, target_loader):
            xs, ys = xs.to(DEVICE), ys.to(DEVICE)
            xt = xt.to(DEVICE)

            x = torch.cat([xs, xt], dim=0)
            y, f = model(x)

            y_s, _ = y.chunk(2)
            f_s, f_t = f.chunk(2)

            cls_loss = F.cross_entropy(y_s, ys)

            f_rev = GradientReversal.apply(f, 1.0)
            d_logits = domain_disc(f_rev).squeeze()

            d_labels = torch.cat([
                torch.ones(len(f_s)),
                torch.zeros(len(f_t))
            ]).to(DEVICE)

            adv_loss = F.binary_cross_entropy_with_logits(
                d_logits, d_labels
            )

            bsp = bsp_loss(f_s, f_t)

            loss = cls_loss + LAMBDA_ADV * adv_loss + LAMBDA_BSP * bsp

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        print(f"[Epoch {epoch+1}/{EPOCHS}] Loss: {total_loss:.4f}")

    print("Training finished.\n")

    # -------------------------
    # EVALUATION
    # -------------------------
    model.eval()
    all_preds, all_labels = [], []

    with torch.no_grad():
        for x, y in target_test_loader:
            x = x.to(DEVICE)
            logits, _ = model(x)
            preds = logits.argmax(1).cpu().numpy()
            all_preds.extend(preds)
            all_labels.extend(y.numpy())

    print("Classification Report (Target Domain):")
    print(classification_report(
        all_labels, all_preds,
        target_names=source_ds.classes
    ))

    print("Confusion Matrix:")
    print(confusion_matrix(all_labels, all_preds))

    return model
