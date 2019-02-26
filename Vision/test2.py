import cv2
import time

def set_res(cap, x,y):
	cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(x))
	cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(y))
	return cap.get(cv2.CAP_PROP_FRAME_WIDTH),cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

cap=cv2.VideoCapture(0)
set_res(cap,1080,960)
print(cap.set(cv2.CAP_PROP_FPS,30))
print(cap.get(cv2.CAP_PROP_FPS))
ret=True
while(ret):
	startTime=time.time()
	ret,frame=cap.read()
	if(ret):
		cv2.imshow("frame",frame)
		key = cv2.waitKey(1) & 0xFF
		print(str((time.time()-startTime)*1000)+"ms")
		if(key==ord('q')):
			break
cap.release()
cv2.destroyAllWindows()
