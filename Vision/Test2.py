from networktables import NetworkTables
import logging
import time
from Suffleboard import Suffleboard

if __name__ == '__main__':
    print("started")
    NetworkTables.startClient('127.0.0.1')
    print(NetworkTables.isConnected())
    for i in range(5):
        if(NetworkTables.isConnected()):
            print("Connected")
            break
        print("Failed to Connect")
        time.sleep(1)

    nt = NetworkTables.getDefault()
    suffle = Suffleboard.ShuffleboardInstance(nt)

    tab = suffle.getTab("test")
    print(tab.getTitle())
    suffle.update()

    suffle.selectTab("test")



    


    test = nt.getTable("/test")
    test.putNumber('test',2)

    # sd = NetworkTables.getTable("/Shuffleboard")
    # meta= sd.getSubTable(".metadata")
    # entry=meta.getEntry("Selected")
    # meta.putNumber("test",2)

    print(NetworkTables.isConnected())
    # sd.putNumber('aNumber', 1234)
    # print(NetworkTables.waitForConnectionListenerQueue(5))
    # otherNumber = sd.getNumber('aNumber', 0)
    # print(otherNumber)
    # print(NetworkTables.waitForConnectionListenerQueue(5))
    # for i in range(5):
    #     if(NetworkTables.isConnected()):
    #         print("Connected")
    #         break
    #     print("Failed to Connect")
    #     time.sleep(1)

    NetworkTables.flush()
    time.sleep(1)
    NetworkTables.shutdown()