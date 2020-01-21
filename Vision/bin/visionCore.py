import json
from drivers.usbcamera import USBCamera

config = {}
cameraPath = "/dev/v4l/"


def loadConfig(file='../etc/config.json'):
    with open(file, 'r') as j:
        return json.load(j)


def cameraInit(id):
    return USBCamera(config["cameras"][id])


if __name__ == '__main__':
    config = loadConfig()


    camera1 = cameraInit("usb-046d_0825_88BA4B60-video-index0")
