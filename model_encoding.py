import face_recognition
from imutils import paths
import cv2
import os
import numpy as np
import pickle
import concurrent.futures

def process_image(filePath):
    print(f"Processing {os.path.basename(filePath)}")
    image = face_recognition.load_image_file(filePath)
    name = os.path.basename(os.path.dirname(filePath))
    faces = face_recognition.face_locations(image, model="cnn")
    encodings = face_recognition.face_encodings(image, faces)
    if not encodings:
        print(f"No face found in {os.path.basename(filePath)}")
        return
    return [(encoding,name) for encoding in encodings]

if __name__ == "__main__":
    # Load reference images
    dataset = list(paths.list_images("dataset"))
    known_encodings = []
    known_names = []

    with concurrent.futures.ProcessPoolExecutor(max_workers = 6) as executor:
        results = executor.map(process_image, dataset)
        for result in results:
            for encoding, name in result:
                known_encodings.append(encoding)
                known_names.append(name)
    # Sequential processing version for reference
    # for i, filePath in enumerate(dataset):
    #     print(f"Processing {os.path.basename(filePath)} --- {i + 1}/{len(dataset)}")
    #     image = face_recognition.load_image_file(filePath)
    #     name = os.path.basename(os.path.dirname(filePath))
    #     faces = face_recognition.face_locations(image, model="cnn")
    #     encodings = face_recognition.face_encodings(image, faces)
    #     if not encodings:
    #         print(f"No face found in {os.path.basename(filePath)}")
    #         continue
    #     for encoding in encodings:
    #         known_encodings.append(encoding)
    #         known_names.append(name)

    # Save the encodings and names to a pickle file
    print("Saving Encodings...")
    model = {"encodings": known_encodings, "names": known_names}
    with open("encodings.pickle", "wb") as f:
        pickle.dump(model, f)
    print("Encodings saved to 'encodings.pickle'")