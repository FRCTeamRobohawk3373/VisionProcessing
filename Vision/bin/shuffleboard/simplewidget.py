from Shuffleboard.shuffleboardComponent import Component
from Shuffleboard.shuffleboardLayout import Layout

class SimpleWidget(Component):
    def __init__(self, parent, title):
        self.entry = None
        super().__init__(parent, title, None)

    def getEntry(self):
        if self.entry is None:
            self.forceGenerate()
        return self.entry

    def withWidget(self, wType):
        self.setType(wType)
        return self

    def forceGenerate(self):
        parent = self.getParent()
        
        while isinstance(parent, Layout):
            parent = parent.getParent()

        parent.getRoot().update()
    
    def buildInto(self, parentTable, metaTable):
        self.buildMetadata(metaTable)
        if (self.entry is None):
            self.entry = parentTable.getEntry(self.getTitle())
        
