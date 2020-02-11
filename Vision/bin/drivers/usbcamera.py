import cv2
import numpy as np
import multiprocessing
# import cscore as cs


class USBCamera:
    def __init__(self, settings):
        self.name = settings["name"]
        self.path = settings["path"]
        self.properties = settings["properties"]
        self.cameraMatrix = np.array(settings["cameraMatrix"])
        self.distortionCoeffients = np.array(settings["distortionCoefficients"])
        self.cam = cv2.VideoCapture(self.path)
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    def set(self, property, value):
        self.cam.set(property, value)

    def grab(self):
        self.cam.grab()

    def retrieve(self):
        _, frame = self.cam.retrieve()
        return frame

    def read(self):
        _, frame = self.cam.read()
        return frame

    def __delete__(self):
        self.cam.close()
