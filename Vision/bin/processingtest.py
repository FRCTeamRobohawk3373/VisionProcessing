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
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    inrange = cv2.inRange(hsv, lowerb, upperb)
    mask = cv2.bitwise_and(frame, frame, mask = inrange)
    cv2.imshow("Mask", mask)
    image = contours(frame, inrange)
    cv2.imshow("Contours", image)
    
def processing(image):
    

def contours(frame, binframe):
    conts, hierarchy = cv2.findContours(binframe, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(frame, conts, -1, (0, 255, 0), 3)
    return frame

if __name__ == "__main__":
    _, frame = cam.read()
    drawFrame(frame)
    
    while True:
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break   
        elif key & 0xFF == ord('.'):
            ret, frame = cam.retrieve()
            drawFrame(frame)

        cam.grab()

    cam.release()
    cv2.destroyAllWindows()
