import face_recognition
from imutils import paths
import cv2
import os
import numpy as np
import pickle

# Load saved encodings
print("Loading encodings...")
with open("./encodings.pickle", "rb") as f:
    data = pickle.loads(f.read())
known_encodings = data["encodings"]
known_names = data["names"]

if not known_encodings:
    print("No known encodings loaded!")
    exit()

# Access the webcam
video_capture = cv2.VideoCapture(0)

while True:
    ret, frame = video_capture.read()

    if not ret:
        print("No more video stream")
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.4)
        # Compute the distance between the detected face and known faces
        distances = face_recognition.face_distance(known_encodings, face_encoding)
        if len(distances) == 0:
            print("No known faces to compare.")
            continue
        best_match_index = np.argmin(distances)

        if matches[best_match_index]:
            name = known_names[best_match_index]
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left + 6, top - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        else:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.putText(frame, "Unknown", (left + 6, top - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    cv2.imshow('Facial Recognition', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()