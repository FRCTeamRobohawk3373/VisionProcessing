# import cv2
import numpy as np
# import cscore as cs

from bin import visioncore


class USBCamera:
    def __init__(self, id):
        settings = visioncore.getCameraSettings(id)
        self.name = settings["name"]
        self.path = settings["path"]
        self.properties = settings["properties"]
        self.cameraMatrix = np.array(settings["cameraMatrix"])
        self.distortionCoeffients = np.array(settings["distortionCoefficients"])
