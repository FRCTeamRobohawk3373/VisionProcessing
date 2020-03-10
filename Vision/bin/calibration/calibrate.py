import numpy as np
import cv2
import glob
import time
import os


CHECKERBOARD_WIDTH=9
CHECKERBOARD_HEIGHT=6
	
CAM_WIDTH=1280
CAM_HEIGHT=720

def set_res(cap, x,y):
	cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(x))
	cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(y))
	return cap.get(cv2.CAP_PROP_FRAME_WIDTH),cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
	
	
cam= cv2.VideoCapture(0)

print(set_res(cam,CAM_WIDTH,CAM_HEIGHT))

ret,frame=cam.read()
finishedCap=False

images = glob.glob('calibrationImgs/*.png')
for img in images:
	print("removing"+img)
	os.remove(img)

while(ret):
	#startTime=time.time()
	ret, frame = cam.read()
	if(ret):
		#cv2.putText(frame,str(int(1/(time.time()-startTime)))+"fps",(10,20),cv2.FONT_HERSHEY_DUPLEX,1,(255,0,0))
		cv2.imshow("LiveVideo", frame)
		key=cv2.waitKey(1)
		if(key == 13): #enter
			finishedCap = True
			break
		elif(key == 32): #space
			cv2.imwrite("calibrationImgs/"+str(time.time())+".png", frame)
			cv2.imshow("LiveVideo", np.zeros((CAM_HEIGHT, CAM_WIDTH, 3), np.uint8))
			cv2.waitKey(20)
			pass
		if key & 0xFF == ord('q'):
			break
		
		

if(finishedCap):
	# termination criteria
	criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
	# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
	objp = np.zeros((CHECKERBOARD_WIDTH*CHECKERBOARD_HEIGHT,3), np.float32)
	objp[:,:2] = np.mgrid[0:CHECKERBOARD_WIDTH,0:CHECKERBOARD_HEIGHT].T.reshape(-1,2)

	# Arrays to store object points and image points from all the images.
	objpoints = [] # 3d point in real world space
	imgpoints = [] # 2d points in image plane.

	images = glob.glob('calibrationImgs/*.png')

	for fname in images:
		img = cv2.imread(fname)
		gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
		
		# Find the chess board corners
		ret, corners = cv2.findChessboardCorners(gray, (CHECKERBOARD_WIDTH,CHECKERBOARD_HEIGHT),None)
		
		# If found, add object points, image points (after refining them)
		if ret == True:
			objpoints.append(objp)
			
			corners2=cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
			imgpoints.append(corners2)
			
			# Draw and display the corners
			cv2.drawChessboardCorners(img, (CHECKERBOARD_WIDTH,CHECKERBOARD_HEIGHT), corners2,ret)
			cv2.imshow('img',img)
			cv2.waitKey(500)
			
	ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)

	print(mtx)
	print(dist)
	#print(rvecs)
	#print(tvecs)

cam.release()
cv2.destroyAllWindows()
