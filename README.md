# SentriCam
SentriCam is a Raspberry Pi based Motion Activated Facial Recognition Doorbell Camera

## Hardware
SentriCam uses a Raspberry Pi 5. I personally used the 4GB model. The project can work on a Pi 4 Model from my research (Expect worse performance of course) but I recommend a bare minimum of 4GB of RAM either way.  
</br>
A Pi Camera Module 3 is the camera used with picamera2 library built into the Raspberry Pi. For proof of concept I did also test it with a regular webcam which it works, there is a file called ``video_facial_recognition.py`` that you can use after training the model with your own faces.  
</br>
For motion detection I used a simple passive infrared sensor and used Raspberry Pi's GPIO library to interface it in my code.
![Picture of an off the shelf PIR sensor](https://github.com/user-attachments/assets/122cb739-9922-4bd4-be38-d010ee5dab9a)  
</br>
For the enclosure I bought a simple ABS plastic enclosure off of Amazon and drilled a few holes in them to mount the PIR sensor and Pi Camera Module.  
<img width="750" height="800" alt="image" src="https://github.com/user-attachments/assets/cf20fdb3-982e-48a8-a47b-5dcd3a3a35e3" />

## After Assembly

## Set Up

After assemb
