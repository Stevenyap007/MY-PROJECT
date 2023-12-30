import os
import cv2
from sklearn.model_selection import train_test_split
import numpy as np
from collections import Counter

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





# Check the distribution of classes in the training set
train_label_counts = Counter(train_labels)
print("\nTraining set class distribution:")
print(train_label_counts)

# Check the distribution of classes in the testing set
test_label_counts = Counter(test_labels)
print("\nTesting set class distribution:")
print(test_label_counts)

classifier = cv2.CascadeClassifier('kepanjangan/trial and error/haarcascade_frontalface_default.xml')



# ... (your existing code)

# Train the face recognizer
face_list = []
face_label_list = []
train_face = 0
total_detected_faces = 0

for i, image_path in enumerate(train_images):
    full_image_path = train_image_paths[i]
    image = cv2.imread(full_image_path, cv2.IMREAD_GRAYSCALE)
    
    # Adjusting parameters for better face detection
    detected_faces = classifier.detectMultiScale(image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
    if len(detected_faces) >= 1:
        total_detected_faces += 1

    if len(detected_faces) < 1:
        train_face += 1
        continue

    for face_rect in detected_faces:
        x, y, w, h = face_rect
        cropped_image = cv2.resize(image[y:y+h, x:x+w], (100, 100))
        face_list.append(cropped_image)
        face_label_list.append(i)

print("Total detected faces in the training set:", total_detected_faces)
print("Number of images without faces:", train_face)

# print(train_face)

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.train(face_list, np.array(face_label_list))

# Test the face recognizer and calculate accuracy
correct_predictions = 0
total_faces = 0
total_accuracy = 0
total_detected_faces_test = 0
test_face = 0

for i, image_path in enumerate(test_images):
    image = cv2.imread(test_image_paths[i])  # Load the image in color
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Convert the color image to grayscale
    detected_faces = classifier.detectMultiScale(image_gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(detected_faces) >= 1:
        total_detected_faces_test += 1


    if len(detected_faces) < 1:
        print(len(detected_faces))
        test_face += 1
        continue

    

    for face_rect in detected_faces:
        x, y, w, h = face_rect
        face_image_gray = cv2.resize(image_gray[y:y+h, x:x+w], (100, 100))
        
        result, confidence = recognizer.predict(face_image_gray)
        accuracy = (1 - (confidence / 300)) * 100
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 1)

        predicted_label = train_labels[result]
        true_label = test_labels[i]

        if predicted_label == true_label:
            correct_predictions += 1

        total_faces += 1

        image_text = f'{predicted_label}: {accuracy:.2f}%'
        print(f"Player: {predicted_label}, Accuracy: {accuracy:.2f}%")
        total_accuracy += accuracy
        cv2.putText(image, image_text, (x, y - 10), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0))

    cv2.imshow('Result', image)
    cv2.waitKey(0)

print("Total detected faces in the testing set:", total_detected_faces_test)
print("Number of images without faces testing:", train_face)
accuracy_percentage = (correct_predictions / total_faces) * 100
print(f"\nModel Accuracy: {accuracy_percentage:.2f}%")

print("akurasi manual {:.2f}%".format(total_accuracy/(40*100)*100))


cv2.destroyAllWindows()


    # Example: Tune Haar Cascade parameters for better face detection
# Example: Tune Haar Cascade parameters for better face detection
# scale_factors = [1.1, 1.2, 1.3, 1.4]
# min_neighbors_values = [3, 4, 5, 6]

# best_parameters = None
# best_num_detected_faces = 0

# for scale_factor in scale_factors:
#     for min_neighbors in min_neighbors_values:
#         # Create a new Haar Cascade classifier with the current parameters
#         classifier = cv2.CascadeClassifier('kepanjangan/trial and error/haarcascade_frontalface_default.xml')

#         # Apply the current parameters to detect faces
#         detected_faces = classifier.detectMultiScale(image_gray, scaleFactor=scale_factor, minNeighbors=min_neighbors)

#         # Count the number of detected faces
#         num_detected_faces = len(detected_faces)
        
#         # Update if the current parameters result in more detected faces
#         if num_detected_faces > best_num_detected_faces:
#             best_num_detected_faces = num_detected_faces
#             best_parameters = (scale_factor, min_neighbors)

# # Print the best parameters
# print(f"Best Parameters: Scale Factor = {best_parameters[0]}, Min Neighbors = {best_parameters[1]}")

# # Suggestion based on best parameters
# if best_num_detected_faces > 0:
#     print("Suggestion: Consider using these parameters for face detection.")
# else:
#     print("Suggestion: No faces detected with any parameter combination. Adjust parameters or inspect the dataset.")



# cv2.destroyAllWindows()
