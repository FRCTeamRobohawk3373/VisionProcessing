import cv2
import time

cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

while(True):
    time_start = time.time()
    ret, frame = cam.read()
    if(ret != True):
        break
    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    print("FPS: ", 1.0 / (time.time() - time_start))
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xff == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()
