print("Importing")
from threading import Thread
#import threading
import cv2
import numpy as np

from networktables import NetworkTables
import cscore as cs

import logging
import six.moves.urllib as urllib
import os
import time
import sys
import subprocess
import shlex

from collections import defaultdict
from io import StringIO

from PIL import Image

import Processing
import Constants

def set_res(cap, x,y):
	cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(x))
	cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(y))
	return cap.get(cv2.CAP_PROP_FRAME_WIDTH),cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

deviceNum=0

def camerainit(num):	
	subprocess.call(shlex.split("v4l2-ctl -d "+str(num)+" -c exposure_auto=3"))
	subprocess.call(shlex.split("v4l2-ctl -d "+str(num)+" -c exposure_auto=1"))
	subprocess.call(shlex.split("v4l2-ctl -d "+str(num)+" -c exposure_absolute=150"))
	#visionCam.set(cv2.CAP_PROP_EXPOSURE,.10)
	subprocess.call(shlex.split("v4l2-ctl -d "+str(num)+" -c saturation=255"))
	subprocess.call(shlex.split("v4l2-ctl -d "+str(num)+" -c white_balance_temperature_auto=0"))
	subprocess.call(shlex.split("v4l2-ctl -d "+str(num)+" -c white_balance_temperature=3277"))

visionCam = cv2.VideoCapture(deviceNum)
ret, camframe1 = visionCam.read()
camerainit(deviceNum)
ret, camframe1 = visionCam.read()

print(set_res(visionCam,1280,720))

ret, camframe1 = visionCam.read()

VisonCamera = 0

vision = Processing.VisionThread(debug=False)
vision.setCameraCharacteristics(Constants.camera2Matrix,Constants.camera2DistortionCoefficients)
if(ret):
	vision.run(camframe1)

logging.basicConfig(level=logging.DEBUG)
NetworkTables.initialize(server='roborio-3373-frc.local')
sd = NetworkTables.getTable("VisionData")
#cameraPre = NetworkTables.getTable("PreLoad")

cvSource = cs.CvSource("Vision Camera", cs.VideoMode.PixelFormat.kMJPEG, 480, 320, 10)
cvMjpegServer = cs.MjpegServer("httpCamera1", port=5801)
cvMjpegServer.setSource(cvSource)

csTable = NetworkTables.getDefault()
csTable.getEntry("/CameraPublisher/PiCam/streams").setStringArray(["mjpeg:http://10.33.73.20:5801/?action=stream"])
#cvSource2 = cs.CvSource("Camera2", cs.VideoMode.PixelFormat.kMJPEG, 320, 240, 15)
#cvMjpegServer2 = cs.MjpegServer("httpCamera2", port=5802)
#cvMjpegServer2.setSource(cvSource2)

cameras=[{"camera":visionCam,"stream":cvSource,"id":VisonCamera,"timeout":0}]

count = 0
#NetworkTables.initialize()

def switchCamera(camobject,deviceNum):
	#subprocess.call(shlex.split("v4l2-ctl -d "+str(deviceNum)+" -c exposure_auto=3"))
	#subprocess.call(shlex.split("v4l2-ctl -d "+str(deviceNum)+" -c exposure_absolute=150"))
	#subprocess.call(shlex.split("v4l2-ctl -d "+str(deviceNum)+" -c saturation=255"))
	#subprocess.call(shlex.split("v4l2-ctl -d "+str(deviceNum)+" -c white_balance_temperature_auto=0"))
	#subprocess.call(shlex.split("v4l2-ctl -d "+str(deviceNum)+" -c white_balance_temperature=3277"))
	try:
		camobject.open(deviceNum)
	except:
		return False
		
	print(set_res(camobject,640,480))
	return True
		
def setVisionCam(camObject):
	if(not(camObject["camera"].isOpened())):
		return False
		
	print(set_res(camObject["camera"],1280,720))
		
	subprocess.call(shlex.split("v4l2-ctl -d "+str(camObject[1])+" -c exposure_auto=3"))
	#subprocess.call(shlex.split("v4l2-ctl -d "+str(camObject[1])+" -c exposure_absolute=150"))
	subprocess.call(shlex.split("v4l2-ctl -d "+str(camObject[1])+" -c saturation=255"))
	subprocess.call(shlex.split("v4l2-ctl -d "+str(camObject[1])+" -c white_balance_temperature_auto=0"))
	subprocess.call(shlex.split("v4l2-ctl -d "+str(camObject[1])+" -c white_balance_temperature=3277"))
	
	VisonCamera=camObject["id"]
	
	

print("running")
if __name__ == '__main__':
	try:
		while(True):
			loopStart=time.time()
			#cs.getEntry("/CameraPublisher/PiCam/streams").setStringArray(["http://10.33.73.18:5801/?action=stream"])
			
			numOfCams=int(sd.getNumber("NumberOfCameras",1))
			#tempcamchoice2=int(sd.getNumber("Camera2",loadedcamera2))
			tempVisionCam=int(sd.getNumber("VisionCam",VisonCamera))
			
			text=sd.getString("text","")
			
			if(numOfCams<1):
				numOfCams=1
				sd.putNumber("NumberOfCameras",1)
			
			for i in range(numOfCams):
				camchoice=int(sd.getNumber("Camera"+str(i),-1))
				if(camchoice>=0):
					print("Cam"+str(i)+"change")
					if(i>=len(cameras)):
						try:
							cap=cv2.VideoCapture(camchoice)
							cvSourceCam=cs.CvSource("Vision Camera"+str(i), cs.VideoMode.PixelFormat.kMJPEG, 480, 320, 10)
							cvMjpegServer = cs.MjpegServer("httpCamera"+str(i), port=5801+i)
							cvMjpegServer.setSource(cvSource)
							csTable.getEntry("/CameraPublisher/PiCam/streams").setStringArray(["mjpeg:http://10.33.73.20:"+str(5801+i)+"/?action=stream"])
							cameras.append({"camera":cap,"stream":cvSource,"id":camchoice,"timeout":0})
						except:
							print("Failed to open "+str(camchoice))
							sd.putNumber("NumberOfCameras",i)
						else:
							cvSource = cs.CvSource("Vision Camera"+str(), cs.VideoMode.PixelFormat.kMJPEG, 480, 320, 10)
							cvMjpegServer = cs.MjpegServer("httpCamera"+str(), port=5801)
							cvMjpegServer.setSource(cvSource)

					else:
						if(not(cameras[i]["id"]==camchoice) and cameras[i]["timeout"]==0):
							for cam in cameras:
								if(cam["id"]==camchoice):
									sd.putNumber("Camera"+str(i),cameras[i]["id"])
									continue
									
							if(switchCamera(cameras[i]["camera"],camchoice)):
								cameras[i]["id"]=camchoice
								print("switched Camera")
							else:
								print("Error Switching Camera")	
								cameras[i][2]=100
							if(cameras[i][2]>0):
								cameras[i][2]-=1
								
			if(numOfCams<len(cameras)):
				cam=cameras[len(cameras)-1]
				if(cam["id"]==VisonCamera):
					setVisionCam(cameras[len(cameras)-2])
				try:
					cam["camera"].release()
				except:
					pass
				finally:
					cameras.pop()
				
			for cam in cameras:
				ret,frame = cam["camera"].read()
				if(ret):
					if(cam["id"]==VisonCamera):
						vision.processNewImage(frame)
						targets=vision.getTargets()
						sd.putStringArray("Objects",targets)
						
						#print(targets)
						fHeight,fWidth=frame.shape[:2]
						for target in targets:
							#print(target)
							if(not(target is None)):
								x=int((target[0]*(fWidth/2))+(fWidth/2))
								y=int((target[1]*(fHeight/2))+(fHeight/2))
								w=int(target[2])
								h=int(target[3])

								cv2.rectangle(frame,(x-int(w/2),y-int(h/2)),(x+int(w/2),y+int(h/2)),(200,0,255),2)
						
						#cv2.imshow('Main',frame)
						frame=cv2.resize(frame,(480, 320),interpolation=cv2.INTER_NEAREST)
						cam["stream"].putFrame(frame)
						
					else:
						cam["stream"].putFrame(frame)
						#cv2.imshow("Camera")
				else:
					cam["camera"].release()
					cameras.remove(cam)
					
			if cv2.waitKey(1) & 0xFF == ord('q'):
				break			
			if(len(cameras)==0):
				print("No Cameras")
				break;	
				#print(str((time.time()-loopStart)*1000)+"ms")
			#else:
				#print("failed to get frame")

		print("stopping")
		cv2.destroyAllWindows()
		for cam in cameras:
			cam["camera"].release()
			
		NetworkTables.shutdown()
		vision.stop()
		
	except KeyboardInterrupt:
		print('Interrupted')
		print("shutting down...")
		cv2.destroyAllWindows()
		for cam in cameras:
			cam["camera"].release()
			
		NetworkTables.shutdown()
		vision.stop()
		try:
			sys.exit(0)
		except SystemExit:
			os._exit(0)
