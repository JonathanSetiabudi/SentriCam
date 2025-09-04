import cv2
import os
import datetime
from picamera2 import Picamera2
import time

def create_folder(name):
    dataset_folder = "dataset"
    if not os.path.exists(dataset_folder):
        os.makedirs(dataset_folder)

    person_folder = os.path.join(dataset_folder, name)
    if not os.path.exists(person_folder):
        os.makedirs(person_folder)
    return person_folder

PERSON_NAME = input("Enter the name of the person you're photographing: ")

# Initialize camera
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picam2.start()

time.sleep(2)

folder = create_folder(PERSON_NAME)
photo_count = 0

print(f"Taking photos for {PERSON_NAME}. Press SPACE to capture, 'q' to quit.")

while (True):
    frame = picam2.capture_array()
    if frame is None:
        print("No more stream")
        break
    cv2.imshow("Capture", frame)

    key = cv2.waitKey(1) & 0xFF
    
    if key == ord(' '):
        file_name = f"{PERSON_NAME}_{datetime.datetime.now().strftime('%Y_%m_%d__%H_%M_%S')}"
        cv2.imwrite(os.path.join(folder, f"{file_name}.jpg"), frame)
        photo_count += 1
        print(f"Photo {photo_count} saved: {file_name}.jpg")
    if key == ord('q'):
        break

cv2.destroyAllWindows()
picam2.stop()
print(f"Photo capture completed. {photo_count} photos saved for {PERSON_NAME}.")