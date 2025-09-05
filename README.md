# SentriCam
SentriCam is a Raspberry Pi based Motion Activated Facial Recognition Doorbell Camera that sends a message and image to a discord channel each time it sees a face using a discord bot. By training it to the faces of your family and friends it can recognize them and send a message such as "So and So is home" or if a stranger appears it sends a message "Someone Unknown is at the door".  
</br>
<img width="706" height="349" alt="image" src="https://github.com/user-attachments/assets/5f82ac64-2a83-439b-8e86-b81c4bbdf0d0" />

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

## Assembly
Assembly is really simple with only 4 main pieces of hardware to assemble. The code has uses pin 11 as GPIO for the PIR sensor. Read your PIR sensor's manual to connect your sensor's output pin to the pin 11. The connect the Pi Camera Module 3 via the ribbon cable. Mount everything appropriately on or in the enclosure. Then mount the entire thing as you see fit on your door or next to it. Mine kinda looks like a makeshift bomb because of the electrical tape but don't mind that.  
</br>
<img width="500" height="800" alt="image" src="https://github.com/user-attachments/assets/24d9d55a-af8e-4347-bef4-b989ff53f55d" />

## Set Up

After assembly, the first step is to make sure your pi is up to date using ``sudo apt update`` and ``sudo apt full-upgrade`` . Then open a virtual environment using ``python3 -m venv --system-site-packages virtual_environment_name``. Before downloading the libraries make sure to install Cmake using ``sudo apt install cmake``.  
Then download the following libraries:  
- discord
- opencv-python(opencv-python-headless if you plan on running it as a background process on your doorbell)
- imutils
- face-recognition

Notes for when installing libraries:  
- face-recognition can take a while when downloading do not be alarmed.
- picamera2 (library that is preinstalled with Raspberry Pis) does not like newer versions of numpy and I spent a while before figuring this out. I personally used numpy version 1.25.2 picamera2 seemed to like that.

From here there are two options for training your model. There are two scripts, one that allows for taking photos from your desktop using your webcam, and one that allows for taking photos from the Raspberry pi using the Pi Camera Module. Either way the ``model_encoding.py`` file works and after you finish taking your photos run the script to train the model. If your dataset contains a lot of different photos from the sheer amount you took or the amount of people in it, I highly recommend you do the model training on your desktop and then transfering the pickle file to your Pi. If you do it this way you must make sure the python version and the numpy version on your desktop when running the script are the same as the one you are running on your Pi. Otherwise the Pi cannot read the pickle files due to minute differences in the pickle file. The ``model_encoding.py`` file is preset to run on a desktop with plenty of cores. Edit the ```max_workers = 6``` line to use however many cores you're comfortable with running to encode the model. If you have no other option or are running a light dataset, feel free to take the images and train the model on the Pi. To do so you need to uncomment the sequential processing version and comment out the parallel process code block like so:
```
# with concurrent.futures.ProcessPoolExecutor(max_workers = 6) as executor:
    #     results = executor.map(process_image, dataset)
    #     for result in results:
    #         for encoding, name in result:
    #             known_encodings.append(encoding)
    #             known_names.append(name)
    # Sequential processing version for reference
    for i, filePath in enumerate(dataset):
        print(f"Processing {os.path.basename(filePath)} --- {i + 1}/{len(dataset)}")
        image = face_recognition.load_image_file(filePath)
        name = os.path.basename(os.path.dirname(filePath))
        faces = face_recognition.face_locations(image, model="cnn")
        encodings = face_recognition.face_encodings(image, faces)
        if not encodings:
            print(f"No face found in {os.path.basename(filePath)}")
            continue
        for encoding in encodings:
            known_encodings.append(encoding)
            known_names.append(name)
```
The Raspberry Pi doesn't like using the parallel processing as it breaks memory while running the python script which is why we have to do this depending on what you are training on.  
</br>
Now that you've trained your model, you must set up your discord bot. I did so by following the first 10 minutes or so of this video.  
[![Code a Discord Bot with Python - Host for Free in the Cloud](https://img.youtube.com/vi/SPTfmiYiuok/0.jpg)](https://www.youtube.com/watch?v=SPTfmiYiuok)
</br>
After setting up your discord bot, copy your discord key and insert it in the ```rbpi_facial_recognition.py``` file at line 130.  
```
if __name__ == "__main__":
    client.run("YOUR TOKEN HERE")
```
Then get the channel ID of the channel you want the notifications to go into. You can do this by going to discord -> user settings -> Advanced -> Enable Developer Mode. Once you've enabled developer mode you can right click on the channel you want to the notifiations to go into and copy the channel id.  
</br>
<img width="266" height="517" alt="image" src="https://github.com/user-attachments/assets/9ae07a6b-76a7-4187-ba7c-2970573bdb44" />
</br>
From here you're free to either run the ```rbpi_facial_recognition``` through Thonny on the Pi or have it run upon startup of your Pi. I personally set mine up through ssh to run upon startup using a service file. 

## Issues during development
Integrating the Computer vision to work with the discord bot was a headache. My initial set up essentially had the PIR activate the bot if it sensed anything but then I found out discord bots don't like being activated and then deactivated more than once in a script. I then altered the script to have the discord bot run once and have the PIR sensor work within the bot's activation code (the on_ready()). But then I learned again that the bot doesn't like the facial recognition loop running because during the loop the bot was essentially sitting idle without any updates causing the bot to shut itself down after 10 seconds of downtime. I tried a lot of unsucessful fixes before realizing I can just have the facial recognition loop have an asyncio time delay to essentially poll the discord bot every iteration in the loop keeping the bot active.   
</br>
My PIR sensor did not come with any instructions and the very basic ones I found on amazon where I bought it from seemed to be slightly incorrect. The setting the instructions were telling me to set it at had it at max sensitivity and detecting the slightest of heat from way past my patio. I had to trial and error before learning the instructions were wrong and that it was actually clockwise to decrease sensitivity on the PIR sensor. Basically these basic PIR sensors have 2 potentiometers that dictate sensitivity/range and delay. The range is self explanatory, with how far the sensor could detect infrared. The delay is how long the output writes a '1' after motion is detected. I set my range and delay to the smallest it would let me because my patio isn't that long and I don't want my program running for too long after motion is detected.  
</br>
The Pi Camera Module 3 to be frank isn't designed for outdoor use. It's autofocus is great but the autoexposure feature is what you expect for buying a tiny $25 camera. It struggles to account for the dark lighting in my shaded patio and after spending a day tinkering with the camera settings I found having a high analog gain was the best fix I could do. The problem with this is that the PIR sensor is a tad bit too sensitive even at the lowest setting so the sunlight reflecting off of leaves in the the wind activates it. In doing so, manually setting the gain to get a high exposure became a different problem since it distorted a distant tree enough for the model to detect it as a face. It also doesn't really work well at night, especially because I didn't want to spend more money on the NOiR model which is better at low light image capturing. You can see the visuals of the issues below.  
Default Camera settings not cutting it.
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/fc9ae9d3-11ad-4a57-8a6f-68048bdbe9b1" />
During midday the heat from the sun reflecting off the tree in front of my house trips off the PIR sensor + the brightness of midday + the high contract fix to see faces in my shaded patio distorts a "suspicious bush" just enough for the facial_recognition library to detect it as a face.
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/4cd4d010-41be-4ad7-8379-1b451480fbdd" />  
At night the basic Pi Camera Module 3 isn't the best at capturing faces.
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/577abddd-a9bb-4d23-a875-9daf227a1d85" />

## Areas for improvement
One area for improvement that's easily visible is the camera. I'm sure I could get somewhat better performance after researching more about the Pi Camera Module's settings. Alternatively I can buy a better camera. Arducam makes some pretty good options that are just outside of my budget for me, but if I really wanted to expand this project I could invest more money in one of their cameras.  
</br>
Another area for improvement is recognition. The program struggles to recognize faces at angles not seen in the dataset. I tried to account for this by taking photos for the dataset at most conventional angles such as looking left/right 45 degrees, up/down at 30 degrees, and tilting heads at 45 degrees. However as you can see below there are still angles where it can't recognize me.  
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/9f0b6bd1-a44c-42f7-a21a-40c44609831c" />
I can perhaps improve this by taking a lot more photos of different angles for everyone in my family. Alternatively I can also try using a more robust facial recognition library such as DeepFace or TensorFlow which is more likely to be able to recognize faces at awkward angles. 
