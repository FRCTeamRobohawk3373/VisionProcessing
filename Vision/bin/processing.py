import cv2
import numpy as np
import logging
from threading import Thread


class ProcessingThread:
    threadCount = 0

    def __init__(self, debug=False):
        ProcessingThread.threadCount+=1
		self.processingLogger = logging.getLogger("ProcessingThread-"+str(ProcessingThread.threadCount))

        self.imageLock = threading.Lock()
        self.thread = Thread(target=self.process)
        #self.thread = Process(target=self.process, args=(self,))
        self.thread.daemon=True
        self.running = False
        self.img=None
        self.newImageAvailable=False
        self.debug=debug
        self.finalTargets=[None]
        self.cameraMatrix=None
        self.distortionCoefficients=None

    def setCameraCharacteristics(self,cameraMatrix,distortionCoefficients):
        self.cameraMatrix=cameraMatrix
        self.distortionCoefficients=distortionCoefficients

    def run(self, firstImage):
        self.img = firstImage
        self.running=True
        self.thread.start()

    def stop(self):
        self.running=False
        cv2.destroyAllWindows()
        self.thread.join(20)

    def __delete__(self):
        self.stop()

    def processNewImage(self, img):
        with self.imageLock:
            self.img=img
            self.newImageAvailable=True

    def getTargets(self):
        return self.finalTargets


    def process(self):
        newImage = False
        image = np.zeros((const.STREAM_RESOLUTION[1],const.STREAM_RESOLUTION[0],3),np.uint8)
        data = None
        while(self.running):
            with self.imageLock:
                newImage = self.newImageAvailable
                if(newImage):
                    image = np.copy(self.img)
                    self.newImageAvailable=False

            if(newImage):
                newImage=False
                fHeight,fWidth=image.shape[:2]

                mask = cv2.GaussianBlur(image, (5, 5), 0)
                mask = cv2.cvtColor(mask, cv2.COLOR_BGR2HSV)
                mask = cv2.inRange(mask, lowerb, upperb)

                struct_erode = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                struct_dilate = cv2.getStructuringElement(cv2.MORPH_CROSS, (5, 5))
                mask = cv2.erode(mask, struct_erode, iterations=1)
                mask = cv2.dilate(mask, struct_dilate, iterations=1)

                masked = cv2.bitwise_and(image, image, mask = mask)

                contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                output = []
                for contour in contours:
                    #x,y,w,h = cv2.boundingRect(contour)
                    area = cv2.contourArea(contour)
                    if (area < MIN_AREA):
                        continue
                    if (cv2.arcLength(contour, True) < MIN_PERIMETER):
                        continue
                    hull = cv2.convexHull(contour)
                    solid = 100 * area / cv2.contourArea(hull)
                    if (solid < SOLIDITY[0] or solid > SOLIDITY[1]):
                        continue

                    output.append(contour)

                print("Found " + str(len(output))+" ")
                cv2.drawContours(image, output, -1, (0, 0, 255), 1)

                finalTargets = []
                for i, cnt in enumerate(output):
                    # poly = approxPolyDP_adaptive(cnt,8)
                    rotRect = cv2.minAreaRect(cnt)
                    # print(len(poly))

                    # cv2.drawContours(image, [poly] ,0,(0, 255, 255),1)

                    hull = cv2.convexHull(cnt)
                    #print(len(hull))
                    cv2.drawContours(image, [hull] ,0,(255, 255, 0),1)

                    #print(hull)

                    rect = cv2.boundingRect(cnt)
                    cv2.rectangle(image, rect, (255, 0, 255))
                    x,y,w,h = rect
                    cx=int(x+w/2)
                    cy=int(y+h/2)
                    cv2.drawMarker(image,(cx,cy),(255, 255, 255))

                    box = cv2.boxPoints(rotRect)
                    box = np.int0(box)
                    #print(box)
                    cv2.drawContours(image,[box],0,(255,255,255),2)

                    Corners2d=np.array([
                        (x-w/2, y-h/2),	# top-left
                        (x+w/2, y-h/2),	# top-right
                        (x+w/2, y+h/2),	# bottom-right
                        (x-w/2, y+h/2)	# bottom-left
                    ])

                    retval, rvec, tvec=cv2.solvePnP(CORNERS_3D, Corners2d, CAMERA_MATRIX, DISTORTION_COEFFICIENTS)

                    print(rect)
                    distance, robotAngle, targetAngle = computeValues(rvec, tvec)
                    #cv2.putText(image,str(distance)+"in",(5,50),cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,255))
                    distance = DISTANCE_SCALER*distance+DISTANCE_OFFSET
                    #robotAngle = ROBOT_ANGLE_SCALER*robotAngle+ROBOT_ANGLE_OFFSET
                    targetOffset = cx-fWidth/2

                    #r=(WIDTH_3D_TOP/w)
                    robotAngle=(targetOffset*(WIDTH_3D_TOP/w))/distance
                    if(abs(robotAngle)>1):
                        robotAngle=math.copysign(1.0,robotAngle)

                    robotAngle=90-math.degrees(math.acos(robotAngle))

                    print("Target #"+str(i)+":distance="+str(distance)+", robot Angle="+\
                        str(robotAngle)+", targetAngle="+str(targetAngle))

                    cv2.putText(image,str(distance)+"in",(5,50),cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,255))
                    cv2.putText(image,str(robotAngle)+"deg",(5,100),cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,255))
                    
                    posx=(cx-fWidth/2)/(fWidth/2)
					posy=(cy-fHeight/2)/(fHeight/2)
                    finalTargets.append([i,round(posx,4),round(posy,4),round(distance,4), round(robotAngle,4), round(targetAngle,4)])


                data=[]

                cv2.imshow("contours", image)



    def approxPolyDP_adaptive(contour, nsides, max_dp_error=0.1):

        step = 0.005
        peri = cv2.arcLength(contour, True)
        dp_err = step
        while dp_err < max_dp_error:
            res = cv2.approxPolyDP(contour, dp_err * peri, True)
            if len(res) <= nsides:
                print(dp_err)
                return res
            dp_err += step
        return None

    def computeValues(rvec, tvec):
        print(tvec)
        print(rvec)
        x=tvec[0][0]
        z=tvec[2][0]

        distance = math.sqrt(x**2+z**2)

        robotAngle = math.degrees(math.atan2(x,z))

        rot,_ = cv2.Rodrigues(rvec)

        print(rot)

        rotInv = rot.transpose()
        pZeroWorld = np.matmul(rotInv, -tvec)
        targetAngle = math.degrees(math.atan2(pZeroWorld[0][0], pZeroWorld[2][0]))

        return distance, robotAngle, targetAngle
