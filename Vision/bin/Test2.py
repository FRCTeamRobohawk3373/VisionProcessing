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

    yPosDropdown = shuffle.addDropdown(["move up", "move down"]).getEntry()

    tt1 = shuffle.getTab("test")
    print("On tab '"+tt1.getTitle()+"'")
    num = tt1.addNumber("testNumber", 2.0).getEntry()
    bol = tt1.addBoolean("testBool", True).withWidget(WidgetTypes.BOOLEANBOX).withProperties({"Color when true":"#FFFFFF","Color when false":"#000000"}).getEntry()
    string = tt1.addString("Dropdown Value", " - - - ").withPosition(5, 4).getEntry()

    def myListener(value):
        if value == "Aa":
            shuffle.selectTab("test")
        elif value == "Bb":
            shuffle.getTab("testB")
            shuffle.selectTab("testB")
        elif value == "Ccc":
            shuffle.getTab("test").addString("greeting", "haseyo").withPosition(4, 4).getEntry()
        else:
            print("Value changed to "+value)

        string.setString(value)
        

    dropdown = shuffle.getTab("test").addDropdown("testChooser", ["Aa","Bb","Ccc","Dd","Ee"])\
        .withDefault("Bb")\
        .withActive("Aa")\
        .withSelected("Ee")\
        .withListener(myListener)\
        .getEntry()
    

    shuffle.selectTab("test")
    
    i = 0
    dir=1
    try:
        while True:
            time.sleep(0.5)
            bol.setBoolean(not bol.getBoolean(False))

            num.setNumber(i)


            #string.withPosition(5, i/2)
            shuffle.update()

            i+=dir
            if(i >= 10):
                dir = -1
            elif(i < 1):
                dir = 1
    except KeyboardInterrupt:
        print("Exited")


    print("NetworkTables is connected: "+str(NetworkTables.isConnected()))
 
    NetworkTables.flush()
    time.sleep(1)
    NetworkTables.shutdown()