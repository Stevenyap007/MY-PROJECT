import os
import cv2
from sklearn.model_selection import train_test_split
import numpy as np

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

# Split the dataset into training and testing sets while maintaining class distribution
train_image_paths, test_image_paths, train_labels, test_labels = train_test_split(
    image_paths, labels, test_size=0.2, random_state=42, stratify=labels
)

# Now you have your training and testing sets, and you can load the images using OpenCV.
# For example, you can use the following to load images using cv2:
train_images = [cv2.imread(path) for path in train_image_paths]
test_images = [cv2.imread(path) for path in test_image_paths]

# Print the size of the training and testing sets
print(f"Number of training samples: {len(train_images)}")
print(f"Number of testing samples: {len(test_images)}")

classifier = cv2.CascadeClassifier('kepanjangan/trial and error/haarcascade_frontalface_default.xml')

import os
import cv2
from sklearn.model_selection import train_test_split
import numpy as np

# ... (your existing code)

# Train the face recognizer
face_list = []
face_label_list = []

for i, image_path in enumerate(train_images):
    full_image_path = train_image_paths[i]
    image = cv2.imread(full_image_path, cv2.IMREAD_GRAYSCALE)
    detected_faces = classifier.detectMultiScale(image, scaleFactor=1.1, minNeighbors=6)

    if len(detected_faces) < 1:
        continue

    for face_rect in detected_faces:
        x, y, w, h = face_rect
        cropped_image = image[y:y+h, x:x+w]
        face_list.append(cropped_image)
        face_label_list.append(i)

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.train(face_list, np.array(face_label_list))

# Test the face recognizer and calculate accuracy
correct_predictions = 0
total_faces = 0
total_accuracy = 0

for i, image_path in enumerate(test_images):
    image = cv2.imread(test_image_paths[i])  # Load the image in color
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Convert the color image to grayscale
    detected_faces = classifier.detectMultiScale(image_gray, scaleFactor=1.1, minNeighbors=6)

    if len(detected_faces) < 1:
        continue

    for face_rect in detected_faces:
        x, y, w, h = face_rect
        face_image_gray = image_gray[y:y+h, x:x+w]
        
        result, confidence = recognizer.predict(face_image_gray)
        accuracy = (1 - (confidence / 300)) * 100
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 1)

        predicted_label = train_labels[result]
        true_label = test_labels[i]

        if predicted_label == true_label:
            correct_predictions += 1

        total_faces += 1

        image_text = f'{predicted_label}: {accuracy:.2f}%'
        total_accuracy += accuracy
        cv2.putText(image, image_text, (x, y - 10), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0))

    cv2.imshow('Result', image)
    cv2.waitKey(0)

print("akurasi manual {:.2f}%".format(total_accuracy/(40*100)*100))


cv2.destroyAllWindows()
