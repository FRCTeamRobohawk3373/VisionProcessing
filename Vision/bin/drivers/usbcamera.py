import cv2
import numpy as np
import multiprocessing
import cscore
from utility import filterDict
import logging
import subprocess
import shlex
from time import time, sleep


class USBCamera:
    def __init__(self, server, settings, size = (320,240), fps = 15):
        self.name = settings["name"]
        self.path = settings["path"]

        self.logger=logging.getLogger("camera("+self.name+")")

        if(settings["destinations"]["streamVideo"] and settings["destinations"]["processVideo"]):
            self.logger.warning("{0} is configured to stream and process".format(self.name))
            self.destination="BOTH"
        elif(settings["destinations"]["streamVideo"]):
            self.destination="STREAM"
        elif(settings["destinations"]["processVideo"]):
            self.destination="VISION"
        else:
            self.destination="NONE"
        
        self.switchIndex = settings["destinations"]["switchIndex"]

        self.settings = settings["settings"]
        self.logger.debug("settings "+ str(self.settings))
        
        self.cameraMatrix = np.array(settings["cameraMatrix"])
        self.distortionCoeffients = np.array(settings["distortionCoefficients"])

        self.properties = settings["properties"]
        if("width" in self.properties and "height" in self.properties):
            self.width = self.properties["width"]
            self.height = self.properties["height"]
        else:
            self.width, self.height = size
        
        #initalize the camera
        self.camera = cscore.UsbCamera(self.name, self.path)
        # keep the camera open for faster switching
        self.camera.setConnectionStrategy(cscore.VideoSource.ConnectionStrategy.kKeepOpen)

        self.camera.setResolution(self.width, self.height)
        self.camera.setFPS(int(fps))

        self.logger.debug("Settings:\n"+subprocess.run(shlex.split("v4l2-ctl -d "+self.path+" -L"),capture_output=True).stdout.decode("utf-8").strip())
        
        self.configSettings()

        mode = self.camera.getVideoMode()
        self.logger.info("{0} started with pixelFormat:{1}, at {2}x{3} {4}FPS".format(self.name, mode.pixelFormat, mode.width, mode.height, mode.fps))

        self.sink = cscore.CvSink("sink_"+self.name)
        self.sink.setSource(self.camera)
        self.cameraFrame = None
        self.frameTime=None
        self.stoped=False

    def configSettings(self):
        if("exposure_auto" in self.settings):
            self._setProperty("exposure_auto", self.settings["exposure_auto"])

        if("white_balance_temperature_auto" in self.settings):
            self._setProperty("white_balance_temperature_auto", self.settings["white_balance_temperature_auto"])
            
        for setting in filterDict(self.settings,["exposure_auto","white_balance_temperature_auto"]):
            self._setProperty(setting, self.settings[setting])
            
    def set(self, property, value):
        if(self._setProperty(self, property, value)):
            self.settings[property]=value
            return True
        return False

    def isConnected(self):
        return self.camera.isConnected()

    def getName(self):
        return self.name

    def getSource(self):
        return self.camera

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

    def start(self):
        t=Thread(target=self._update,args=())
        t.daemon = True
        t.start()

    def _update(self):
        fpsStart = time()

        while True:
            if (self.stopped):
                return

            self.frametime, self.camera_frame = self.sink.grabFrame(self.camera_frame)
            frameNumber+=1
            if (frameNumber % 150 == 0):
                fpsEnd = time()
                dt = fpsEnd - fpsStart
                self.logger.info("150 frames in {0:.3f} seconds = {1:.2f} FPS".format(dt, 150.0 / dt))
                fpsStart=fpsEnd
                frameNumber=0
        
        return

    def read(self):
        return self.frametime, self.camera_frame

    def stop(self):
        self.stopped = True
        sleep(0.3)
        return

    def __delete__(self):
        self.stop()