import cv2
import numpy as np
# import cscore as cs


class USBCamera:
    def __init__(self, settings):
        self.name = settings["name"]
        self.path = settings["path"]
        self.properties = settings["properties"]
        self.cameraMatrix = np.array(settings["cameraMatrix"])
        self.distortionCoeffients = np.array(settings["distortionCoefficients"])
        self.cam = cv2.VideoCapture(self.path)
    def read(self):
        return self.cam.read()
    def set(self, property, value):
        self.cam.set(property, value)
