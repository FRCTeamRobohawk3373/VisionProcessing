import cv2
import numpy as np
import threading
from threading import Thread
import Constants
import time
import datetime
from multiprocessing import Process
import math


class VisionThread:
	def __init__(self, debug=False):
		self.arrayLock = threading.Lock()
		self.thread = Thread(target=self.process)
		#self.thread = Process(target=self.process, args=(self,))
		self.thread.daemon=True
		self.running = False
		self.img=None
		self.newImageAvailable=False
		self.debug=debug
		self.finalTargets=[None]
		self.cameraMatrix=None
		self.distortionCoefficients=None
		pass
	def setCameraCharacteristics(self,cameraMatrix,distortionCoefficients):
		self.cameraMatrix=cameraMatrix
		self.distortionCoefficients=distortionCoefficients
		
	def run(self, firstImage):
		self.img = firstImage
		self.running=True
		self.thread.start()
		
	def stop(self):
		self.running=False
		cv2.destroyAllWindows() 
		self.thread.join(10)
		
	def processNewImage(self, img):
		self.img=np.copy(img)
		self.newImageAvailable=True
		
	def getTargets(self):
		return self.finalTargets
		
		
	def process(self):
		width3d=Constants.targetWidth #14.62677
		height3d=Constants.targetHeight#5.825591
		rectCorners3d=np.array([
			[-width3d/2, -height3d/2, 0.0],	# top-left
			[width3d/2, -height3d/2, 0.0],	# top-right
			[width3d/2, height3d/2, 0.0],	# bottom-right
			[-width3d/2, height3d/2, 0.0]	# bottom-left
		])
		##intrinsic_parameters=np.array([
		##[1.45631289e+03, 0.00000000e+00, 9.59733424e+02],
		##[0.00000000e+00, 1.46236722e+03, 5.23444394e+02],
		##[0.00000000e+00, 0.00000000e+00, 1.00000000e+00]
		##])
		##distortion_coefficients=np.array([ 0.06717082, -0.26083562, -0.0014863,  -0.00031783,  0.24629886])
		
		while(self.running):
			if(self.newImageAvailable):
				loopStartTime=time.time()
				processImg=np.copy(self.img)
				fHeight,fWidth=processImg.shape[:2]
				
				###################################################
				##  Change to draw box around this years target  ##
				###################################################
				blur = cv2.medianBlur(processImg, Constants.BLUR_SIZE)
				
				HSVout = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
				HSVout = cv2.inRange(HSVout, (Constants.HSV_THRESHHOLD_HUE[0], Constants.HSV_THRESHHOLD_SAT[0], Constants.HSV_THRESHHOLD_VALUE[0]),
					(Constants.HSV_THRESHHOLD_HUE[1], Constants.HSV_THRESHHOLD_SAT[1], Constants.HSV_THRESHHOLD_VALUE[1]))
				
				HSVout=cv2.erode(HSVout, None, iterations=Constants.ERODE_ITERATIONS, borderType=Constants.ERODE_BORDERTYPE)
				
				
				im2, contours, hierarchy = cv2.findContours(HSVout, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)
				
				if(self.debug):
					cv2.imshow("preprocessed",im2)
				
				output = []
				for contour in contours:# filtering contours base on area, perimeter,and solidity
					x,y,w,h = cv2.boundingRect(contour)
					area = cv2.contourArea(contour)
					if (area < Constants.FILTER_MIN_AREA): #Filters out anything that is too small by area
						continue
					if (cv2.arcLength(contour, True) < Constants.FILTER_MIN_PERIMETER): #Filters out anything that is too small by perimeter
						continue
					hull = cv2.convexHull(contour)
					solid = 100 * area / cv2.contourArea(hull)
					if (solid < Constants.FILTER_MIN_SOLIDITY):#Filters out anything that is not filled in enough
						continue
					output.append(contour)
					
				###################################################
				##   Change to group targets this years target   ##
				###################################################
				targets=[]
##				rawTargets=[]
				length = len(output)
				for contour in output: # group left and right angled targets
					rect1=cv2.minAreaRect(contour)
					if(rect1[2]<-45):#target to the left
						rect1Pos=rect1[0][0]
						closestTarget = None
						closest=None
						for contour2 in output:
							rect2=cv2.minAreaRect(contour2)
							if(rect2[2]>-45):#target to the right
								if(rect2[0][0]>rect1Pos):
									if(closest is None):
										closestTarget=contour2
										closest=rect2
									elif(rect2[0][0]<closest[0][0]):
										closestTarget=contour2
										closest=rect2
										
##						rawTargets.append([rect1,closest,contour,closestTarget])	
##								
##				for x,obj in enumerate(rawTargets):
##					#if(abs(rect2[0][0]-rect1[0][0])/abs(rect2[0][1]-rect1[0][1])<10000):
##					print(str(obj[1][0][0])
##					for i,obj2 in enumerate(rawTargets):
##						if(not(x==i)):
##							if(obj[3] is obj2[3]):
##								print(str(x)+" at "+str(obj[1])+" matches "+str(i)+" at "+str(obj2[1]))
##								#print(str(obj[1][0][0])+" matches "+str(obj2[1][0][0]))
##								if(obj[1][0][0]>obj2[1][0][0]):
##									print(str(x)+" is greater than "+str(i))
##						
##				for	target in rawTargets:	
##						rect1,closest,contour,closestTarget=target			
						#print(cv2.boundingRect(contour));				
						if(closestTarget is not None): # Generates and oganizes all useful data from contours
							if(self.debug):
								targetGroup={"left":rect1,"right":closest}
							else:
								targetGroup={}
							x1,y1,w1,h1=cv2.boundingRect(contour);
							x2,y2,w2,h2=cv2.boundingRect(closestTarget)
							topY=0
							if(y1<y2):
								topY=y1
							else:
								topY=y2
								
							bottomY=0
							if(y1+h1>y2+h2):
								bottomY=y1+h1
							else:
								bottomY=y2+h2
								
							targetGroup["center"]=((x1+x2+w2)/2,(bottomY+topY)/2)
							targetGroup["size"]=(x2+w2-x1,bottomY-topY)
							
							w,h=targetGroup["size"]
							x,y=targetGroup["center"]
							
							#######################################################
							## Distance and Rotation Calculations, DO NOT CHANGE ##
							#######################################################
							
							rectCorners2d=np.array([
								(x-w/2, y-h/2),	# top-left
								(x+w/2, y-h/2),	# top-right
								(x+w/2, y+h/2),	# bottom-right
								(x-w/2, y+h/2)	# bottom-left
							])
							
							retval, rvec, tvec=cv2.solvePnP(rectCorners3d, rectCorners2d, self.cameraMatrix, self.distortionCoefficients)
							
							targetGroup["distance"]=tvec[2][0]
							targetGroup["rotation"]=math.degrees(rvec[1])*1.3
							
							targets.append(targetGroup)
							
				if(self.debug):	
					for group in targets:
						box = cv2.boxPoints(group["left"])
						box = np.int0(box)
						cv2.drawContours(processImg,[box],0,(0,255,0),2)
						box = cv2.boxPoints(group["right"])
						box = np.int0(box)
						cv2.drawContours(processImg,[box],0,(0,0,255),2)
						cv2.circle(processImg,(int(group["center"][0]),int(group["center"][1])),2,(0,255,255))
						leftPt=(int(group["center"][0]-group["size"][0]/2),int(group["center"][1]-group["size"][1]/2))
						rightPt=(int(group["center"][0]+group["size"][0]/2),int(group["center"][1]+group["size"][1]/2))
						cv2.rectangle(processImg,leftPt,rightPt,(200,0,255),2)
						
						left=group["left"][1]
						right=group["right"][1]
						if(left[0]>left[1]):
							left=(left[1],left[0])
						if(right[0]>right[1]):
							right=(right[1],right[0])
							
						#distance=(8865.45/(group["size"][1]+7.34651))-2.22347
						#distance=(8339.96/(group["size"][1]+4.04455))-0.58572
						cv2.putText(processImg,str(group["distance"]),(int(group["center"][0]-20),int(group["center"][1]-50)),cv2.FONT_HERSHEY_DUPLEX,1,(255,0,255))
						cv2.putText(processImg,str(group["rotation"]),(int(group["center"][0]-20),int(group["center"][1]-100)),cv2.FONT_HERSHEY_DUPLEX,1,(255,0,255))
						cv2.putText(processImg,"X: " + str((group["center"][0]-fWidth/2)/(fWidth/2)),(int(group["center"][0]-100),int(group["center"][1]-150)),cv2.FONT_HERSHEY_DUPLEX,1,(255,0,255))
						#print("left: "+str(left[0])+" right: "+str(right[0]))
						print("X: " + str((group["center"][0]-fWidth/2)/(fWidth/2))+" Y:"+str((group["center"][1]-fHeight/2)/(fHeight/2)))
						#print(cv2.boundingRect(cv2.boxPoints(group["left"])))
					cv2.putText(processImg,str((time.time()-loopStartTime)*1000)+"ms",(10,20),cv2.FONT_HERSHEY_DUPLEX,1,(255,0,0))
					#print("ran "+str((time.time()-loopStartTime)*1000)+"ms")
					cv2.imshow("processed",processImg)
					cv2.waitKey(1)
				
				
				
				self.finalTargets=[None]
				for i,target in enumerate(targets):
					w,h=target["size"]
					x,y=target["center"]
					distance=target["distance"]
					rotation=target["rotation"]
					
					posx=(x-fWidth/2)/(fWidth/2)
					posy=(y-fHeight/2)/(fHeight/2)
					
					if(i==0):
						self.finalTargets[i]=[round(posx,4),round(posy,4),round(w,4),round(h,4),round(distance,4),round(rotation,4)]
					else:
						self.finalTargets.append([round(posx,4),round(posy,4),round(w,4),round(h,4),round(distance,4),round(rotation,4)])
				
				
				if((time.time()-loopStartTime)*1000>=100):
					print("["+datetime.datetime.now().strftime("%I:%M:%S.%s")+"] WARNING: processing loop took longer than 100ms("+str((time.time()-loopStartTime)*1000)+"ms).")
				
					
				self.newImageAvailable=False
				
			#else:
				#cv2.waitKey(1)#lockup prevention
				
				
				
				
				
				
				
				
				
				
