import wx
from taskcoachlib.thirdparty import squaremap


class SquareMap(squaremap.SquareMap):
    def __init__(self, parent, rootNode, onSelect, onEdit):
        self.__selection = []
        super(SquareMap, self).__init__(parent, model=rootNode, adapter=parent)
        self.selectCommand = onSelect
        self.Bind(squaremap.EVT_SQUARE_SELECTED, self.onSelect)
        self.editCommand = onEdit
        self.Bind(squaremap.EVT_SQUARE_ACTIVATED, self.onEdit)
        
    def refresh(self, count):
        self.Refresh()
        
    def onSelect(self, event):
        if event.node == self.model:
            self.__selection = []
        else:
            self.__selection = [event.node]
        wx.CallAfter(self.selectCommand)
        event.Skip()
        
    def select(self, index):
        pass
    
    def onEdit(self, event):
        self.editCommand(event)
        event.Skip()
    
    def curselection(self):
        return self.__selection