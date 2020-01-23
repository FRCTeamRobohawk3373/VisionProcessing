from networktables import NetworkTables
import logging
import time
from shuffleboard import shuffleboard
from shuffleboard.component import WidgetTypes


if __name__ == '__main__':
    print("started")
    NetworkTables.startClient('127.0.0.1')
    print("NetworkTables is connected: "+str(NetworkTables.isConnected()))
    for i in range(5):
        if(NetworkTables.isConnected()):
            print("Connected")
            break
        print("Failed to Connect")
        time.sleep(1)

    nt = NetworkTables.getDefault()
    shuffle = shuffleboard.ShuffleboardInstance(nt)

    tab = shuffle.getTab("test")
    print("On tab '"+tab.getTitle()+"'")
    num = shuffle.getTab("test").addNumber("testNumber", 2.0).getEntry()
    bol = shuffle.getTab("test").addBoolean("testBool", True).withWidget(WidgetTypes.BOOLEANBOX).withProperties({"Color when true":"#FFFFFF","Color when false":"#000000"}).getEntry()
    string = shuffle.getTab("test").addString("testStr", "This is a Test").withPosition(5, 4)

    dropdown = shuffle.getTab("test").addDropdown("testChooser", [1,2,3])
    
    dropdown.withActive(2)
    #dropdown.withDefault(3)#!default doesn't do anything?
    dropdown.withSelected(2)
 



  
    
    # shuffle.update()

    shuffle.selectTab("test")
    
    i = 0
    dir=1
    try:
        while True:
            time.sleep(0.5)
            bol.setBoolean(not bol.getBoolean(False))
            num.setNumber(i)
            string.getEntry().setString(string.getEntry().getString("")+"|"+str(i))

            if i == 7:
                dropdown.withActive(3)
            elif i == 0:
                dropdown.withActive(2)

            #string.withPosition(5, i/2)
            shuffle.update()

            i+=dir
            if(i >= 10):
                dir = -1
            elif(i < 1):
                dir = 1
    except KeyboardInterrupt:
        print("hola amigos")

    test = nt.getTable("/test")
    test.putNumber('test',2)

    print("NetworkTables is connected: "+str(NetworkTables.isConnected()))
 
    NetworkTables.flush()
    time.sleep(1)
    NetworkTables.shutdown()