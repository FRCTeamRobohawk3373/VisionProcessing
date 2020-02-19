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

        self.width, self.height = size
        
        self.camera = cscore.UsbCamera(self.name, self.path)
        server.startAutomaticCapture(camera=self.camera)
        # keep the camera open for faster switching
        self.camera.setConnectionStrategy(cscore.VideoSource.ConnectionStrategy.kKeepOpen)

        self.camera.setResolution(self.width, self.height)
        self.camera.setFPS(int(fps))

        #for prop in self.camera.enumerateProperties():
            #print(str(prop))
            #print(prop.getName()+"("+str(prop.getKind())+"): min="+str(prop.getMin())+" max="+str(prop.getMax())+" default="+str(prop.getDefault())+" value="+str(prop.get()))

        self.logger.debug("Settings:\n"+subprocess.run(shlex.split("v4l2-ctl -d "+self.path+" -L"),capture_output=True).stdout.decode("utf-8").strip())
        
        self.configSettings()

        self.logger.info("camera started")

    def configSettings(self):

        if("exposure_auto" in self.settings):
            status = subprocess.run(shlex.split("v4l2-ctl -d "+self.path+" -c exposure_auto="+str(self.settings["exposure_auto"])),capture_output=True)
            if(not(status.stderr.decode("utf-8") == "")):
                self.logger.error(status.stderr.decode("utf-8").strip())

        if("white_balance_temperature_auto" in self.settings):
            status = subprocess.run(shlex.split("v4l2-ctl -d "+self.path+" -c white_balance_temperature_auto="+str(self.settings["white_balance_temperature_auto"])),capture_output=True)
            if(not(status.stderr.decode("utf-8") == "")):
                self.logger.error(status.stderr.decode("utf-8").strip())

        for setting in filterDict(self.settings,["exposure_auto","white_balance_temperature_auto"]):
            status = subprocess.run(shlex.split("v4l2-ctl -d "+self.path+" -c "+setting+"="+str(self.settings[setting])),capture_output=True)
            if(not(status.stderr.decode("utf-8") == "")):
                self.logger.error(status.stderr.decode("utf-8").strip())

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
