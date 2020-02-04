import cv2
import numpy as np

H = [63, 78]
S = [195, 255]
V = [90, 190]

lowerb = (H[0], S[0], V[0])
upperb = (H[1], S[1], V[1])

def drawFrame(frame, m=True):
    cv2.imshow("Image", frame)
    if m:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        inrange = cv2.inRange(hsv, lowerb, upperb)
        mask = cv2.bitwise_and(frame, frame, mask = inrange)
        cv2.imshow("Mask", mask)

if __name__ == "__main__":
    while True:
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            print(H, S, V)
            break   
        elif key & 0xFF == ord('.'):
            ret, frame = cam.retrieve()
            drawFrame(frame)
        # elif key & 0xFF == ord('s'):
            # savindex += 1
            # ret, frame = cam.retrieve()
            # path = os.path.relpath("../imgsav/img_{}.jpg".format(savindex))
            # ret = cv2.imwrite(path, frame)

        cam.grab()

    cam.release()
    cv2.destroyAllWindows()
