import json
import cv2
from drivers.usbcamera import USBCamera
from os import listdir
import time
import processing
import logging
import constants as const
import sys

config = {}

streamCams = []
processCams = []


def loadConfig(cfile=const.CONFIG_FILE):
    with open(cfile, 'r') as f:
        return json.load(f)

def loadBackup(bfile=const.BACKUP_FILE):
    bak = loadConfig(bfile)
    saveConfig(bak, backup=False)

def saveConfig(config, cfile=const.CONFIG_FILE, backup=True, bfile=const.BACKUP_FILE):
    if (backup):
        with open(cfile, 'r') as c:
            with open(bfile, 'w') as b:
                b.writelines(c.readlines())
    with open(cfile, 'w') as f:
        json.dump(config, f, indent=4, sort_keys=True)

def addCamera(cam, config):
    config["cameras"][cam] = {
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
    saveConfig(config)


def setupCameras(cameras):
    for camera in cameras:
        cam = cameras[camera]
        if(cam["destinations"]["streamVideo"]):
            streamCams.append(USBCamera(cam))
        elif(cam["destinations"]["processVideo"]):
            processCams.append(USBCamera(cam))
    pass

    # ids = listdir(const.CAMERA_PATH)
    # for id_ in ids:
    #     if id_[-1] == "1":
    #         continue
    #     try:
    #         destinations = config["cameras"][id_]["destinations"]
    #     except KeyError:
    #         print("Setting up camera id {}.".format(id_))
    #         config["cameras"][id_] = {"path": "/dev/v4l/by-id/" + id_,
    #                                   "name": "",
    #                                   "properties": {},
    #                                   "destinations": {
    #                                       "streamVideo": False,
    #                                       "processVideo": False,
    #                                       "switchIndex": -1
    #                                   },
    #                                   "cameraMatrix": [],
    #                                   "distortionCoefficients": []
    #                                  }
    #         continue
    #     print("Camera id {} initializing".format(id_))
    #     if destinations["streamVideo"]:
    #         streamCams.append(cameraInit(id_))
    #     elif destinations["processVideo"]:
    #         processCams.append(cameraInit(id_))

    # saveConfig(config)
    
def my_handler(exc_type, exc_value, exc_traceback):
    logger.exception("Uncaught exception:",exc_info=(exc_type, exc_value, exc_traceback))

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
    logging.log(45,"############# Vision Started #############")

    sys.excepthook = my_handler

    #logger for this file
    logger=logging.getLogger("main")

    #Load the json config file
    config = loadConfig()

    #identify connected cameras and their config
    cameras={}
    for cam in listdir(const.CAMERA_PATH):
        if("index0" in cam):
            if(cam in config["cameras"]):
                logger.info(cam+" was found in config with name \""+config["cameras"][cam]["name"]+"\"")
            else:
                logger.info(cam+" was not found in config! Adding...")
                addCamera(cam, config)

            cameras[cam] = config["cameras"][cam]
    
    for configCam in config["cameras"]:
        if(configCam not in cameras):
            if(True in config["cameras"][configCam]["destinations"].values()):
                logger.warning(configCam+"("+config["cameras"][configCam]["name"]+")"+" is not connected, but is used!")
                #cameras[configCam]["status"]={"connected":True}

        #else:
            #cameras[configCam]["status"]={"connected":True}
        
                #print(configCam + "is not pluged in")

    setupCameras(cameras)
    #print(config)

    #print(cameras)
    #setupCameras()


    """ for camera in streamCams:
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    while True:
        # Display streaming cameras
        for camera in streamCams:
            frame = camera.read()
            cv2.imshow("{} ({})".format(camera.name, camera.path), frame)

        if cv2.waitKey(1) & 0xff == ord('q'):
            break

        for camera in processCams:
            camera.grab()

    cv2.destroyAllWindows() """
