import cv2
import numpy as np

from cscore import CameraServer, CvSource, VideoMode, UsbCamera

def main():
    cs = CameraServer.getInstance()
    cs.enableLogging()

    outputStream = CvSource('camera', VideoMode.PixelFormat.kMJPEG,
                                             int(640), int(480),
                                             int(15))
    cs.addCamera(outputStream)
    server = cs.addServer(name='camera', port=int(5801))
    server.setSource(outputStream)

    camera = UsbCamera("cam1", '/dev/v4l/by-id/usb-HD_Camera_Manufacturer_USB_2.0_Camera-video-index0')
    # Capture from the first USB Camera on the system
    cs.startAutomaticCapture(camera=camera)
    camera.setResolution(640, 480)

    # Get a CvSink. This will capture images from the camera
    cvSink = cs.getVideo(camera=camera)

    # Allocating new images is very expensive, always try to preallocate
    img = np.zeros(shape=(480, 640, 3), dtype=np.uint8)

    while True:
        # Tell the CvSink to grab a frame from the camera and put it
        # in the source image.  If there is an error notify the output.
        time, img = cvSink.grabFrame(img)
        if time == 0:
            # Send the output the error.
            outputStream.notifyError(cvSink.getError());
            # skip the rest of the current iteration
            continue

        #
        # Insert your image processing logic here!
        #
        cv2.imshow("stream",img)
        # (optional) send some image back to the dashboard
        outputStream.putFrame(img)

main()

# cam = cv2.VideoCapture(0)
# cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
# cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# while(True):
#     time_start = time.time()
#     ret, frame = cam.read()
#     if(ret != True):
#         break
#     #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#     print("FPS: ", 1.0 / (time.time() - time_start))
#     cv2.imshow('frame', frame)
#     if cv2.waitKey(1) & 0xff == ord('q'):
#         break

# cam.release()
# cv2.destroyAllWindows()
