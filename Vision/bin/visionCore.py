import json
from drivers.usbcamera import USBCamera

config = {}


def loadJSON(file='../etc/config.json'):
    with open(file, 'r') as j:
        return json.load(j)


def cameraInit(id):
    return USBCamera(config["cameras"][id])


if __name__ == '__main__':
    config = loadJSON()
    # print(json.dumps(config, sort_keys=True, indent=4))
    camera1 = cameraInit("usb-046d_0825_88BA4B60-video-index0")
    print(camera1)
