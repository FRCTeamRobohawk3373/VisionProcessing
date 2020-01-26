from shuffleboard.component import Component
from shuffleboard.layout import Layout

class ComplexWidget(Component):
    def __init__(self, parent, title):
        self.entry = None
        super().__init__(parent, title, None)

    def buildInto(self, parent, metaTable):
        self.buildMetadata(metaTable)


class DropdownWidget(ComplexWidget):
    def __init__(self, parent, title):
        super().__init__(parent, title)
        self.options = []
        self.active = None
        self.default = None
        self.selected = None
        self.onChoice = None   
        self._selectionHandler = None
 
    def _handleOnChange(self, table, key, value, isNew):
        if key == "selected":
            if self._selectionHandler is not None:
                self._selectionHandler(value)
        

    def withListener(self, onSelected):
        if callable(onSelected):
            self._selectionHandler = onSelected
            self.getEntry().addTableListener(self._handleOnChange, True)
        else:
            raise TypeError(str(type(onSelected))+" object isn't callable")

        return self

    def close(self):#doesn't work rn
        if self.on_choices or self.on_selected:
            self.subtable.removeTableListener(self._on_change)


    def getEntry(self):
        if self.entry is None:
            self.forceGenerate()
        return self.entry

    def withOptions(self, options):
        if options is None:
            raise NameError("No options for DropdownWidget provided")
        
        self.options = options
        self.active = self.default = self.selected = options[0]

        return self

    def withActive(self, value):
        self.active = value
        return self

    def withDefault(self, value):
        self.default = value
        return self

    def withSelected(self, value):
        self.selected = value
        return self

    def buildInto(self, parentTable, metaTable):
        self.buildMetadata(metaTable)
        if (self.entry is None):
            self.entry = parentTable.getSubTable(self.getTitle())
            self.entry.getEntry(".controllable").forceSetBoolean(True)
            self.entry.getEntry(".instance").forceSetString(1.0)
            self.entry.getEntry(".type").forceSetString("String Chooser")
            self.entry.getEntry("active").forceSetString(self.active)
            self.entry.getEntry("default").forceSetString(self.default)
            self.entry.getEntry("selected").forceSetString(self.selected)
            self.entry.getEntry("options").forceSetStringArray(self.options)

    def forceGenerate(self):
        parent = self.getParent()
        
        while isinstance(parent, Layout):
            parent = parent.getParent()

        parent.getRoot().update()
