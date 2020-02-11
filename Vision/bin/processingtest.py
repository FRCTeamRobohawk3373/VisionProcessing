import cv2
import numpy as np


H = [63, 78]
S = [195, 255]
V = [90, 190]

lowerb = (H[0], S[0], V[0])
upperb = (H[1], S[1], V[1])

cam = cv2.VideoCapture("/dev/v4l/by-id/usb-HD_Camera_Manufacturer_USB_2.0_Camera-video-index0")
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)


def drawFrame(frame):
    cv2.imshow("Frame", frame)
    cv2.imshow("Processed", process(frame))


def process(image):
    proc = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    proc = cv2.medianBlur(proc, 1)

    proc = cv2.erode(proc, struct)
    proc = cv2.dilate(proc, struct)

    inrange = cv2.inRange(proc, lowerb, upperb)
    
    final = cv2.bitwise_and(image, image, mask = inrange)

    #conts, hierarchy = cv2.findContours(inrange, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #cv2.drawContours(final, conts, -1, (0, 255, 0), 3)
    return final

def callback(_):
    pass


if __name__ == "__main__":
    cv2.namedWindow("Frame")
    cv2.namedWindow("Processed")

    _, frame = cam.read()
    drawFrame(frame)

    while True:
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break
        elif key & 0xFF == ord('.'):
            ret, frame = cam.retrieve()
            drawFrame(frame)
        #elif key & 0xFF == ord('r'):
        #    drawFrame(frame)

        cam.grab()

    cam.release()
    cv2.destroyAllWindows()
