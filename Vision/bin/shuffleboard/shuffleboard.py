from networktables import NetworkTables
import Shuffleboard.shuffleboardTab as ShuffleboardTab

class ShuffleboardInstance():
    BASETABLENAME = "/Shuffleboard"

    def __init__(self, ntInstance):
        self.tabs = {}
        self.tabsChanged = False

        self.rootTable = ntInstance.getTable(ShuffleboardInstance.BASETABLENAME)
        self.rootMetaTable = self.rootTable.getSubTable(".metadata")
        self.selectedTabEntry = self.rootMetaTable.getEntry("Selected")

    def getTab(self, title):
        if(not(title in self.tabs)):
            self.tabs[title] = ShuffleboardTab.Tab(self, title)
            self.tabsChanged = True

        return self.tabs[title]
    
    def selectTab(self, title):
        if(title in self.tabs):
            self.selectedTabEntry.forceSetString(title)

    def update(self):
        if(self.tabsChanged):
            tabTitles = list(self.tabs.keys())
            print(tabTitles)
            self.rootMetaTable.getEntry("Tabs").forceSetStringArray(tabTitles)
            self.tabsChanged=False
            
        for tab in self.tabs.values():
            title = tab.getTitle()
            tab.buildInto(self.rootTable, self.rootMetaTable.getSubTable(title))

