import cv2
import numpy as np
import math


RANGE_H = [63, 78]
RANGE_S = [195, 255]
RANGE_V = [90, 255]

lowerb = (RANGE_H[0], RANGE_S[0], RANGE_V[0])
upperb = (RANGE_H[1], RANGE_S[1], RANGE_V[1])

WIDTH_3D = 39.25
HEIGHT_3D = 17

rect_corners_3d = np.array([
    [-WIDTH_3D/2, -HEIGHT_3D/2, 0.0], # top-left
    [WIDTH_3D/2, -HEIGHT_3D/2, 0.0],  # top-right
    [WIDTH_3D/2, HEIGHT_3D/2, 0.0],   # bottom-right
    [-WIDTH_3D/2, HEIGHT_3D/2, 0.0]   # bottom-left
])

CAMERA_MATRIX = np.array([
    [2.51394629e+04, 0.00000000e+00, 1.14952902e+03],
    [0.00000000e+00, 2.68897824e+04, 7.98795645e+02],
    [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]
])

DISTORTION_COEFFICIENTS = np.array([
    -1.03301952e+01,
    -2.41200817e+04,
     6.00390632e-02,
    -2.78240440e-01,
    -9.02368894e+01
])

cam = cv2.VideoCapture("/dev/v4l/by-id/usb-HD_Camera_Manufacturer_USB_2.0_Camera-video-index0")
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)


def drawFrame(frame):
    cv2.imshow("Frame", frame)
    cv2.imshow("Processed", process(frame))


def process(image):
    cont = np.copy(image)
    proc = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    proc = cv2.medianBlur(proc, 1)

    mask = cv2.inRange(proc, lowerb, upperb)
    struct_erode = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    struct_dilate = cv2.getStructuringElement(cv2.MORPH_CROSS, (5, 5))
    mask = cv2.erode(mask, struct_erode)
    mask = cv2.dilate(mask, struct_dilate, iterations=2)

    masked = cv2.bitwise_and(image, image, mask = mask)

    conts, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    rects = []
    for i, cnt in enumerate(conts):
        rect = cv2.boundingRect(cnt)
        rects.append(cv2.boundingRect(cnt))
        cv2.rectangle(cont, rect, (255, 0, 255))
        x,y,w,h = rect
        rectCorners2d=np.array([
            (x-w/2, y-h/2), # top-left
            (x+w/2, y-h/2), # top-right
            (x+w/2, y+h/2), # bottom-right
            (x-w/2, y+h/2)  # bottom-left
        ])
        
        retval, rvec, tvec=cv2.solvePnP(rect_corners_3d, rectCorners2d, CAMERA_MATRIX, DISTORTION_COEFFICIENTS)
        
        distance, robotAngle, targetAngle = computeValues(rvec, tvec)
        print("Target #"+str(i)+":distance="+str(distance)+", robot Angle="+\
              str(robotAngle)+", targetAngle"+str(targetAngle))
    
    
    
    
    cv2.drawContours(cont, conts, -1, (0, 0, 255), 1)
    cv2.imshow("Cont", cont)
    return masked

def computeValues(rvec, tvec):
    x=tvec[0][0]
    z=tvec[2][0]
    
    distance = math.sqrt(x*x+z*z)
    
    robotAngle = math.atan2(x,z)
    
    rot,_ = cv2.Rodrigues(rvec)
    
    rotInv = rot.transpose()
    pZeroWorld = np.matmul(rotInv, -tvec)
    targetAngle = math.atan2(pZeroWorld[0][0], pZeroWorld[2][0])
    
    return distance, robotAngle, targetAngle

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
