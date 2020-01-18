from Shuffleboard.ShuffleboardComponent import Component

class ComplexWidget(Component):
    def __init__(self, parent, title):
        super().__init__(parent, title, None)

    def buildInto(self, parent, metaTable):
        self.buildMetadata(metaTable)

            
class DropdownWidget(ComplexWidget):
    def __init__(self, parent, title):
        pass