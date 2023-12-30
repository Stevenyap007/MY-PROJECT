import os
import cv2
from sklearn.model_selection import train_test_split

# Path to your dataset folder
dataset_path = 'kepanjangan/trial and error/Dataset'

# List to store image paths and labels
image_paths = []
labels = []

# Iterate through each athlete folder
for athlete_folder in os.listdir(dataset_path):
    athlete_path = os.path.join(dataset_path, athlete_folder)
    
    # Iterate through each image in the athlete folder
    for image_file in os.listdir(athlete_path):
        image_path = os.path.join(athlete_path, image_file)
        image_paths.append(image_path)
        labels.append(athlete_folder)

# Split the dataset into training and testing sets
train_image_paths, test_image_paths, train_labels, test_labels = train_test_split(
    image_paths, labels, test_size=0.2, random_state=42
)

# Now you have your training and testing sets, and you can load the images using OpenCV.
# For example, you can use the following to load images using cv2:
train_images = [cv2.imread(path) for path in train_image_paths]
test_images = [cv2.imread(path) for path in test_image_paths]

# Print the size of the training and testing sets
print(f"Number of training samples: {len(train_images)}")
print(f"Number of testing samples: {len(test_images)}")
from collections import Counter

# Check the distribution of classes in the training set
train_label_counts = Counter(train_labels)
print("\nTraining set class distribution:")
print(train_label_counts)

# Check the distribution of classes in the testing set
test_label_counts = Counter(test_labels)
print("\nTesting set class distribution:")
print(test_label_counts)

