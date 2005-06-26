import test, widgets, wx, dummy

class VirtualListCtrlTestCase(test.wxTestCase):
    def getItemText(self, index, column):
        return 'Dummy text'
    
    def getItemImage(self, index):
        return -1
    
    def getItemAttr(self, index):
        return wx.ListItemAttr()
        
    def onSelect(self, *args):
        pass
        
    def createListCtrl(self, nrColumns=3):
        return widgets.ListCtrl(self.frame, self.createColumns(nrColumns),
            self.getItemText, self.getItemImage, self.getItemAttr, self.onSelect, 
            dummy.DummyUICommand())
            
    def createColumns(self, nrColumns):
        columns = []
        for columnIndex in range(1, nrColumns+1):
            columns.append('column%d'%columnIndex)
        return columns

    def setUp(self):
        self.listctrl = self.createListCtrl(nrColumns=3)
            
    def testOneItem(self):
        self.listctrl.refresh(1)
        self.assertEqual(1, self.listctrl.GetItemCount())

    def testNrOfColumns(self):
        self.assertEqual(3, self.listctrl.GetColumnCount())
            
    def testCurselection_EmptyList(self):
        self.assertEqual([], self.listctrl.curselection())
        
    def testShowColumn_Hide(self):
        self.listctrl.showColumn('column2', False)
        self.assertEqual(2, self.listctrl.GetColumnCount())
        
    def testShowColumn_HideAndShow(self):
        self.listctrl.showColumn('column2', False)
        self.listctrl.showColumn('column2', True)
        self.assertEqual(3, self.listctrl.GetColumnCount())
        
    def testShowColumn_ColumnOrderIsKept(self):
        self.listctrl.showColumn('column2', False)
        self.listctrl.showColumn('column3', False)
        self.listctrl.showColumn('column2', True)
        self.listctrl.showColumn('column3', True)
        self.assertEqual('column2', self.listctrl.getColumnHeader(1))
        self.assertEqual('column3', self.listctrl.getColumnHeader(2))
        
    def testShowColumn_HideTwice(self):
        self.listctrl.showColumn('column2', False)
        self.listctrl.showColumn('column2', False)
        self.assertEqual(2, self.listctrl.GetColumnCount())