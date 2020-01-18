from Shuffleboard.ShuffleboardComponent import Component
from Shuffleboard.SimpleWidget import SimpleWidget
from Shuffleboard.ComplexWidget import ComplexWidget
from Shuffleboard.ContainerHelper import Helper


class Tab():
    def __init__(self, root, title):
        self.title = title
        self.root = root
        self.helper = Helper(self)

    def getTitle(self):
        return self.title

    def getRoot(self):
        return self.root
        
    def getComponents(self):
        return self.helper.getComponents()

    def getLayout(self, title, lType=None):
        return self.helper.getLayout(title, lType)

    def addBoolean(self, title, value):
        return self.helper.addBoolean(title, value)

    def addBooleanArray(self, title, arr):
        return self.helper.addBooleanArray(title, arr)

    def addNumber(self, title, value):
        return self.helper.addNumber(title, value)
    
    def addNumberArray(self, title, arr):
        return self.helper.addNumberArray(title, arr)

    def addString(self, title, value):
        return self.helper.addString(title, value)
    
    def addStringArray(self, title, arr):
        return self.helper.addStringArray(title, arr)

    def buildInto(self, parentTable, metaTable):
        tabTable = parentTable.getSubTable(self.getTitle())
        tabTable.getEntry(".type").setString("ShuffleboardTab")
        for component in self.getComponents():
            component.buildInto(tabTable,metaTable.getSubTable(component.getTitle()))