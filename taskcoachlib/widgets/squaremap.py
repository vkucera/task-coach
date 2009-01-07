from taskcoachlib.thirdparty import squaremap


class SquareMap(squaremap.SquareMap):
    def __init__(self, parent, rootNode):
        super(SquareMap, self).__init__(parent, model=rootNode, adapter=parent)
        
    def refresh(self, count):
        self.Refresh()
        
    def select(self, index):
        pass
    
    def curselection(self):
        return []