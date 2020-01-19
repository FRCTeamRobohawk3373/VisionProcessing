import cv2
import numpy as np

sensitivity = 25
cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_EXPOSURE, .5)
cam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)

min_hsv = np.array([85, 205, 140])
max_hsv = np.array([92, 255, 151])


def onMouse(k, x, y, s, p):
    global hsv
    if k == 1:
        print(hsv[y, x])


cv2.namedWindow("hsv")
cv2.setMouseCallback("hsv", onMouse)
while(True):
    _, img = cam.read()
    blur = cv2.medianBlur(img, 5)
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    greenBin = cv2.inRange(hsv, min_hsv, max_hsv)

    darkCon, hierarchy = cv2.findContours(greenBin, mode=cv2.RETR_EXTERNAL,
                                          method=cv2.CHAIN_APPROX_SIMPLE)

    cv2.drawContours(img, darkCon, -1, (0, 0, 255))

    cv2.imshow('hsv', hsv)
    cv2.imshow('image', img)
    cv2.imshow('blur', blur)
    cv2.imshow("green map", greenBin)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()
