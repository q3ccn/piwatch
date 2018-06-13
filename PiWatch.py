# -*- coding: utf-8 -*-
### Imports ###################################################################

import time
import cv2
import urllib2
import numpy as np
import pygame


### Setup #####################################################################

CAMURL = 'http://localhost:8080?action=stream'


def detect_motion():    
    cap = cv2.VideoCapture()
    fCounter = 0
    playLong = 60
    pygame.mixer.init()
    pygame.mixer.music.load("/home/pi/piwatch/Ooo.wav")
    sensitive = 10000
    preFrame = 0
   
    t_play = 0
    imgBytes = ''    

    stream=urllib2.urlopen(CAMURL)

    while True:
        # Capture frames from the camera

        imgBytes += stream.read(1024)
        a = imgBytes.find('\xff\xd8')
        b = imgBytes.find('\xff\xd9')
        if a!=-1 and b!=-1:
            imgRaw = imgBytes[a:b+2]
            imgBytes= imgBytes[b+2:]
            #flags = 1 for color image
            image = cv2.imdecode(np.fromstring(imgRaw, dtype=np.uint8),flags=1)
                
            if fCounter % 4 == 3:

                fCounter = 0

                gray = cv2.cvtColor( image, cv2.COLOR_BGR2GRAY )
                gray_blur = cv2.GaussianBlur(gray, (21, 21), 0)      

                if preFrame is None:
                    preFrame = gray_blur
                else:
                    imgDelta = cv2.absdiff(preFrame,gray_blur)                   
                    thresh = cv2.threshold(imgDelta,25,255, cv2.THRESH_BINARY)[1]
                    thresh = cv2.dilate(thresh, None, iterations=2)
                    
                    contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    print 'hello' ,time.time()             
              

                    if len(contours) > 0 :
                        if  reduce(lambda x,y:x+y,map(lambda x:cv2.contourArea(x),contours)) <  sensitive: # 设置敏感度
                            print 'less'                        
                        else:
                            #print(cv2.contourArea(c))
                            print 'more'                       
                            #play Ooo.wav
                            if pygame.mixer.music.get_busy() != 1:
                                pygame.mixer.music.play(loops=3)
                                t_play = time.time()                
                                            
                    preFrame = gray_blur
            else:
                pass

            fCounter += 1

            #stop Ooo.wav after {playLong} sec
            if pygame.mixer.music.get_busy() == 1 and time.time() - t_play  > playLong :       
                pygame.mixer.music.stop()
                t_play = 0       

if __name__ == '__main__':
    detect_motion()