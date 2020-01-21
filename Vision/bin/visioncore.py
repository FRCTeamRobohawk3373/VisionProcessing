import json
from drivers.usbcamera import USBCamera
from os import listdir
import time

config = {}
cameraPath = "/dev/v4l/"
configFile = "../etc/config.json"
backupFile = "../etc/config.json.bak"
streamCams = []
processCams = []


def loadConfig(cfile=configFile):
    with open(cfile, 'r') as f:
        return json.load(f)


def loadBackup(bfile=backupFile):
    loadConfig(bfile)


def saveConfig(config, cfile=configFile, backup=True, bfile=backupFile):
    with open(cfile, 'w') as f:
        json.dump(config, f)


def cameraInit(id_):
    return USBCamera(config["cameras"][id_])


def setupCameras():
    ids = os.listdir(cameraPath)
    for id_ in ids:
        destinations = config["cameras"][id_]["destinations"]
        if destinations["streamVideo"]:
            streamCams.append(cameraInit(id_))
        else if destinations["processCams"]:
            processCams.append(cameraInit(id_))
        else:
            config["cameras"][id_] = {"path": "/dev/v4l/by-id/" + id_,
                                      "name": "",
                                      "properties": {},
                                      "destinations": {
                                          "streamVideo": False,
                                          "processVideo": False,
                                          "switchIndex": -1
                                      },
                                      "cameraMatrix": [],
                                      "distortionCoefficients": [] 
                                     }
    saveConfig(config)


if __name__ == '__main__':
    config = loadConfig()

    camera1 = cameraInit("usb-046d_0825_88BA4B60-video-index0")
