class WidgetTypes:
    TEXTVIEW = "Text View"
    NUMBERSLIDER = "Number Slider"
    NUMBERBAR = "Number Bar"
    DIAL = "Simple Dial"
    GRAPH = "Graph"
    BOOLEANBOX = "Boolean Box"
    TOGGLEBUTTON = "Toggle Button"
    TOGGLESWITCH = "Toggle Switch"
    COMBOBOXCHOOSER = "ComboBox Chooser"
    SPLITBUTTONCHOOSER = "Split Button Chooser"
    SPEEDCONTROLLER = "Speed Controller"
    COMMAND = "Command"
    CAMERASTREAM = "Camera Stream"
    SHUFFLEBOARDLAYOUT = "ShuffleboardLayout"

    def getProperties(type):
        types = {
            WidgetTypes.TEXTVIEW: {},
            WidgetTypes.NUMBERSLIDER: {'Min':float,'Max':float,'Block increment':float},
            WidgetTypes.NUMBERBAR: {'Min':float,'Max':float,'Center':float},
            WidgetTypes.DIAL: {'Min':float,'Max':float,'Show value':bool},
            WidgetTypes.GRAPH: {'Visible time':float},
            WidgetTypes.BOOLEANBOX: {'Color when true':str,'Color when false':str},
            WidgetTypes.TOGGLEBUTTON: {},
            WidgetTypes.TOGGLESWITCH: {},
            WidgetTypes.COMBOBOXCHOOSER: {},
            WidgetTypes.SPLITBUTTONCHOOSER: {},
            WidgetTypes.SPEEDCONTROLLER: {},
            WidgetTypes.COMMAND: {},
            WidgetTypes.CAMERASTREAM: {},
            WidgetTypes.SHUFFLEBOARDLAYOUT: {}
        }
        if(type in types):
            return types[type]

        else:
            return None


class Component:
    def __init__(self, parent, title, wType=None):
        self.size = (-1,-1) #width,height
        self.position = (-1,-1) #column,row
        self.properties = {}
        self.dataUpdated=True
        self.title = title
        self.type = wType
        self.parent = parent
        
    def getParent(self):
        return self.parent

    def setType(self, wType):
        self.type = wType
        self.dataUpdated = True

    def getTitle(self):
        return self.title

    def getProperties(self):
        return self.properties

    def withProperties(self, prop):
        validProps = WidgetTypes.getProperties(self.type)

        for p in prop:
            if p in validProps:
                if type(p) == validProps[p]:
                    continue
                else:
                    raise TypeError("must be "+str(validProps[p])+", not "+str(type(p)))
            else:
                raise NameError("invalid property "+p)

        self.properties = prop
        self.dataUpdated = True
        return self

    def withPosition(self, col, row):
        self.position = (col, row) #this order, not (row, col)
        self.dataUpdated = True
        return self

    def withSize(self, width, height):
        self.size = (width, height)
        self.dataUpdated = True
        return self  

    def buildMetadata(self, metaTable):
        if(not self.dataUpdated):
            return
        
        if(self.type == None):
            metaTable.getEntry("PreferredComponent").delete()
        else:
            metaTable.getEntry("PreferredComponent").forceSetString(self.type)

        if(self.size[0] <= 0 or self.size[1] <= 0):
            metaTable.getEntry("Size").delete()
        else:
            metaTable.getEntry("Size").setDoubleArray(list(self.size))

        if(self.position[0] < 0 or self.position[1] < 0):
            metaTable.getEntry("Position").delete()
        else:
            metaTable.getEntry("Position").setDoubleArray(list(self.position))

        if(self.getProperties != None):
            propTable = metaTable.getSubTable("Properties")
            for prop in self.properties:
                propTable.getEntry(prop).setValue(self.properties[prop])

        self.dataUpdated = False
