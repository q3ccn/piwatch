### Imports ###################################################################

from picamera.array import PiRGBArray
from picamera import PiCamera

import time
import cv2
import os
import pygame


### Setup #####################################################################

# Setup the camera
camera = PiCamera()
camera.resolution = ( 320, 240 )
camera.framerate = 32
camera.rotation =90
rawCapture = PiRGBArray( camera, size=( 320, 240 ) )

FCounter = 0

pygame.mixer.init()
pygame.mixer.music.load("Ooo.wav")


t_start = time.time()
t_play = 0
fps = 0

PREFRAME = None
PLAYMUSIC = False
SENSITIVE = 1000
PLAYLONG= 60
OUTPATH = '/tmp/face_stream/motion.jpg'

### Main ######################################################################

# Capture frames from the camera
for frame in camera.capture_continuous( rawCapture, format="bgr", use_video_port=True ):

    image = frame.array
  
    if FCounter % 4 == 3:

        FCounter = 0

        
        gray = cv2.cvtColor( image, cv2.COLOR_BGR2GRAY )
        gray_blur = cv2.GaussianBlur(gray, (21, 21), 0)      

        if PREFRAME is None:
            PREFRAME = gray_blur
        else:
            imgDelta = cv2.absdiff(PREFRAME,gray_blur)
            thresh = cv2.threshold(imgDelta,25,255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=2)
            _image, contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for c in contours:
                if cv2.contourArea(c) < SENSITIVE: # 设置敏感度
                    continue
                else:
                    #print(cv2.contourArea(c))
                   
                    PLAYMUSIC = True
                    #play Ooo.wav
                    if pygame.mixer.music.get_busy() != 1:
                        pygame.mixer.music.play()
                        t_play = time.time()

                    
                    #draw a rectangle
                    minx =  reduce(lambda x:x.min(),map(lambda x:x[:,:,0].min(),contours))
                    miny =  reduce(lambda x:x.min(),map(lambda x:x[:,:,1].min(),contours))
                    maxx =  reduce(lambda x:x.max(),map(lambda x:x[:,:,0].max(),contours))
                    maxy =  reduce(lambda x:x.max(),map(lambda x:x[:,:,1].max(),contours))

                    cv2.rectangle(image,(minx,miny),(maxx,maxy),(255,255,0),2)


                    break
            PREFRAME = gray_blur
    else:
        pass

    FCounter += 1

    #play Ooo.wav for 60 sec
    if pygame.mixer.music.get_busy() == 1 and time.time() - t_play  > PLAYLONG :
        PLAYMUSIC = False
        pygame.mixer.music.stop()
        t_play = 0



    # Calculate and show the FPS
    fps = fps + 1
    sfps = fps / ( time.time() - t_start )
    cv2.putText( image, "FPS : " + str( int( sfps ) ), ( 10, 10 ), cv2.FONT_HERSHEY_SIMPLEX, 0.5, ( 0, 0, 255 ), 2 )

    cv2.imwrite(OUTPATH, image )
 

    # Clear the stream in preparation for the next frame
    rawCapture.truncate( 0 )