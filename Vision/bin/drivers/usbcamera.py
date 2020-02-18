import cv2
import numpy as np
import multiprocessing
import cscore as cs
from utility import filterDict
import logging
import subprocess
import shlex


class USBCamera:
    def __init__(self, settings):
        self.name = settings["name"]
        self.path = settings["path"]
        self.properties = settings["properties"]

        self.logger=logging.getLogger("camera-"+self.name)

        self.settings = settings["settings"]
        self.logger.debug("settings "+ str(self.settings))
        self.configSettings()

        self.cameraMatrix = np.array(settings["cameraMatrix"])
        self.distortionCoeffients = np.array(settings["distortionCoefficients"])

        
        #self.cam = cv2.VideoCapture(self.path)
        #self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        #self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        self.logger.info("camera started")

    def configSettings(self):

        if("exposure_auto" in self.settings):
            subprocess.call(shlex.split("v4l2-ctl -d "+self.path+" -c exposure_auto="+str(self.settings["exposure_auto"])))
        if("white_balance_temperature_auto" in self.settings):
            subprocess.call(shlex.split("v4l2-ctl -d "+self.path+" -c white_balance_temperature_auto="+str(self.settings["white_balance_temperature_auto"])))

        for setting in filterDict(self.settings,["exposure_auto","white_balance_temperature_auto"]):
            subprocess.call(shlex.split("v4l2-ctl -d "+self.path+" -c "+setting+"="+str(self.settings[setting])))

    def set(self, property, value):
        subprocess.call(shlex.split("v4l2-ctl -d "+self.path+" -c "+property+"="+str(value)))
        self.settings[property]=value

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
