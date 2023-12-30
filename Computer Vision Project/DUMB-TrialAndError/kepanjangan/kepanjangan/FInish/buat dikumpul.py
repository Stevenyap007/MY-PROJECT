import os
import cv2
from sklearn.model_selection import train_test_split
import numpy as np

dataset_path = 'kepanjangan\Dataset'

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

train_images = [cv2.imread(path) for path in train_image_paths]
test_images = [cv2.imread(path) for path in test_image_paths]

classifier = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


def train_lbph_model(model_filename='Saved_model.yaml'):
    print("Training Model...")
# TRAIN
    face_list = []
    face_label_list = []
    train_face = 0
    total_detected_faces = 0

    for i, image_path in enumerate(train_images):
        full_image_path = train_image_paths[i]
        image = cv2.imread(full_image_path, cv2.IMREAD_GRAYSCALE)

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

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(face_list, np.array(face_label_list))

    # Save the LBPH model
    model_filename = 'Saved_model.yaml'
    recognizer.save(model_filename)
    print(f"LBPH model saved as {model_filename}")

# TEST

def test_lbph_model(test_images, test_image_paths, classifier, model_filename, train_labels, test_labels):
    # Load the LBPH model
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
            total_accuracy += accuracy
            cv2.putText(image, image_text, (x, y - 10), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0))

        # Uncomment to visualize the detected faces and recognition results
        # cv2.imshow('Result', image)
        # cv2.waitKey(0)
    cv2.destroyAllWindows()

    print("Total detected faces in the testing set:", total_detected_faces_test)
    print("Number of images without faces testing:", test_face)
    accuracy_percentage = (correct_predictions / total_faces) * 100
    print(f"Model Accuracy: {accuracy_percentage}%")
    print("akurasi manual {:.2f}%".format(total_accuracy/total_detected_faces_test))
    input("Press enter to continue...")



def predict_from_terminal(classifier, model_filename, train_labels):
    # Load the LBPH model
    recognizer = cv2.face.LBPHFaceRecognizer_create()

    try:
        recognizer.read(model_filename)
    except cv2.error:
        print(f"Error: Could not load the model from {model_filename}. Please train the model first.")
        return

    # Ask the user to input the image path
    input_image_path = input("Input image path (absolute path) >> ")

    # Read the input image
    input_image = cv2.imread(input_image_path)

    if input_image is None:
        print(f"Error: Could not read the image from {input_image_path}. Make sure the path is correct.")
        return

    input_image_gray = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)

    # Detect faces in the input image
    detected_faces = classifier.detectMultiScale(input_image_gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    for face_rect in detected_faces:
        x, y, w, h = face_rect
        face_image_gray = cv2.resize(input_image_gray[y:y+h, x:x+w], (100, 100))

        # Predict the face using the loaded model
        result, confidence = recognizer.predict(face_image_gray)
        accuracy = (1 - (confidence / 300)) * 100

        # Get the predicted label and display it on the image
        predicted_label = train_labels[result]
        image_text = f'{predicted_label}: {accuracy:.2f}%'
        print(f"Player: {predicted_label}, Accuracy: {accuracy:.2f}%")
        cv2.rectangle(input_image, (x, y), (x + w, y + h), (0, 255, 0), 1)
        cv2.putText(input_image, image_text, (x, y - 10), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0))

    # Show the prediction result
    cv2.imshow('Prediction Result', input_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def main():
    model_filename = 'Saved_model.yaml'
    model_exists = os.path.exists(model_filename)

    choice = 0
    while choice != 3:
        print("\nVaskeTball Player Face Detection")
        print("1. Train and test model")
        print("2. Predict")
        print("3. Exit")
        choice = int(input("Choose your option >> "))

        if choice == 1:
            train_lbph_model(model_filename)
            model_exists = os.path.exists(model_filename)
            test_lbph_model(test_images, test_image_paths, classifier, model_filename, train_labels, test_labels)
        elif choice == 2:
            if not model_exists:
                print("Please train the model first.")
            else:
                predict_from_terminal(classifier, model_filename, train_labels)
        elif choice == 3:
            break

if __name__ == "__main__":
    main()