import cv2
import numpy as np

BLUR_SIZE = 5  # Size of the Medianblur

HSV_THRESHHOLD_HUE = [0, 100]  # HSV Hue [Min,Max]
HSV_THRESHHOLD_SAT = [100, 255.0]  # HSV Saturation [Min,Max]
HSV_THRESHHOLD_VALUE = [100, 255.0]  # HSV Value [Min,Max]

ERODE_ITERATIONS = 1  # Number of time to run erode
ERODE_BORDERTYPE = cv2.BORDER_CONSTANT  # Erode filter type

FILTER_MIN_AREA = 200
FILTER_MIN_PERIMETER = 65
FILTER_MIN_SOLIDITY = 75

targetWidth = 14.62677
targetHeight = 5.825591

# camera1Matrix=np.array([
# 	[1.45631289e+03, 0.00000000e+00, 9.59733424e+02],
# 	[0.00000000e+00, 1.46236722e+03, 5.23444394e+02],
# 	[0.00000000e+00, 0.00000000e+00, 1.00000000e+00]
# ])

# camera1DistortionCoefficients=np.array([ 0.06717082, -0.26083562, -0.0014863,
#                                         -0.00031783,  0.24629886])

camera2Matrix = np.array([
    [966.76912687, 0, 631.74719378],
    [0, 967.10192295, 338.30596511],
    [0, 0, 1],
])

camera2DistortionCoefficients = np.array([0.06621377, -0.26423108, -0.00032913,
                                          0.0009213, 0.24902609])

camera1Matrix = np.array([
    [980.79815218, 0.0, 629.144456],
    [0.0, 981.43793669, 350.9971199],
    [0.0, 0.0, 1.0]
])

camera1DistortionCoefficients = np.array([0.06853195, -0.23183811, -0.00123328,
                                         -0.00386146, 0.18565542])

cam = cv2.VideoCapture(1)

while(True):
    _, processImg = cam.read()
    blur = cv2.medianBlur(processImg, BLUR_SIZE)
    gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
    # im1 = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
    dark = cv2.inRange(gray, 0, 63)
    medium = cv2.inRange(gray, 64, 127)
    light = cv2.inRange(gray, 128, 191)
    bright = cv2.inRange(gray, 192, 255)

    # HSVout = cv2.inRange(im1, (HSV_THRESHHOLD_HUE[0], HSV_THRESHHOLD_SAT[0], HSV_THRESHHOLD_VALUE[0]),
    #                     (HSV_THRESHHOLD_HUE[1], HSV_THRESHHOLD_SAT[1], HSV_THRESHHOLD_VALUE[1]))
    # HSVout=cv2.erode(HSVout, None, iterations=ERODE_ITERATIONS,
    #                  borderType=ERODE_BORDERTYPE)
    # contours, hierarchy = cv2.findContours(HSVout, mode=cv2.RETR_EXTERNAL,
    #                                        method=cv2.CHAIN_APPROX_SIMPLE)
    darkCon, hierarchy = cv2.findContours(dark, mode=cv2.RETR_EXTERNAL,
                                          method=cv2.CHAIN_APPROX_SIMPLE)
    medCon, hierarchy = cv2.findContours(medium, mode=cv2.RETR_EXTERNAL,
                                         method=cv2.CHAIN_APPROX_SIMPLE)
    lightCon, hierarchy = cv2.findContours(light, mode=cv2.RETR_EXTERNAL,
                                           method=cv2.CHAIN_APPROX_SIMPLE)
    brightCon, hierarchy = cv2.findContours(bright, mode=cv2.RETR_EXTERNAL,
                                            method=cv2.CHAIN_APPROX_SIMPLE)

    cv2.drawContours(processImg, darkCon, -1, (0, 0, 0))
    cv2.drawContours(processImg, medCon, -1, (0, 255, 0))
    cv2.drawContours(processImg, lightCon, -1, (0, 255, 255))
    cv2.drawContours(processImg, brightCon, -1, (0, 0, 255))

    # cv2.imshow('preprocessed', HSVout)
    cv2.imshow('image', processImg)
    cv2.imshow('preproc', gray)
    cv2.imshow('light', light)
    cv2.imshow('dark', dark)
    # cv2.imshow('contours', im1)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()
