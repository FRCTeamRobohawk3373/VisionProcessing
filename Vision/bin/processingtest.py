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
    diameter = (cv2.getTrackbarPos("Diameter", "Processed") * 2) + 1
    sigma_color = cv2.getTrackbarPos("Sigma Color", "Processed")
    sigma_space = cv2.getTrackbarPos("Sigma Space", "Processed")
    #blur_size = cv2.getTrackbarPos("Blur Size", "Processed")
    #morph_type = cv2.getTrackbarPos("Morph Type", "Processed")
    
    
    proc = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    proc = cv2.bilateralFilter(proc, diameter, sigma_color, sigma_space)
    
    inrange = cv2.inRange(proc, lowerb, upperb)
    final = cv2.bitwise_and(image, image, mask = inrange)
    
    #proc_rect = cv2.erode(proc, cv2.getStructuringElement(morph_type, 5))
    
    #conts, hierarchy = cv2.findContours(inrange, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #cv2.drawContours(final, conts, -1, (0, 255, 0), 3)
    return final

def callback(_):
    pass


if __name__ == "__main__":
    cv2.namedWindow("Frame")
    cv2.namedWindow("Processed")
    cv2.createTrackbar("Diameter", "Processed", 2, 2, callback)
    cv2.createTrackbar("Sigma Color", "Processed", 10, 25, callback)
    cv2.createTrackbar("Sigma Space", "Processed", 10, 25, callback)
    #.createTrackbar("Blur Size", "Processed", 1, 15, None)
    #cv2.createTrackbar("Morph Type", "Processed", 0, 2, None)
    
    _, frame = cam.read()
    drawFrame(frame)
    
    while True:
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break   
        elif key & 0xFF == ord('.'):
            ret, frame = cam.retrieve()
            drawFrame(frame)
        elif key & 0xFF == ord('r'):
            drawFrame(frame)

        cam.grab()

    cam.release()
    cv2.destroyAllWindows()
