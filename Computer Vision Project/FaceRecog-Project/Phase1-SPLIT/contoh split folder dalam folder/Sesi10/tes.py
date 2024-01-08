import os
import numpy as np
import cv2

classifier = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

train_path = 'images/train'

classes = os.listdir(train_path)

# ['felix', 'jokowi', 'jonas', 'nayeon']
# 0 1 2 3

image_list = []
class_list = []
train_face = 0
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
        print("Train len = ",len(detected_faces))  
        if len(detected_faces) >= 1:  
            
            train_face += 1

        if len(detected_faces) < 1:
            continue

        for face_rect in detected_faces:
            x, y, w, h = face_rect
            cropped_image = image[y:y+h, x:x+w]
            image_list.append(cropped_image)
            class_list.append(i)
print("Train = ",train_face)

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.train(image_list, np.array(class_list))

test_path = 'images/test'
test_face = 0
for image_path in os.listdir(test_path):
    # print(f'{test_path}/{image_path}')
    full_image_path = f'{test_path}/{image_path}'

    image = cv2.imread(full_image_path)
    image_gray = cv2.imread(full_image_path, cv2.IMREAD_GRAYSCALE)

    detected_faces = classifier.detectMultiScale(image_gray, scaleFactor = 1.2, minNeighbors = 5)
    print("Test len = ",len(detected_faces))
    if len(detected_faces) >= 1:
        test_face += 1
        continue

    if len(detected_faces) < 1:
        continue

    for face_rect in detected_faces:
        x, y, w, h = face_rect
        face_image = image_gray[y:y+h, x:x+w]

        result, confidence = recognizer.predict(face_image)
        accuracy = (1-(confidence/300))*100

        cv2.rectangle(image, (x,y), (x + w, y + h), (0,255,0), 1)

        image_text = f'{classes[result]}: {accuracy}'
        cv2.putText(image, image_text, (x, y - 10), cv2.FONT_HERSHEY_PLAIN, 1.5, (0,255,0))
        # cv2.imshow('Result', image)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
print("test = ",test_face)


# print(image_list)
# print(class_list)
            





