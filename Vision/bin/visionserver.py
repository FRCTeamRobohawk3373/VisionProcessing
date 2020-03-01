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
import socket
from networktables import NetworkTables
from networktables.util import ntproperty
import numpy as np

class VisionServer:
    PARENT_NAME = "vision"

    #switching camera ntTable
    SUBTABLE_STREAM_NAME = "switching"
    STREAM_CAM_MAP = "CamMap"

    STREAM_READER_SELECTED_CAM_NUM = "selectedCamIndex"
    STREAM_READER_SELECTED_CAM_NAME = "selectedCamName"
    STREAM_SETTER_ACTIVE_CAM_NUM =  "activeCamIndex"
    STREAM_SETTER_ACTIVE_CAM_NAME = "activeCamName"

    #proccesing camera ntTable
    SUBTABLE_DATA_NAME = "processing"
    DATA_SETTER_TARGET_INFO = "targetInfo"

    
    def __init__(self, debug=False):
        self.areDebugging=debug

        self.logger=logging.getLogger("server")

        #Load the json config file
        self.config = self.loadConfig()

        #Start the camera Server
        self.cameraServer = cscore.CameraServer.getInstance()
        self.cameraServer.enableLogging()

        self.activeCamera={"index":-1, "name":""}
        self.streamingCams=[]  
        self.visionCams=[]

        #self.activeCam = None
        #self.currentCam = None
        
        cams = self.findCameras()
        self.startCameras(cams)

        self.switchingServer = self.createOutputStream()
        
        #NetworkTables
        self.setUpNetworkTables()

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

    def startCameras(self, cameras):
        for camera in cameras:
            cam = cameras[camera]
            if(cam["destinations"]["streamVideo"] or cam["destinations"]["processVideo"]):
                #camType=None
                visionThread = None
                newCamera=USBCamera(self.cameraServer, cam, const.DEFAULT_RESOLUTION)
                camDict={
                    "camera": newCamera,
                    "switchIndex": cam["destinations"]["switchIndex"], 
                    "isConnected": newCamera.isConnected,
                    "name": cam["name"],
                    "id": camera
                }

                if(cam["destinations"]["streamVideo"] and cam["destinations"]["processVideo"]):
                    self.logger.warning("{0}({1}) is configured to stream and process".format(camera, cam["name"]))

                if(cam["destinations"]["streamVideo"]):
                    self.logger.debug("adding "+camDict["name"]+" to streaming cameras")
                    if(len(self.streamingCams)==0):
                        print("first streaming")
                        self.streamingCams.append(camDict)
                    else:
                        added=False
                        for i,item in enumerate(self.streamingCams):
                            if(item["switchIndex"]>camDict["switchIndex"]):
                                print("cam has smaller index. adding at "+str(i))
                                self.streamingCams.insert(i,camDict)
                                added=True
                                break

                        if(not(added)):
                            self.streamingCams.append(camDict)
                
                if(cam["destinations"]["processVideo"]):
                    newCamera.start()   
                    self.logger.info("Starting "+camera+" vision Thread")
                    visionThread = processing.ProcessingThread(self.areDebugging)
                    visionThread.setCamera(newCamera)
                    visionThread.run()
                    camDict["processing"] = visionThread
                    self.logger.debug("adding "+camDict+" to vision cameras")
                    self.visionCams.append(camDict)

    def setUpNetworkTables(self):
        self.parentTable = NetworkTables.getTable(VisionServer.PARENT_NAME)
        self.streamTable = self.parentTable.getSubTable(VisionServer.SUBTABLE_STREAM_NAME)
        cams = []
        for cam in self.streamingCams:
            cams.append([str(cam["switchIndex"]), cam["name"]])

        self.logger.info("Available streaming cameras: "+str(cams))

        self.streamTable.putStringArray(VisionServer.STREAM_CAM_MAP, cams)
        if(len(self.streamingCams)>0):
            self.streamTable.putNumber(VisionServer.STREAM_READER_SELECTED_CAM_NUM, self.streamingCams[0]["switchIndex"])
            self.streamTable.putString(VisionServer.STREAM_READER_SELECTED_CAM_NAME, self.streamingCams[0]["name"])
            self.streamTable.putNumber(VisionServer.STREAM_SETTER_ACTIVE_CAM_NUM, -1)
            self.streamTable.putString(VisionServer.STREAM_SETTER_ACTIVE_CAM_NAME, "")

        else:
            self.streamTable.putNumber(VisionServer.STREAM_READER_SELECTED_CAM_NUM, -1)
            self.streamTable.putString(VisionServer.STREAM_READER_SELECTED_CAM_NAME, "")
            self.streamTable.putNumber(VisionServer.STREAM_SETTER_ACTIVE_CAM_NUM, -1)
            self.streamTable.putString(VisionServer.STREAM_SETTER_ACTIVE_CAM_NAME, "")


        self.processingTable = self.parentTable.getSubTable(VisionServer.SUBTABLE_DATA_NAME)
        self.processingTable.putStringArray(VisionServer.DATA_SETTER_TARGET_INFO,[])
    
    def addCamera(self, cameraName):
        if(cameraName not in self.cameras):
            pass

            #if(self.switchingCamera.getSource() is None and (camType=="BOTH" or camType=="STREAM")):
            #    self.switchingCamera.setSource(self.cameras[camera]["camera"])

    def createOutputStream(self):
        #Create the MJPEG server

        #give the stream a blank stream to give it the name we want
        blankFrame = cscore.CvSource(const.STREAM_NAME, cscore.VideoMode.PixelFormat.kMJPEG,
                                     const.STREAM_RESOLUTION[0], const.STREAM_RESOLUTION[1],
                                     const.STREAM_FPS)

        self.cameraServer.addCamera(blankFrame)
        server = self.cameraServer.addServer(name="serve_" + blankFrame.getName())
        self.cameraServer._fixedSources[server.getHandle()] = blankFrame #! The only thing that actualy makes this work and it is stupid and wrong. DO NOT DO UNLESS NECESSARY! (Remove if addSwitchedCamera() works) Breaks PEP 8 guidelines
        server.setSource(blankFrame)

        return server

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
        
        self.logger.debug(cam+" added to "+ const.CONFIG_FILE)
        self.saveConfig(self.config)

    def switchCameras(self, cam):
        
        self.switchingServer.setSource(cam)

    def run(self):
        #Main Loop.
        while True:
            selectedIndex = int(self.streamTable.getNumber(VisionServer.STREAM_READER_SELECTED_CAM_NUM,-1))
            selectedName = self.streamTable.getString(VisionServer.STREAM_READER_SELECTED_CAM_NAME,None)
            
            if(not(selectedIndex == self.activeCamera["index"])):
                self.logger.debug("Attempting to switch cameras to index: "+str(selectedIndex))
                found = False
                for item in self.streamingCams:
                    if(item["switchIndex"] == selectedIndex):
                        self.logger.info("switching to camera {0}({1}) with index {2}".format(item["id"], item["name"], item["switchIndex"]))
                        found = True
                        self.activeCamera["index"] = selectedIndex
                        self.activeCamera["name"] = item["name"]
                        self.switchCameras(item["camera"].getSource())
                        break

                if(not(found)):
                    if(selectedIndex<len(self.streamingCams) and selectedIndex >= 0):
                        item = self.streamingCams[selectedIndex]
                        self.logger.info("switching to camera {0}({1}) with index {2}".format(item["id"], item["name"], item["switchIndex"]))
                        found = True
                        self.activeCamera["index"] = selectedIndex
                        self.activeCamera["name"] = item["name"]
                        self.switchCameras(item["camera"].getSource())

                if(not(found)):
                    self.logger.info("unable to find camera with index {0}".format(selectedIndex))
                
                self.streamTable.putNumber(VisionServer.STREAM_READER_SELECTED_CAM_NUM, self.activeCamera["index"])
                self.streamTable.putString(VisionServer.STREAM_READER_SELECTED_CAM_NAME, self.activeCamera["name"])
                    

            elif(not(selectedName == self.activeCamera["name"])):
                self.logger.debug("Attempting to switch cameras to name: \""+str(selectedName)+"\"")
                found = False
                for item in self.streamingCams:
                    if(item["name"] == selectedName):
                        self.logger.info("switching to camera {0}({1}) with index {2}".format(item["id"], item["name"], item["switchIndex"]))
                        found = True
                        self.activeCamera["index"] = item["switchIndex"]
                        self.activeCamera["name"] = item["name"]
                        self.switchCameras(item["camera"].getSource())
                        break

                if(not(found)):
                    self.logger.info("unable to find camera with name \"{0}\"".format(selectedName))
                
                self.streamTable.putNumber(VisionServer.STREAM_READER_SELECTED_CAM_NUM, self.activeCamera["index"])
                self.streamTable.putString(VisionServer.STREAM_READER_SELECTED_CAM_NAME, self.activeCamera["name"])
                    

            #self.streamTable.putNumber(VisionServer.STREAM_READER_SELECTED_CAM_NUM, self.streamingCams[0]["switchIndex"])
            #self.streamTable.putString(VisionServer.STREAM_READER_SELECTED_CAM_NAME, self.streamingCams[0]["name"])
            
            self.streamTable.putNumber(VisionServer.STREAM_SETTER_ACTIVE_CAM_NUM, self.activeCamera["index"])
            self.streamTable.putString(VisionServer.STREAM_SETTER_ACTIVE_CAM_NAME, self.activeCamera["name"])

            """  if (not(self.currentCamIndex == self.activeCamIndex)):
            self.currentCamIndex = self.activeCamIndex
            self.logger.info("switching camera to "+self.activeCam["name"])
            self.switchCameras(self.activeCam["camera"].getSource())
            pass
            """
            time.sleep(1)
        
        '''switchTime = time.time()+5
        cams = list(self.cameras.keys())
        print(cams)
        index=0
        while True:
            time.sleep(1)
            if(time.time()>switchTime):
                if(self.cameras[cams[index]]["type"]=="STREAM"):
                    print("setting camera to "+cams[index])
                    self.switchCameras(self.cameras[cams[index]]["camera"].getSource())
                    switchTime = time.time()+5

                index = index + 1
                if(index>=len(cams)):
                    index=0
            
            time.sleep(0.01)
            #cv2.waitKey(10)'''

def getHostNameAndIP(): 
    try: 
        host_name = socket.gethostname() 
        host_ip = socket.gethostbyname(host_name+".local") 
        
        logging.info("Hostname: " + host_name + ", IP: " + host_ip) 
    except: 
        logging.warning("Unable to get Hostname and IP") 


def exceptionHandler(exc_type, exc_value, exc_traceback):
    logging.critical("Uncaught exception:",exc_info=(exc_type, exc_value, exc_traceback))

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
    getHostNameAndIP()

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