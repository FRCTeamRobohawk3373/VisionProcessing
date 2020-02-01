import cv2
import time

start = time.time()

duration = 30
counter = 0

cam = cv2.VideoCapture(2)

print("Initialization complete - took ",  (time.time() - start), " seconds.")

#cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
#cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

start_test = time.time()

while time.time() - start_test < duration:
    _, frame = cam.read()
    
    blur = cv2.medianBlur(frame, 5)
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    hsv = cv2.inRange(hsv, (72, 79, 170), (96, 255, 255))
    
    final = cv2.erode(hsv, None, iterations=1, borderType=cv2.BORDER_CONSTANT)
    counter += 1
    
print("Resolution: 1920x1080, FPS: ", counter / (time.time() - start_test))

cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

start_test = time.time()

while time.time() - start_test < duration:
    _, frame = cam.read()
    
    blur = cv2.medianBlur(frame, 5)
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    hsv = cv2.inRange(hsv, (72, 79, 170), (96, 255, 255))
    
    final = cv2.erode(hsv, None, iterations=1, borderType=cv2.BORDER_CONSTANT)
    counter += 1
    
print("Resolution: 1280x720, FPS: ", counter / (time.time() - start_test))

cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

start_test = time.time()

while time.time() - start_test < duration:
    _, frame = cam.read()
    
    blur = cv2.medianBlur(frame, 5)
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    hsv = cv2.inRange(hsv, (72, 79, 170), (96, 255, 255))
    
    final = cv2.erode(hsv, None, iterations=1, borderType=cv2.BORDER_CONSTANT)
    counter += 1
    
print("Resolution: 640x480, FPS: ", counter / (time.time() - start_test))

print("Total Time: ", time.time() - start)

cam.release()
cv2.destroyAllWindows()
