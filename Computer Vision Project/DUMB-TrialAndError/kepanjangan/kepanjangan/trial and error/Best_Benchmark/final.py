import cv2
import os
import numpy as np
from sklearn.model_selection import train_test_split

def preprocess_image(image):
    # CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    clahe_image = clahe.apply(image)

    # Equalize
    equalized_image = cv2.equalizeHist(clahe_image)

    return equalized_image

def extract_faces_and_labels(dataset_path):
    faces = []
    labels = []

    subfolders = [f.path for f in os.scandir(dataset_path) if f.is_dir()]

    for subfolder in subfolders:
        label = os.path.basename(subfolder)

        # Get list of image files in each subfolder
        image_files = [f for f in os.listdir(subfolder) if f.endswith(('.jpg', '.jpeg', '.png'))]

        for image_file in image_files:
            image_path = os.path.join(subfolder, image_file)

            # Read and preprocess the image
            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            preprocessed_image = preprocess_image(image)

            # Detect faces
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces_in_image = face_cascade.detectMultiScale(preprocessed_image, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))

            for (x, y, w, h) in faces_in_image:
                face_roi = preprocessed_image[y:y + h, x:x + w]
                faces.append(face_roi)
                labels.append(label)

    return faces, labels

def train_model(x_train, y_train):
    # Convert labels to numerical values
    label_set = set(y_train)
    label_dict = {label: i for i, label in enumerate(label_set)}
    y_train_encoded = [label_dict[label] for label in y_train]

    # Split dataset into training (70%) and testing (30%)
    x_train, x_test, y_train, y_test = train_test_split(x_train, y_train_encoded, test_size=0.2, random_state=42)

    # Train LBPH model
    lbph_model = cv2.face.LBPHFaceRecognizer_create()
    lbph_model.train(x_train, np.array(y_train))

    return lbph_model, x_test

def evaluate_model(model, x_test):
    predictions = []
    confidence_values = []

    for test_face in x_test:
        label, confidence = model.predict(test_face)
        predictions.append(label)
        confidence_values.append(confidence)

    # Calculate accuracy using confidence values
    confidence_values = np.array(confidence_values)
    confidence_accuracy = (1 - (confidence_values / 300)) * 100
    overall_accuracy = np.mean(confidence_accuracy)

    return overall_accuracy

def train():
    print("Training Model...")
    dataset_path = 'kepanjangan/Dataset'
    faces, labels = extract_faces_and_labels(dataset_path)

    # Split dataset into training (70%) and testing (30%)
    x_train, _, y_train, _ = train_test_split(faces, labels, test_size=0.2, random_state=42)

    print("Number of training samples:", len(x_train))

    # Train the LBPH model and get the testing set
    lbph_model, x_test = train_model(x_train, y_train)

    # Evaluate the model on the testing set
    accuracy = evaluate_model(lbph_model, x_test)

    # Save the trained model
    model_filename = "Saved_model.yml"
    lbph_model.save(model_filename)

    # Print accuracy
    print("Done Training!")
    print(f"Model Accuracy: {accuracy:.2f}%")
    input("Press enter to continue...")

def detect_face(image_path):
    # Read the input image
    input_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Detect faces in the input image
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces_in_image = face_cascade.detectMultiScale(input_image, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))

    if len(faces_in_image) > 0:
        (x, y, w, h) = faces_in_image[0]
        face_roi = input_image[y:y + h, x:x + w]
        return face_roi
    else:
        return None

def predict():
    model_filename = "Saved_model.yml"

    if not os.path.exists(model_filename):
        print("Please train the model first.")
        return

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(model_filename)

    test_image_path = input("Input image path (absolute path) >> ")

    if not os.path.exists(test_image_path):
        print("Error: Image not found.")
        return

    # Read the input image
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

def main():
    choice = 0
    while choice != 3:
        print("VaskeTball Player Face Detection")
        print("1. Train and test model")
        print("2. Predict")
        print("3. Exit")
        choice = int(input("Choose your option >> "))

        if choice == 1:
            train()
        elif choice == 2:
            predict()
        elif choice == 3:
            break

if __name__ == "__main__":
    main()