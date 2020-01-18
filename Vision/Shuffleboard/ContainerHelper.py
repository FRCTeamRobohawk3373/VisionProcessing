from Shuffleboard.SimpleWidget import SimpleWidget
from Shuffleboard.ComplexWidget import ComplexWidget

class Helper:
    def __init__(self, container):
        self.usedTitles = []
        self.components = []
        self.layouts = {}
        
        self.container = container

    def getComponents(self):
        return self.components
    
    def getLayout(self, title, lType=None):
        if (not(self.layouts.containsKey(title))):
            if(lType is None):
                raise NameError("No Layout with name "+title)

            layout = ShuffleboardLayout(self.container, lType, title)
            self.components.append(layout)
            self.layouts[title] = layout

        return layouts[title]

    def addBoolean(self, title, value):
        self.checkTitle(title)
        return self.addSupplied(title, value)

    def addBooleanArray(self, title, arr):
        self.checkTitle(title)
        return self.addSupplied(title, arr)

    def addNumber(self, title, value):
        self.checkTitle(title)
        return self.addSupplied(title, value)
    
    def addNumberArray(self, title, arr):
        self.checkTitle(title)
        return self.addSupplied(title, arr)

    def addString(self, title, value):
        self.checkTitle(title)
        return self.addSupplied(title, value)
    
    def addStringArray(self, title, arr):
        self.checkTitle(title)
        return self.addSupplied(title, arr)

    def addSupplied(self, title, value):
        widget = SimpleWidget(self.container, title)
        self.components.append(widget)
        widget.getEntry().setValue(value)
        
        return widget

    def checkTitle(self, title):
        if(title in self.usedTitles):
            raise NameError("Title is already is use: "+title)
        self.usedTitles.append(title)



