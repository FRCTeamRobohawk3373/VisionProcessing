from shuffleboard.component import Component

class Layout(Component):
    def __init__(self, parent, name, lType):
        self.helper = Helper(self)
        super().__init__(parent, name, "ShuffleboardLayout")
        
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
        self.buildMetadata(metaTable)
        table = parentTable.getSubTable(self.getTitle())
        table.getEntry(".type").setString("ShuffleboardLayout")
        for c in self.getComponents():
            component.buildInto(table, meta.getSubTable(component.getTitle()))

