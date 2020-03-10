import sys
from networktables import NetworkTables
import logging

class NetworkTableManager:
    def __init__(self, address):
        logging.basicConfig(level=logging.DEBUG)
        NetworkTables.startClient(address)
        #NetworkTables.startClientTeam(3373)
        self.ShuffleboardTable = NetworkTables.getTable

    def getTable(self, name):
        return NetworkTables.getTable(name)

    def flush(self):
        NetworkTables.flush()
    
    def shutdown(self):
        NetworkTables.shutdown()