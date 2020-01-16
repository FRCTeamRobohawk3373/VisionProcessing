import Suffleboard.SuffleboardComponent


class Tab():
    def __init__(self, root, title):
        self.title = title

    def add(self):
        pass

    def getTitle(self):
        return self.title

    def buildInto(self, parentTable, metaTable):
        tabTable = parentTable.getSubTable(self.title)
        tabTable.getEntry(".type").setString("ShuffleboardTab")