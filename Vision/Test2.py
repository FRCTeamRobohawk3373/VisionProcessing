from networktables import NetworkTables
import logging
import time
from Shuffleboard import Shuffleboard
from Shuffleboard.ShuffleboardComponent import WidgetTypes

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
    shuffle = Shuffleboard.ShuffleboardInstance(nt)

    tab = shuffle.getTab("test")
    print(tab.getTitle())
    num = shuffle.getTab("test").addNumber("testNumber", 2.0).getEntry()
    bol = shuffle.getTab("test").addBoolean("testBool", True).withWidget(WidgetTypes.BOOLEANBOX).withProperties({"Color when true":"#FFFFFF","Color when false":"#000000"}).getEntry()
    string = shuffle.getTab("test").addString("testStr", "This is a Test").withPosition(5, 4)
    
    # shuffle.update()

    shuffle.selectTab("test")
    
    i = 0
    dir=1
    while True:
        time.sleep(0.5)
        bol.setBoolean(not bol.getBoolean(False))
        num.setNumber(num.getNumber(-2)+1)
        string.getEntry().setString(string.getEntry().getString("")+"|"+str(i))

        #string.withPosition(5, i/2)
        shuffle.update()

        i+=dir
        if(i >= 10):
            dir = -1
        elif(i < 1):
            dir = 1
        

        
    


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