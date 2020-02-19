import json
import cv2
from drivers.usbcamera import USBCamera
from os import listdir
import time
import processing
import logging
import constants as const
import sys
import cscore
from networktables import NetworkTables



class VisionServer:
    def __init__(self, debug=False):
        self.areDebugging=debug

        self.logger=logging.getLogger("server")

        #Load the json config file
        self.config = self.loadConfig()

        #Start the camera Server
        self.cameraServer = cscore.CameraServer.getInstance()
        self.cameraServer.enableLogging()

        self.cameras={}
        self.active_camera = None

        cams = self.findCameras()
        self.startCameras(cams)

        #setupCameras(cameras)

    def findCameras(self):
        cams = {}
        for cam in listdir(const.CAMERA_PATH):
            if("index0" in cam):
                if(cam in self.config["cameras"]):
                    self.logger.info(cam+" was found in config with name \""+self.config["cameras"][cam]["name"]+"\"")
                else:
                    self.logger.info(cam+" was not found in config! Adding...")
                    self.addCamToConfig(cam)

                cams[cam] = self.config["cameras"][cam]
        
        for configedCam in self.config["cameras"]:
            if(configedCam not in cams):
                if(True in self.config["cameras"][configedCam]["destinations"].values()):
                    self.logger.warning(configedCam+"("+self.config["cameras"][configedCam]["name"]+")"+" is not connected, but is used!")
        
        return cams

    def startCameras(self, cams):
        for camera in cams:
            cam = cams[camera]
            if(cam["destinations"]["streamVideo"] and cam["destinations"]["processVideo"]):
                self.logger.warning("{0}({1}) is configured to stream and process".format(camera, cam["name"]))
                camType="BOTH"
            elif(cam["destinations"]["streamVideo"]):
                camType="STREAM"
            elif(cam["destinations"]["processVideo"]):
                camType="VISION"

            self.cameras[camera]={"camera": USBCamera(self.cameraServer, cam), "switchIndex": cam["destinations"]["switchIndex"], "type": "stream", "isConnected": True}


    def loadConfig(self, cfile=const.CONFIG_FILE):
        with open(cfile, 'r') as f:
            return json.load(f)

    def loadBackup(self, bfile=const.BACKUP_FILE):
        bak = loadConfig(bfile)
        saveConfig(bak, backup=False)

    def saveConfig(self, config, cfile=const.CONFIG_FILE, backup=True, bfile=const.BACKUP_FILE):
        if (backup):
            with open(cfile, 'r') as c:
                with open(bfile, 'w') as b:
                    b.writelines(c.readlines())
        with open(cfile, 'w') as f:
            json.dump(config, f, indent=4, sort_keys=True)

    def addCamToConfig(self, cam):
        self.config["cameras"][cam] = {
                "path": "/dev/v4l/by-id/" + cam,
                "name": cam,
                "properties": {},
                "settings": {},
                "destinations": {
                    "streamVideo": False,
                    "processVideo": False,
                    "switchIndex": -1
                },
                "cameraMatrix": [],
                "distortionCoefficients": []
            }
        
        logger.debug(cam+" added to "+ const.CONFIG_FILE)
        saveConfig(self.config)

    def run(self):
        #Main Loop.
        while True:
            cv2.waitKey(10)
    
def exceptionHandler(exc_type, exc_value, exc_traceback):
    logging.exception("Uncaught exception:",exc_info=(exc_type, exc_value, exc_traceback))

if __name__ == '__main__':

    #Logging setup
    fileIndex = ""
    if(const.LOG_SEPERATE_FILES):
        fileIndex=len(listdir(const.LOG_BASE_PATH))
    
    logging.basicConfig(level=const.LOG_LEVEL, 
                        filename=const.LOG_BASE_PATH + const.LOG_NAME.format(fileIndex), 
                        format='%(asctime)s: [%(levelname)-8s] -> %(name)s : %(message)s')

    console = logging.StreamHandler()
    console.setLevel(const.LOG_LEVEL_CONSOLE)

    formatter = logging.Formatter('[%(levelname)-8s] -> %(name)s : %(message)s')
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)
    logging.info("############# Vision Started #############")
    logging.info("OpenCV Version: {0}".format(cv2.__version__))
    logging.info("CSCore Version: {0}".format(cscore.__version__))
    #logging.info("NetworkTables Version: {0}".format(NetworkTables.__version__))

    sys.excepthook = exceptionHandler

    if(const.IS_TESTING):
        #if(const.LOG_LEVEL == logging.DEBUG or const.LOG_LEVEL_CONSOLE==logging.DEBUG):
            #NetworkTables.enableVerboseLogging()

        NetworkTables.startServer()

    else:
        #if(const.LOG_LEVEL == logging.DEBUG or const.LOG_LEVEL_CONSOLE==logging.DEBUG):
            #NetworkTables.enableVerboseLogging()
        
        NetworkTables.startClientTeam(const.TEAM_NUMBER)

    server = VisionServer(debug=const.IS_TESTING)

    server.run()