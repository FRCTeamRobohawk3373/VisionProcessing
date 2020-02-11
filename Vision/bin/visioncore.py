import json
import cv2
from drivers.usbcamera import USBCamera
from os import listdir
import time
import processing

config = {}
cameraPath = "/dev/v4l/by-id"
configFile = "../etc/config.json"
backupFile = "../etc/config.json.bak"
streamCams = []
processCams = []


def loadConfig(cfile=configFile):
    with open(cfile, 'r') as f:
        return json.load(f)


def loadBackup(bfile=backupFile):
    bak = loadConfig(bfile)
    saveConfig(bak, backup=False)



def saveConfig(config, cfile=configFile, backup=True, bfile=backupFile):
    if (backup):
        with open(cfile, 'r') as c:
            with open(bfile, 'w') as b:
                b.writelines(c.readlines())
    with open(cfile, 'w') as f:
        json.dump(config, f, indent=4, sort_keys=True)


def cameraInit(id_):
    return USBCamera(config["cameras"][id_])


def setupCameras():
    ids = listdir(cameraPath)
    for id_ in ids:
        if id_[-1] == "1":
            continue
        try:
            destinations = config["cameras"][id_]["destinations"]
        except KeyError:
            print("Setting up camera id {}.".format(id_))
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
            continue
        print("Camera id {} initializing".format(id_))
        if destinations["streamVideo"]:
            streamCams.append(cameraInit(id_))
        elif destinations["processVideo"]:
            processCams.append(cameraInit(id_))

    saveConfig(config)


if __name__ == '__main__':
    config = loadConfig()
    setupCameras()

    for camera in streamCams:
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

    cv2.destroyAllWindows()
