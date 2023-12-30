import os
# import random
import numpy as np
from sklearn.model_selection import train_test_split

def copy_images(src_folder, dest_folder, image_list):
    for image in image_list:
        src_path = os.path.join(src_folder, image)
        dest_path = os.path.join(dest_folder, image)
        with open(src_path, 'rb') as src, open(dest_path, 'wb') as dest:
            dest.write(src.read())

# Set the path to your image dataset folder
dataset_path = "trial and error/Dataset"

# Set the path where you want to create the training and testing folders
output_path = "trial and error/output"

# Create output folders if they don't exist
for folder in ['train', 'test']:
    folder_path = os.path.join(output_path, folder)
    os.makedirs(folder_path, exist_ok=True)

# Get a list of all class folders in the dataset folder
class_folders = [f for f in os.listdir(dataset_path) if os.path.isdir(os.path.join(dataset_path, f))]

# Set the random seed for reproducibility
# random.seed(42)
np.random.seed(42)

# Iterate over each class folder
for class_folder in class_folders:
    class_path = os.path.join(dataset_path, class_folder)

    # Get a list of all image files in the class folder
    class_images = [f for f in os.listdir(class_path) if f.endswith('.jpg') or f.endswith('.png')]

    # Split the class dataset into training and testing sets
    train_images, test_images = train_test_split(class_images, test_size=0.2, random_state=42)

    # Create 'train' and 'test' folders within each class folder
    train_folder_path = os.path.join(output_path, 'train', class_folder)
    test_folder_path = os.path.join(output_path, 'test', class_folder)
    os.makedirs(train_folder_path, exist_ok=True)
    os.makedirs(test_folder_path, exist_ok=True)

    # Copy training images to the 'train' folder within the class folder
    copy_images(class_path, train_folder_path, train_images)

    # Copy testing images to the 'test' folder within the class folder
    copy_images(class_path, test_folder_path, test_images)

import os
import numpy as np
import cv2

classifier = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

train_path = 'trial and error/output/train'

classes = os.listdir(train_path)

# ['felix', 'jokowi', 'jonas', 'nayeon']
# 0 1 2 3

image_list = []
class_list = []

for i, c in enumerate(classes):
    class_path = f'{train_path}/{c}'
    # print(class_path)
    # print(os.listdir(class_path))

    for image_path in os.listdir(class_path):
        full_image_path = f'{class_path}/{image_path}'

        image = cv2.imread(full_image_path, cv2.IMREAD_GRAYSCALE)

        # cv2.imshow('Image',image)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        detected_faces = classifier.detectMultiScale(image,scaleFactor = 1.2, minNeighbors = 5)

        if len(detected_faces) < 1:
            continue

        for face_rect in detected_faces:
            x, y, w, h = face_rect
            cropped_image = image[y:y+h, x:x+w]
            image_list.append(cropped_image)
            class_list.append(i)


recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.train(image_list, np.array(class_list))

test_path = 'trial and error/output/test'

for image_path in os.listdir(test_path):
    # print(f'{test_path}/{image_path}')
    full_image_path = f'{test_path}/{image_path}'

    image = cv2.imread(full_image_path)
    image_gray = cv2.imread(full_image_path, cv2.IMREAD_GRAYSCALE)

    detected_faces = classifier.detectMultiScale(image_gray, scaleFactor = 1.2, minNeighbors = 5)

    if len(detected_faces) < 1:
        continue

    for face_rect in detected_faces:
        x, y, w, h = face_rect
        face_image = image_gray[y:y+h, x:x+w]

        result, confidence = recognizer.predict(face_image)

        cv2.rectangle(image, (x,y), (x + w, y + h), (0,255,0), 1)

        image_text = f'{classes[result]}: {confidence}'
        cv2.putText(image, image_text, (x, y - 10), cv2.FONT_HERSHEY_PLAIN, 1.5, (0,255,0))
        cv2.imshow('Result', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()



# print(image_list)
# print(class_list)
            





