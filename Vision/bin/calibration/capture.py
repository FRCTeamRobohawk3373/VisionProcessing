import cv2
import os

cam = cv2.VideoCapture("/dev/v4l/by-id/usb-HD_Camera_Manufacturer_USB_2.0_Camera-video-index0")
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
savindex = 0

if __name__ == "__main__":
    ret, frame = cam.read()
    cv2.imshow("Frame", frame)

    while True:
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break
        elif key & 0xFF == ord('.'):
            ret, frame = cam.retrieve()
            cv2.imshow("Frame", frame)
        elif key & 0xFF == ord('s'):
            savindex += 1
            path = os.path.relpath("./calib-imgs/{}.jpg".format(savindex))
            ret = cv2.imwrite(path, frame)

        cam.grab()

    cam.release()
    cv2.destroyAllWindows()
