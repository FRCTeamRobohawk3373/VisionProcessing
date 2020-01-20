print("Importing")
from threading import Thread
import threading
import cv2
import numpy as np
##from networktables import NetworkTables
##import cscore as cs
import logging
import six.moves.urllib as urllib

import os
import time
import sys

from collections import defaultdict
from io import StringIO

from PIL import Image

import Processing
import Constants

class WebcamVideoStream:
	def __init__(self, src=0):
		# initialize the video camera stream and read the first frame
		# from the stream
		os.popen("v4l2-ctl -d "+str(src)+" -c exposure_auto=1")
		self.stream = cv2.VideoCapture(src)
		self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
		self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
		self.stream.set(cv2.CAP_PROP_EXPOSURE, .03)
		(self.grabbed, self.frame) = self.stream.read()
 
		# initialize the variable used to indicate if the thread should
		# be stopped
		self.stopped = False
		
	def start(self):
		# start the thread to read frames from the video stream
		Thread(target=self.update, args=()).start()
		return self
 
	def update(self):
		# keep looping infinitely until the thread is stopped
		while True:
			# if the thread indicator variable is set, stop the thread
			if self.stopped:
				return
 
			# otherwise, read the next frame from the stream
			(self.grabbed, self.frame) = self.stream.read()
 
	def read(self):
		# return the frame most recently read
		return self.grabbed,self.frame
 
	def release(self):
		# indicate that the thread should be stopped
		self.stopped = True

if __name__ == '__main__':
	# #Tape filtering
	# FILTER_MIN_AREA = 250
	# FILTER_MIN_PERIMETER = 80
	# FILTER_MIN_SOLIDITY = 75

	# #object definitions
	# TAPEKNOWNWIDTH= 8
	# CUBEKNOWNWIDTH=13
	# BUMPERKNOWNHEIGHT=5;

	# #camera definitions
	# CAM1FOCALLENGTH= 885
	# CAM2FOCALLENGTH= 885
	# CAM3FOCALLENGTH= 885
	# CAMFOCALLENGTH = 1000

	# FRONTCAMERANUM = 0
	# LEFTCAMERANUM = 1
	# RIGHTCAMERANUM = 2

	# TOLERANCEY = 50
	# CONFIDENCETHRESHOLD = 50

	# colors = [(0,0,255),(0,255,0),(255,255,0),(0,255,255),(255,0,255),(255,255,255)]


	frame=np.zeros((480,640,3),np.uint8)
	frame2=np.zeros((480,640,3),np.uint8)

	visionTape = [0]
	trackingObjects = [0]
	objects = []
			
				
	def set_res(cap, x,y):
		cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(x))
		cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(y))
		return cap.get(cv2.CAP_PROP_FRAME_WIDTH),cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

	logging.basicConfig(level=logging.DEBUG)
	print("starting cam")
	##cap1=PictureCapture(imagePaths,20)
	##cap1 = cv2.VideoCapture("Target.mov") 
	##cap1 = cv2.VideoCapture("distanceTest.mov") 	
	
	os.popen("v4l2-ctl -c exposure_auto=1")
	cap1 = cv2.VideoCapture(0) 
	set_res(cap1,1920,1080)
	
	cap1.set(cv2.CAP_PROP_EXPOSURE, .0150) 
	print(cap1.get(cv2.CAP_PROP_EXPOSURE))
	##print("reading cam")
	##ret, frame = cap1.read()    
	##print(ret)   
	    

	#cap1=WebcamVideoStream(0)
	#cap1.start()
	ret, frame = cap1.read() 
	
	vision = Processing.VisionThread(debug=False)
	
	vision.setCameraCharacteristics(Constants.camera1Matrix,Constants.camera1DistortionCoefficients)
	
	vision.run(frame)

	##NetworkTables.initialize(server='roborio-3373-frc.local')
	##sd = NetworkTables.getTable("VisionData")
	#cameraPre = NetworkTables.getTable("PreLoad")

	##cvSource = cs.CvSource("Camera1", cs.VideoMode.PixelFormat.kMJPEG, 1280, 480, 15)
	##cvMjpegServer = cs.MjpegServer("httpCamera1", port=5801)
	##cvMjpegServer.setSource(cvSource)

	##cs = NetworkTables.getDefault()
	##cs.getEntry("/CameraPublisher/Camera1/streams").setStringArray(["mjpeg:http://10.33.73.18:5801/?action=stream"])
	#cvSource2 = cs.CvSource("Camera2", cs.VideoMode.PixelFormat.kMJPEG, 320, 240, 15)
	#cvMjpegServer2 = cs.MjpegServer("httpCamera2", port=5802)
	#cvMjpegServer2.setSource(cvSource2)

	test = np.zeros(shape=(240, 640, 3), dtype=np.uint8)
	testFrame=np.zeros(shape=(480, 640, 3), dtype=np.uint8)
	count = 0
	#NetworkTables.initialize()
	#CAMFOCALLENGTH = CAM1FOCALLENGTH
	print("running")
	try:
		while(ret):
			ret,frame=cap1.read()
			#cs.getEntry("/CameraPublisher/PiCam/streams").setStringArray(["http://10.33.73.18:5801/?action=stream"])
			if ret==True:
				vision.processNewImage(frame)
				targets=vision.getTargets()
				
				fHeight,fWidth=frame.shape[:2]
				for target in targets:
					#print(target)
					if(not(target is None)):
						x=int((target[0]*(fWidth/2))+(fWidth/2))
						y=int((target[1]*(fHeight/2))+(fHeight/2))
						w=int(target[2])
						h=int(target[3])
						cv2.rectangle(frame,(x-int(w/2),y-int(h/2)),(x+int(w/2),y+int(h/2)),(200,0,255),2)
						
				cv2.imshow("frame",frame)
				key=cv2.waitKey(1) & 0xFF
				if key == ord('q'):
					break
			#else:
				#print("failed to get frame")

		print("stopping")
		vision.stop()
		
		cv2.destroyAllWindows()
		#NetworkTables.shutdown()
		
		cap1.release()
		#cap2.release()
	except KeyboardInterrupt:
		print('Interrupted')
		print("shutting down...")
		cv2.destroyAllWindows()
		vision.stop()
		#NetworkTables.shutdown()
		cap1.release()
		#cap2.release()
