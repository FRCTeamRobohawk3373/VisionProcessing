import logging
import numpy as np

###############
#   General   #
###############
IS_TESTING = False
TEAM_NUMBER = 3373
DEFAULT_RESOLUTION=(320,240)

#############
#   Paths   #
#############
CAMERA_PATH = "/dev/v4l/by-id"
CONFIG_FILE = "../etc/config.json"
BACKUP_FILE = "../etc/config.json.bak"

#############
#  logging  #
#############
#Log Levels: DEBUG,INFO,WARNING(default),ERROR,CRITICAL
LOG_LEVEL = logging.DEBUG
LOG_LEVEL_CONSOLE = logging.INFO

LOG_BASE_PATH = "../etc/log/"
LOG_NAME="vision{0}.log"
LOG_SEPERATE_FILES = True

###############
#  Streaming  #
###############
STREAM_PORT = 1181
STREAM_RESOLUTION = (320,240)
STREAM_FPS = 15
STREAM_NAME = "stream"
STREAM_DEFAULT_COMPRESSION = -1

################
#  Processing  #
################

#target size
WIDTH_3D = 39.25
HEIGHT_3D = 17

#3D target positions
CORNERS_3D = np.array([
    [-WIDTH_3D/2, HEIGHT_3D/2, 0.0], # top-left
    [WIDTH_3D/2, HEIGHT_3D/2, 0.0],  # top-right
    [WIDTH_3D/2, -HEIGHT_3D/2, 0.0],   # bottom-right
    [-WIDTH_3D/2, -HEIGHT_3D/2, 0.0]   # bottom-left
])

#lower and upper target colors
LOWER_HSV = (50, 39, 55)
UPPER_HSV = (85, 255, 255)

#contour filtering
MIN_AREA = 500
MIN_PERIMETER = 100
SOLIDITY = [8,33]

#distance calculation scaling
DISTANCE_SCALER = 0.793025
DISTANCE_OFFSET = 0.474402

ROBOT_ANGLE_SCALER = 1
ROBOT_ANGLE_OFFSET = 0



