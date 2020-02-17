import cv2
import numpy as np

def process(image):
    fHeight,fWidth=image.shape[:2]
    contourImg = np.copy(image)

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
    cv2.drawContours(contourImg, output, -1, (0, 0, 255), 1)


    for i, cnt in enumerate(output):
        # poly = approxPolyDP_adaptive(cnt,8)
        rotRect = cv2.minAreaRect(cnt)
        # print(len(poly))

        # cv2.drawContours(contourImg, [poly] ,0,(0, 255, 255),1)

        hull = cv2.convexHull(cnt)
        #print(len(hull))
        cv2.drawContours(contourImg, [hull] ,0,(255, 255, 0),1)
        
        #print(hull)

        rect = cv2.boundingRect(cnt)
        cv2.rectangle(contourImg, rect, (255, 0, 255))
        x,y,w,h = rect
        cx=int(x+w/2)
        cy=int(y+h/2)
        cv2.drawMarker(contourImg,(cx,cy),(255, 255, 255))


        # topLeft=-hull[0][0][0]-hull[0][0][1]
        # topLeftIndex=0
        # topRight=hull[0][0][0]-hull[0][0][1]
        # topRightIndex=0

        # bottomLeft=hull[0][0][1]-hull[0][0][0]
        # bottomLeftIndex=0
        # bottomRight=hull[0][0][0]+hull[0][0][0]
        # bottomRightIndex=0
        # for x,pt in enumerate(hull):
        #     #top left corner point
        #     if(-pt[0][0]-pt[0][1]>topLeft):
        #         topLeft=-pt[0][0]-pt[0][1]
        #         topLeftIndex=x

        #     #top right corner point
        #     if(pt[0][0]-pt[0][1]>topRight):
        #         topRight=pt[0][0]-pt[0][1]
        #         topRightIndex=x

        #     #bottom left corner point
        #     if(pt[0][1]-(pt[0][0]-mx)>bottomLeft):
        #         bottomLeft=pt[0][1]-(pt[0][0]-mx)
        #         bottomLeftIndex=x

        #     #bottom right corner point
        #     if((my-pt[0][1])+(mx-pt[0][0])<bottomRight):
        #         bottomRight=(my-pt[0][1])+(mx-pt[0][0])
        #         bottomRightIndex=x

        #cv2.drawMarker(contourImg,tuple(hull[bottomLeftIndex][0]),(0, 255, 255),thickness=2)
        #cv2.drawMarker(contourImg,tuple(hull[bottomRightIndex][0]),(0, 255, 255),thickness=2)
        #cv2.drawMarker(contourImg,tuple(hull[topLeftIndex][0]),(0, 255, 255),thickness=2)
        #cv2.drawMarker(contourImg,tuple(hull[topRightIndex][0]),(0, 255, 255),thickness=2)
        
        #topLeft = tuple(hull[topLeftIndex][0])
        #topRight = tuple(hull[topRightIndex][0])
        #bottomLeft = tuple(hull[bottomLeftIndex][0])
        #bottomRight = tuple(hull[bottomRightIndex][0])

        #print(slopes)

        box = cv2.boxPoints(rotRect)
        box = np.int0(box)
        #print(box)
        cv2.drawContours(contourImg,[box],0,(255,255,255),2)

        #centerX=(topLeft[0]+topRight[0]+bottomLeft[0]+bottomRight[0])/4
        #centerY=(topLeft[1]+topRight[1]+bottomLeft[1]+bottomRight[1])/4

        #cv2.rectangle(contourImg, rect, (255, 0, 255))
        '''Corners2d=np.array([
            (topLeft[0]-centerX, topLeft[1]-centerY), # top-left
            (topRight[0]-centerX, topRight[1]-centerY), # top-right
            (bottomRight[0]-centerX, bottomRight[1]-centerY), # bottom-right
            (bottomLeft[0]-centerX, bottomLeft[1]-centerY) # bottom-left
        ], dtype=np.float32)'''

        Corners2d=np.array([
            (x-w/2, y-h/2),	# top-left
            (x+w/2, y-h/2),	# top-right
            (x+w/2, y+h/2),	# bottom-right
            (x-w/2, y+h/2)	# bottom-left
        ])
        '''Corners2d=np.array([
            (x, y),	# top-left
            (x+w, y),	# top-right
            (x+w, y+h),	# bottom-right
            (x, y+h)	# bottom-left
        ])'''

        retval, rvec, tvec=cv2.solvePnP(CORNERS_3D, Corners2d, CAMERA_MATRIX, DISTORTION_COEFFICIENTS)

        print(rect)
        distance, robotAngle, targetAngle = computeValues(rvec, tvec)
        #cv2.putText(contourImg,str(distance)+"in",(5,50),cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,255))
        distance = DISTANCE_SCALER*distance+DISTANCE_OFFSET
        robotAngle = ROBOT_ANGLE_SCALER*robotAngle+ROBOT_ANGLE_OFFSET
        targetOffset = cx-fWidth/2

        #r=(WIDTH_3D_TOP/w)
        robotAngle=(targetOffset*(WIDTH_3D_TOP/w))/distance
        if(abs(robotAngle)>1):
            robotAngle=math.copysign(1.0,robotAngle)
        
        robotAngle=90-math.degrees(math.acos(robotAngle))

        
        print("Target #"+str(i)+":distance="+str(distance)+", robot Angle="+\
              str(robotAngle)+", targetAngle="+str(targetAngle))
        
        cv2.putText(contourImg,str(distance)+"in",(5,50),cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,255))
        cv2.putText(contourImg,str(robotAngle)+"deg",(5,100),cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,255))

    cv2.imshow("contours", contourImg)
    return masked

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
