import cv2
import numpy as np
import multiprocessing
import cscore
from utility import filterDict
import logging
import subprocess
import shlex


class USBCamera:
    def __init__(self, server, settings, size = (320,240), fps = 15):
        self.name = settings["name"]
        self.path = settings["path"]
        self.properties = settings["properties"]

        self.logger=logging.getLogger("camera("+self.name+")")

        self.settings = settings["settings"]
        self.logger.debug("settings "+ str(self.settings))
        
        self.cameraMatrix = np.array(settings["cameraMatrix"])
        self.distortionCoeffients = np.array(settings["distortionCoefficients"])

        if("width" in self.properties and "height" in self.properties):
            self.width = self.properties["width"]
            self.height = self.properties["height"]
        else:
            self.width, self.height = size
        
        self.camera = cscore.UsbCamera(self.name, self.path)
        #server.startAutomaticCapture(camera=self.camera)
        # keep the camera open for faster switching
        self.camera.setConnectionStrategy(cscore.VideoSource.ConnectionStrategy.kKeepOpen)

        self.camera.setResolution(self.width, self.height)
        self.camera.setFPS(int(fps))

        self.logger.debug("Settings:\n"+subprocess.run(shlex.split("v4l2-ctl -d "+self.path+" -L"),capture_output=True).stdout.decode("utf-8").strip())
        
        self.configSettings()

        mode = self.camera.getVideoMode()
        self.logger.info("{0} started with pixelFormat:{1}, at {2}x{3} {4}FPS".format(self.name, mode.pixelFormat, mode.width, mode.height, mode.fps))

    def configSettings(self):
        if("exposure_auto" in self.settings):
            self._setProperty("exposure_auto", self.settings["exposure_auto"])

        if("white_balance_temperature_auto" in self.settings):
            self._setProperty("white_balance_temperature_auto", self.settings["white_balance_temperature_auto"])
            
        for setting in filterDict(self.settings,["exposure_auto","white_balance_temperature_auto"]):
            self._setProperty(setting, self.settings["setting"])
            
    def set(self, property, value):
        if(self._setProperty(self, property, value):
            self.settings[property]=value
            return True
        return False

    def _setProperty(self, name, value):
        try:
            if(type(value) is str):
                self.camera.getProperty(name).setString(value)
            else:
                self.camera.getProperty(name).set(value)
            return True

        except Exception:
            self.logger.warning("Unable to set property '{0}' to '{1}'".format(name,value))
            return False

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
