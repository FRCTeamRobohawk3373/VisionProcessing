import cv2
import numpy as np

#class Constants:

BLUR_SIZE = 5 #Size of the Medianblur 

HSV_THRESHHOLD_HUE = [72.84172661870504, 96] #HSV Hue [Min,Max]
HSV_THRESHHOLD_SAT = [79, 255.0]#HSV Saturation [Min,Max]
HSV_THRESHHOLD_VALUE = [170, 255.0]#HSV Value [Min,Max]

ERODE_ITERATIONS = 1 #Number of time to run erode
ERODE_BORDERTYPE = cv2.BORDER_CONSTANT #Erode filter type

FILTER_MIN_AREA = 200
FILTER_MIN_PERIMETER = 65
FILTER_MIN_SOLIDITY = 75

targetWidth=14.62677
targetHeight=5.825591

#camera1Matrix=np.array([
#	[1.45631289e+03, 0.00000000e+00, 9.59733424e+02],
#	[0.00000000e+00, 1.46236722e+03, 5.23444394e+02],
#	[0.00000000e+00, 0.00000000e+00, 1.00000000e+00]
#])

#camera1DistortionCoefficients=np.array([ 0.06717082, -0.26083562, -0.0014863,  -0.00031783,  0.24629886])

camera2Matrix=np.array([
	[966.76912687, 0, 631.74719378],
	[0, 967.10192295, 338.30596511],
	[0, 0, 1],
])

camera2DistortionCoefficients=np.array([0.06621377, -0.26423108, -0.00032913,  0.0009213, 0.24902609])

camera1Matrix=np.array([
	[980.79815218, 0.0, 629.144456],
 	[0.0, 981.43793669, 350.9971199],
 	[0.0, 0.0, 1.0]
])

camera1DistortionCoefficients=np.array([0.06853195,-0.23183811,-0.00123328,-0.00386146,0.18565542])
