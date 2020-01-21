import json


def loadJSON(file='../etc/config.json'):
    with open(file, 'r') as j:
        return json.load(j)


def getCameraSettings(id):
    return {"camera"}


if __name__ == '__main__':
    config = loadJSON()
    print(json.dumps(config, sort_keys=True, indent=4))
