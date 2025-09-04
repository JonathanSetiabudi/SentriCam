import cv2
import os
import datetime

def create_folder(name):
    dataset_folder = "dataset"
    if not os.path.exists(dataset_folder):
        os.makedirs(dataset_folder)

    person_folder = os.path.join(dataset_folder, name)
    if not os.path.exists(person_folder):
        os.makedirs(person_folder)
    return person_folder

PERSON_NAME = input("Enter the name of the person you're photographing: ")

stream = cv2.VideoCapture(0)

if not stream.isOpened():
    print("Cannot open camera")
    exit()

fps = stream.get(cv2.CAP_PROP_FPS)
width = int(stream.get(3))
height = int(stream.get(4))

folder = create_folder(PERSON_NAME)
photo_count = 0

while (True):
    ret, frame = stream.read()
    if not ret:
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

stream.release()
cv2.destroyAllWindows()
print(f"Photo capture completed. {photo_count} photos saved for {PERSON_NAME}.")