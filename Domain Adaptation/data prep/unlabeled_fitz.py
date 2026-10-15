import os
import shutil
from glob import glob

# Labeled Fitz grouped by ISIC classes
fitz_labeled = "fitz_selected"        # e.g., fitz_selected/mel/, fitz_selected/nv/, ...
fitz_unlabeled = "fitz_unlabeled"     # Output folder for unlabeled target domain

# Create output directory
os.makedirs(fitz_unlabeled, exist_ok=True)

# Loop over class folders in labeled source
for class_name in os.listdir(fitz_labeled):
    class_folder = os.path.join(fitz_labeled, class_name)
    if not os.path.isdir(class_folder):
        continue

    for img_path in glob(os.path.join(class_folder, "*.*")):
        if img_path.lower().endswith((".jpg", ".jpeg", ".png")):
            # Rename to avoid filename collisions
            new_name = f"{class_name}_{os.path.basename(img_path)}"
            dst_path = os.path.join(fitz_unlabeled, new_name)

            # Copy the file (not move)
            shutil.copy2(img_path, dst_path)

print("✅ All labeled images copied to 'fitz_unlabeled/' for UDA.")
