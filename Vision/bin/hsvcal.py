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

def mouseHSV(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        colorsH = hsv[y,x,0]
        colorsS = hsv[y,x,1]
        colorsV = hsv[y,x,2]
        colors = hsv[y,x]
        if colorsH > H[1]:
            H[1] = colorsH
        elif colorsH < H[0]:
            H[0] = colorsH
        if colorsS > S[1]:
            S[1] = colorsS
        elif colorsS < S[0]:
            S[0] = colorsS
        if colorsV > V[1]:
            V[1] = colorsV
        elif colorsV < V[0]:
            V[0] = colorsV
        print("HSV Format: ",colors)
        
def drawFrame(frame):
    cv2.imshow("Image", frame)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    inrange = cv2.inRange(hsv, lowerb, upperb)
    mask = cv2.bitwise_and(frame, frame, mask = inrange)
    cv2.imshow("Mask", mask)

if __name__ == "__main__":
    ret, frame = cam.read()
    drawFrame(frame)

    cv2.namedWindow("Image")
    cv2.setMouseCallback("Image", mouseHSV)
    
    cv2.namedWindow("Mask")
    cv2.setMouseCallback("Mask", mouseHSV)

    while True:
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            print(H, S, V)
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
