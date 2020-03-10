import cv2
import numpy as np

H = np.array([71, 73])
S = np.array([237, 255])
V = np.array([171, 179])
 
def mouseRGB(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN: #checks mouse left button down condition
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
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
        elif colorsV < S[0]:
            V[0] = colorsV
        print("HSV Format: ",colors)
 
# Read an image, a window and bind the function to window
image = cv2.imread("img_1.jpg")
cv2.namedWindow('mouseRGB')
cv2.setMouseCallback('mouseRGB',mouseRGB)
 
#Do until esc pressed
while(1):
    cv2.imshow('mouseRGB',image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print(H, S, V)
        break
#if esc pressed, finish.
cv2.destroyAllWindows()
