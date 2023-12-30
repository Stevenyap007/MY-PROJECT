import os
import cv2
from sklearn.model_selection import train_test_split
import numpy as np

dataset_path = 'kepanjangan/trial and error/Dataset'

image_paths = []
labels = []

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

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

print("Training Model...")

def train_lbph_model(model_filename='Saved_model.yaml'):
    face_list = []
    face_label_list = []
    train_face = 0
    total_detected_faces = 0

    for i, image_path in enumerate(train_images):
        full_image_path = train_image_paths[i]
        image = cv2.imread(full_image_path, cv2.IMREAD_GRAYSCALE)

        detected_faces = face_cascade.detectMultiScale(image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

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

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(face_list, np.array(face_label_list))

    # Save the LBPH model
    recognizer.save(model_filename)
    print(f"LBPH model saved as {model_filename}")

# TEST
def test_lbph_model(test_images, test_image_paths, classifier, model_filename, train_labels, test_labels):
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(model_filename)

    correct_predictions = 0
    total_faces = 0
    total_accuracy = 0
    total_detected_faces_test = 0
    test_face = 0

    for i, image_path in enumerate(test_images):
        image = cv2.imread(test_image_paths[i]) 
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 

        detected_faces = classifier.detectMultiScale(image_gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(detected_faces) >= 1:
            total_detected_faces_test += 1

        if len(detected_faces) < 1:
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
            cv2.putText(image, image_text, (x, y - 10), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0))

    cv2.destroyAllWindows()

    print("Done Testing!")

def evaluate_model_accuracy(test_images, test_image_paths, classifier, model_filename, true_labels):
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(model_filename)

    correct_predictions = 0
    total_faces = 0
    total_detected_faces_test = 0
    test_face = 0

    for i, image_path in enumerate(test_images):
        image = cv2.imread(test_image_paths[i]) 
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 

        detected_faces = classifier.detectMultiScale(image_gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(detected_faces) >= 1:
            total_detected_faces_test += 1

        if len(detected_faces) < 1:
            test_face += 1
            continue

        for face_rect in detected_faces:
            x, y, w, h = face_rect
            face_image_gray = cv2.resize(image_gray[y:y+h, x:x+w], (100, 100))

            result, confidence = recognizer.predict(face_image_gray)

            # Check if the result is within the valid range of true_labels
            if 0 <= result < len(true_labels):
                predicted_label = true_labels[result]
                true_label = true_labels[i]

                if predicted_label == true_label:
                    correct_predictions += 1

                total_faces += 1
            else:
                print("Error: Predicted label out of range")

    accuracy = (1 - (confidence / 300)) * 100
    print("Total detected faces in the test set:", total_detected_faces_test)
    print("Number of images without faces:", test_face)
    print("Overall Accuracy (using provided formula):", accuracy)

    
def detect_face(image_path):
    input_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    faces_in_image = face_cascade.detectMultiScale(input_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces_in_image) > 0:
        (x, y, w, h) = faces_in_image[0]
        face_roi = cv2.resize(input_image[y:y + h, x:x + w], (100, 100))
        return face_roi
    else:
        return None

def predict():
    model_filename = "Saved_model.yaml"

    if not os.path.exists(model_filename):
        print("Please train the model first.")
        return

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(model_filename)

    test_image_path = input("Input image path (absolute path) >> ")

    if not os.path.exists(test_image_path):
        print("Error: Image not found.")
        return

    input_image = cv2.imread(test_image_path)
    face = detect_face(test_image_path)

    if face is not None:
        predicted_label, confidence = recognizer.predict(face)
        accuracy = (1 - confidence / 300) * 100

        athletes = os.listdir("kepanjangan/Dataset/")
        predicted_athlete = athletes[predicted_label]

        x, y, w, h = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml').detectMultiScale(input_image)[0]
        cv2.rectangle(input_image, (x, y), (x+w, y+h), (0, 255, 0), 1)

        text = f"{predicted_athlete} : {accuracy:.2f}%"
        cv2.putText(input_image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

        cv2.imshow("Prediction Result", input_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("No face detected in the input image.")

def predict_all_images():
    model_filename = "Saved_model.yaml"

    if not os.path.exists(model_filename):
        print("Please train the model first.")
        return

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(model_filename)

    dataset_path = 'kepanjangan/trial and error/Dataset'

    athletes = os.listdir("kepanjangan/Dataset/")
    print("Number of athletes:", len(athletes))

    for athlete_folder in os.listdir(dataset_path):
        athlete_path = os.path.join(dataset_path, athlete_folder)

        for image_file in os.listdir(athlete_path):
            image_path = os.path.join(athlete_path, image_file)

            if not os.path.exists(image_path):
                print(f"Error: Image not found - {image_path}")
                continue

            input_image = cv2.imread(image_path)
            face = detect_face(image_path)

            if face is not None:
                predicted_label, confidence = recognizer.predict(face)
                accuracy = (1 - confidence / 300) * 100

                print("Predicted label:", predicted_label)
                if 0 <= predicted_label < len(athletes):
                    predicted_athlete = athletes[predicted_label]
                    print("Predicted athlete:", predicted_athlete)

                    x, y, w, h = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml').detectMultiScale(input_image)[0]
                    cv2.rectangle(input_image, (x, y), (x+w, y+h), (0, 255, 0), 1)

                    text = f"{predicted_athlete} : {accuracy:.2f}%"
                    cv2.putText(input_image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

                    cv2.imshow("Prediction Result", input_image)
                    cv2.waitKey(0)
                    cv2.destroyAllWindows()
                else:
                    print("Error: Predicted label out of range")

            else:
                print(f"No face detected in the input image - {image_path}")

# Call the predict_all_images function to predict all images in the dataset
# Example usage
train_lbph_model()
model_filename = 'Saved_model.yaml'
test_lbph_model(test_images, test_image_paths, face_cascade, model_filename, train_labels, test_labels)
evaluate_model_accuracy(test_images, test_image_paths, face_cascade, model_filename, test_labels)
# predict()
# predict_all_images()
