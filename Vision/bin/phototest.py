import cv2
import numpy as np
import time
import os

lowerb = (71, 237, 171)
upperb = (73, 255, 179)

cam = cv2.VideoCapture("/dev/v4l/by-id/usb-HD_Camera_Manufacturer_USB_2.0_Camera-video-index0")
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
savindex = 0

def drawFrame(frame):
    cv2.imshow("Image", frame)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    inrange = cv2.inRange(hsv, lowerb, upperb)
    mask = cv2.bitwise_and(frame, frame, mask = inrange)
    cv2.imshow("Mask", mask)

if __name__ == "__main__":
    ret, frame = cam.read()
    drawFrame(frame)

    while True:
        time_start = time.time()
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break
        elif key & 0xFF == ord('.'):
            ret, frame = cam.retrieve()
            drawFrame(frame)
        elif key & 0xFF == ord('s'):
            savindex += 1
            ret, frame = cam.retrieve()
            path = os.path.relpath("../imgsav/img_{}.jpg".format(savindex))
            ret = cv2.imwrite(path, frame)

        cam.grab()

    cam.release()
    cv2.destroyAllWindows()
