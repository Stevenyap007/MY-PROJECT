import os
import random
from sklearn.model_selection import train_test_split

# Set the path to your image dataset folder
dataset_path = "kepanjangan/trial and error/Dataset"

# Set the path where you want to create the training and testing folders
output_path = "kepanjangan/trial and error/SPLIT/output2"

# Create output folders if they don't exist
for folder in ['train', 'test']:
    folder_path = os.path.join(output_path, folder)
    os.makedirs(folder_path, exist_ok=True)

# Get a list of all class folders in the dataset folder
class_folders = [f for f in os.listdir(dataset_path) if os.path.isdir(os.path.join(dataset_path, f))]

# Set the random seed for reproducibility
random.seed(42)

# Iterate over each class folder
for class_folder in class_folders:
    class_path = os.path.join(dataset_path, class_folder)

    # Get a list of all image files in the class folder
    class_images = [f for f in os.listdir(class_path) if f.endswith('.jpg') or f.endswith('.png')]

    # Split the class dataset into training and testing sets
    train_images, test_images = train_test_split(class_images, test_size=0.2, random_state=42)

    # Copy training images to the 'train' folder within the respective class folder
    for image in train_images:
        src_path = os.path.join(class_path, image)
        dest_path = os.path.join(output_path, 'train', class_folder, image)
        os.makedirs(os.path.join(output_path, 'train', class_folder), exist_ok=True)
        with open(src_path, 'rb') as src, open(dest_path, 'wb') as dest:
            dest.write(src.read())

    # Copy testing images to the 'test' folder within the respective class folder
    for image in test_images:
        src_path = os.path.join(class_path, image)
        dest_path = os.path.join(output_path, 'test', class_folder, image)
        os.makedirs(os.path.join(output_path, 'test', class_folder), exist_ok=True)
        with open(src_path, 'rb') as src, open(dest_path, 'wb') as dest:
            dest.write(src.read())
