import asyncio
import face_recognition
from imutils import paths
import cv2
import os
import numpy as np
import pickle
import discord
import io
from picamera2 import Picamera2
import time
import RPi.GPIO as GPIO

# Load saved encodings
print("Loading encodings...")
with open("./encodings.pickle", "rb") as f:
    data = pickle.loads(f.read())
known_encodings = data["encodings"]
known_names = data["names"]
if not known_encodings:
    print("No known encodings loaded!")
    exit()

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# PIR Setup
GPIO.setmode(GPIO.BOARD)
pir = 11
GPIO.setup(pir, GPIO.IN)
time.sleep(2)  # Sensor initialization delay

# Global variable to track running facial recognition
facial_recognition_task = None

async def facial_recognition_loop(duration=30):
    # Access the pi camera
    try:
        picam2 = Picamera2()
        picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (1920, 1080)}))
        picam2.start()
        picam2.set_controls({"AeMeteringMode": 1, "AwbEnable": True, "ExposureTime": 20000, "AnalogueGain": 1.7})   #Tweak the controls to your specific lighting
    except RuntimeError as e:
        print(f"Failed to start camera: {e}")
        return

    seen = {name: True for name in known_names}
    unknown_encodings = []
    channel = client.get_channel(YOUR_CHANNEL_ID)  # Replace with your channel ID
    scaler = 5
    end_time = time.time() + duration
    # Runs the loop for duration seconds
    while time.time() < end_time:
        frame = picam2.capture_array()
        if frame is None:
            print("No more video stream")
            break
        # Flip the camera, comment if your camera is right side up, mine is upside down
        frame = cv2.flip(frame, -1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Scale the image down to make it easier for the pi to process
        scaled_rgb_frame = cv2.resize(rgb_frame, (0, 0), fx=(1/scaler), fy=(1/scaler))
        face_locations = face_recognition.face_locations(scaled_rgb_frame)
        face_encodings = face_recognition.face_encodings(scaled_rgb_frame, face_locations)

        # For each face detected compare it to known encodings
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.4)
            distances = face_recognition.face_distance(known_encodings, face_encoding)
            if len(distances) == 0:
                continue
            best_match_index = np.argmin(distances)

            #if a match was found to known_encodings send a message to discord and track their face
            if matches[best_match_index]:
                name = known_names[best_match_index]
                cv2.rectangle(frame, (left*scaler, top*scaler), (right*scaler, bottom*scaler), (0, 255, 0), 10)
                cv2.putText(frame, name, (left*scaler + 6, top*scaler - 6),
                            cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 0), 7)
                if seen.get(name):
                    _, buffer = cv2.imencode('.png', frame)
                    image_bytes = io.BytesIO(buffer.tobytes())
                    msg = f"Welcome home Supreme Leader." if name == "Audie" else f"{name} is home."
                    await channel.send(msg)
                    await channel.send(file=discord.File(image_bytes, filename="detected_person.png"))
                    seen[name] = False
            # If no match was found, treat it as unknown
            else:
                cv2.rectangle(frame, (left*scaler, top*scaler), (right*scaler, bottom*scaler), (0, 0, 255), 10)
                cv2.putText(frame, "Unknown", (left*scaler + 6, top*scaler - 6),
                            cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 0, 255), 7)
                if not unknown_encodings or face_recognition.face_distance(unknown_encodings, face_encoding).min() > 0.5:
                    unknown_encodings.append(face_encoding)
                    _, buffer = cv2.imencode('.png', frame)
                    image_bytes = io.BytesIO(buffer.tobytes())
                    await channel.send("Someone unknown is at the door.")
                    await channel.send(file=discord.File(image_bytes, filename="detected_person.png"))

        # Optional: uncomment for local testing
#         cv2.imshow('Facial Recognition', frame)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

        await asyncio.sleep(0.01)  # Yield control to event loop

    picam2.stop()
    picam2.close()

async def pir_watcher():
    global facial_recognition_task
    while True:
        if GPIO.input(pir):
            print("Motion detected.")
            if facial_recognition_task is None or facial_recognition_task.done():
                print("Starting facial recognition loop...")
                facial_recognition_task = asyncio.create_task(facial_recognition_loop(duration=30))
            await asyncio.sleep(2)  # Cooldown
        await asyncio.sleep(0.1)  # PIR polling

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    asyncio.create_task(pir_watcher())


if __name__ == "__main__":
    client.run("YOUR TOKEN HERE")
    