print("Importing")
from threading import Thread
import threading
import cv2
import numpy as np
from networktables import NetworkTables
import cscore as cs
import logging
import six.moves.urllib as urllib
import tensorflow as tf
import os
import time
import sys

from collections import defaultdict
from io import StringIO

from PIL import Image


#Tape filtering
BLUR_RADIUS = 2
HSV_HUE = [61.510791366906474, 100.2]#Min,Max Hue
HSV_SAT = [36.690647482014384, 255.0]#Min,Max Sat
HSV_VALUE = [158.22841726618702, 255.0]#Min,Max Value

FILTER_MIN_AREA = 250
FILTER_MIN_PERIMETER = 80
FILTER_MIN_SOLIDITY = 75

#object definitions
TAPEKNOWNWIDTH= 8
CUBEKNOWNWIDTH=13
BUMPERKNOWNHEIGHT=5;

#camera definitions
CAM1FOCALLENGTH= 885
CAM2FOCALLENGTH= 885
CAM3FOCALLENGTH= 885
CAMFOCALLENGTH = 1000

FRONTCAMERANUM = 0
LEFTCAMERANUM = 1
RIGHTCAMERANUM = 2

TOLERANCEY = 50
CONFIDENCETHRESHOLD = 50

colors = [(0,0,255),(0,255,0),(255,255,0),(0,255,255),(255,0,255),(255,255,255)]

cap1 = cv2.VideoCapture(0)
cap2 = cv2.VideoCapture()
ret, camframe1 = cap1.read()
camframe2 = np.zeros((480,640,3),np.uint8)
ret2=False

frame1=np.zeros((480,640,3),np.uint8)
frame2=np.zeros((480,640,3),np.uint8)

loadedcamera1 = 0
loadedcamera2 = -1
loadedprecamera = -1

arrayLock = threading.Lock()

visionTape = [0]
trackingObjects = [0]
objects = []

class Threads:
    
    def thread1(self):
        global visionTape
        while(cap1.isOpened()):
            resized = np.copy(frame1) #cv2.resize(frame, (480, 320), 0, 0, cv2.INTER_CUBIC)
            fHeight,fWidth=resized.shape[:2]
            
            ksize = int(6 * round(BLUR_RADIUS) + 1)
            blur = cv2.GaussianBlur(resized, (ksize, ksize), round(BLUR_RADIUS))

            out = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
            HSV_out = cv2.inRange(out, (HSV_HUE[0], HSV_SAT[0], HSV_VALUE[0]),  (HSV_HUE[1], HSV_SAT[1], HSV_VALUE[1]))
            
            im2, contours, hierarchy = cv2.findContours(HSV_out, mode=cv2.RETR_LIST, method=cv2.CHAIN_APPROX_SIMPLE)

            output = []
            for contour in contours:
                x,y,w,h = cv2.boundingRect(contour)
                area = cv2.contourArea(contour)
                if (area < FILTER_MIN_AREA):
                    continue
                if (cv2.arcLength(contour, True) < FILTER_MIN_PERIMETER):
                    continue
                hull = cv2.convexHull(contour)
                solid = 100 * area / cv2.contourArea(hull)
                if (solid < FILTER_MIN_SOLIDITY):
                    continue
                output.append(contour)
                #debug
                cv2.rectangle(resized,(x,y),(w+x,h+y),(200,0,255),4)
                
            if(len(output)>0):
                bx,by,bx2,by2 = cv2.boundingRect(output[0])
                bx2+=bx
                by2+=by
                for contour in output:
                    x,y,w,h = cv2.boundingRect(contour)
                    if not(y<by-TOLERANCEY):
                        if(x<bx):
                            bx=x
                        if(y<by):
                            by=y
                        if(x+w>bx2):
                            bx2=x+w
                        if(y+h>by2):
                            by2=y+h
                bw=bx2-bx
                bh=by2-by
                #debug
                #cv2.rectangle(resized,(bx,by),(bx2,by2),(100,100,255),4)

                distance = (TAPEKNOWNWIDTH * CAM1FOCALLENGTH) / bw
                
                centerX = int(bw/2+bx)
                centerY = int(bh/2+by)

                #cv2.circle(resized,(centerX,centerY),2,(255,0,0))
                posx = (centerX-fWidth/2)/(fWidth/2)
                posy = (centerY-fHeight/2)/(fHeight/2)

                visionTape[0]=[3,95,posx,posy,distance]
            else:
                visionTape=[0]
                
                #cv2.putText(resized,str(distance),(10,30),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
                
                #cv2.putText(resized,str(posx),(10,60),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
                #cv2.putText(resized,str(posy),(10,90),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)

            #cv2.imshow('output',resized)
            #cv2.waitKey(10)
        
   
            

    
threads = Threads()
thread1 = Thread(target=threads.thread1)

thread1.start()
logging.basicConfig(level=logging.DEBUG)
NetworkTables.initialize(server='roborio-3373-frc.local')
sd = NetworkTables.getTable("VisionData")
#cameraPre = NetworkTables.getTable("PreLoad")

cvSource = cs.CvSource("Camera1", cs.VideoMode.PixelFormat.kMJPEG, 320, 240, 15)
cvMjpegServer = cs.MjpegServer("httpCamera1", port=5801)
cvMjpegServer.setSource(cvSource)

cs = NetworkTables.getDefault()
cs.getEntry("/CameraPublisher/PiCam/streams").setStringArray(["mjpeg:http://10.33.73.18:5801/?action=stream"])
#cvSource2 = cs.CvSource("Camera2", cs.VideoMode.PixelFormat.kMJPEG, 320, 240, 15)
#cvMjpegServer2 = cs.MjpegServer("httpCamera2", port=5802)
#cvMjpegServer2.setSource(cvSource2)

test = np.zeros(shape=(240, 640, 3), dtype=np.uint8)
count = 0
#NetworkTables.initialize()
CAMFOCALLENGTH = CAM1FOCALLENGTH
print("running")
if __name__ == '__main__':
    try:
        while(True):
            #cs.getEntry("/CameraPublisher/PiCam/streams").setStringArray(["http://10.33.73.18:5801/?action=stream"])
            tempcamchoice1=int(sd.getNumber("Camera1",loadedcamera1))
            tempcamchoice2=int(sd.getNumber("Camera2",loadedcamera2))
            tempprecam=int(sd.getNumber("Preload",loadedprecamera))
            #print()
            if(not(tempcamchoice1==loadedcamera1)):
                #try:
                    print("switchingcam1 to " + str(tempcamchoice1))
                    cap1.open(tempcamchoice1)
                    print("cam1Switched")
                    loadedcamera1 = tempcamchoice1
                #except:
                    #print("camera1 switch failed... trying again")
                    
            if(not(tempcamchoice2==loadedcamera2)):
                try:
                    print("switchingcam2 to " + str(tempcamchoice2))
                    cap2.open(tempcamchoice2)
                    print("cam2Switched")
                    loadedcamera2 = tempcamchoice2
                except:
                    print("camera2 switch failed... trying again")

            if(not(tempprecam==loadedprecamera)):
                try:
                    print("switchingcam2 to " + str(tempcamchoice2))
                    cap2.open(tempprecam)
                    print("cam2Switched")
                    loadedprecamera = tempprecam
                except:
                    print("camera2 switch failed... trying again") 

            try:
                if(loadedcamera1>=0):
                    if(cap1.isOpened):
                        ret, camframe1 = cap1.read()
                    else:
                        ret=False
                        print("Camera Not open")
                    if ret==False:
                        camframe1=np.zeros((480,640,3),np.uint8)
                else:
                    camframe1=np.zeros((480,640,3),np.uint8)
                    
            except:
                print("failed to get video from camera1")
                
            try:
                if(loadedcamera2>=0) or (loadedprecamera>=0):
                    ret2, camframe2 = cap2.read()
                    if ret2==False:
                        camframe2 = np.zeros((480,640,3),np.uint8) 
                else:
                    camframe2 = np.zeros((480,640,3),np.uint8)
            except:
                print("failed to get video from camera2")

            if(cap1.isOpened()):
                count=0
            else:
                #print("not Open")
                count+=1
                camframe1=np.zeros((480,640,3),np.uint8)
                if(count>1000):
                    count=0
                    loadedcamera1=-1
            
            if(cap2.isOpened()):
                count=0
            else:
                #print("not Open")
                count+=1
                camframe2 = np.zeros((480,640,3),np.uint8)
                if(count>750):
                    count=0
                    loadedcamera1=-1
                    
            if ret==True:
                if(loadedcamera1==FRONTCAMERANUM):
                    frame1=np.copy(camframe1)
                else:
                    frame1=np.zeros((480,640,3),np.uint8)
                    
                frame2=np.copy(camframe1)
                fheight,fwidth=frame2.shape[:2]
                count=0
##                for thing in objects:
##                    try:
##                        print(thing[2][1])
##                        tx = int((thing[2]+1)*(fwidth/2))
##                        ty = int((thing[3]+1)*(fheight/2))
##                        cv2.circle(camframe1,(tx,ty),2,colors[count],4)
##                        count+=1
##                    except:
##                        #print("error")
##                        continue
                h1,w1 = camframe1.shape[:2]
                h2,w2 = camframe2.shape[:2]
                img = np.zeros((max(h1,h2),w1+w2,3),np.uint8)
                img[:h1,:w1,:3] = camframe1
                img[:h1,w1:w1+w2,:3] = camframe2
                
                cvSource.putFrame(img)
                #cv2.imshow('Main',frame)
                objects = []
                arrayLock.acquire()
                #print(trackingObjects)
                if(trackingObjects!=[0]):
                    objects.extend(trackingObjects)
                    
                if(visionTape!=[0]):
                    objects.extend(visionTape)
                sd.putStringArray("Objects",objects)
                #print(objects)
                arrayLock.release()
                if cv2.waitKey(1) & 0xFF == ord('q'):
                     break
            #else:
                #print("failed to get frame")

        print("stopping")
        cv2.destroyAllWindows()
        NetworkTables.shutdown()
        cap1.release()
        cap2.release()
    except KeyboardInterrupt:
        print('Interrupted')
        print("shutting down...")
        cv2.destroyAllWindows()
        NetworkTables.shutdown()
        cap1.release()
        cap2.release()
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
