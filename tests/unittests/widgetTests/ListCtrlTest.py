import test, widgets, wx
import unittests.dummy as dummy

class VirtualListCtrlTestCase(test.wxTestCase):
    def getItemText(self, index, column):
        return 'Dummy text'
    
    def getItemImage(self, index):
        return -1
    
    def getItemAttr(self, index):
        return wx.ListItemAttr()
        
    def onSelect(self, *args):
        pass
        
    def createListCtrl(self):
        return widgets.ListCtrl(self.frame, self.columns,
            self.getItemText, self.getItemImage, self.getItemAttr, self.onSelect, 
            dummy.DummyUICommand())
            
    def createColumns(self, nrColumns):
        columns = []
        for columnIndex in range(1, nrColumns+1):
            name = 'column%d'%columnIndex
            columns.append(widgets.Column(name, name, None, None))
        return columns

    def setUp(self):
        self.columns = self.createColumns(nrColumns=3)
        self.listctrl = self.createListCtrl()
            
    def testOneItem(self):
        self.listctrl.refresh(1)
        self.assertEqual(1, self.listctrl.GetItemCount())

    def testNrOfColumns(self):
        self.assertEqual(3, self.listctrl.GetColumnCount())
            
    def testCurselection_EmptyList(self):
        self.assertEqual([], self.listctrl.curselection())
        
    def testShowColumn_Hide(self):
        self.listctrl.showColumn(self.columns[2], False)
        self.assertEqual(2, self.listctrl.GetColumnCount())
        
    def testShowColumn_HideAndShow(self):
        self.listctrl.showColumn(self.columns[2], False)
        self.listctrl.showColumn(self.columns[2], True)
        self.assertEqual(3, self.listctrl.GetColumnCount())
        
    def testShowColumn_ColumnOrderIsKept(self):
        self.listctrl.showColumn(self.columns[1], False)
        self.listctrl.showColumn(self.columns[2], False)
        self.listctrl.showColumn(self.columns[1], True)
        self.listctrl.showColumn(self.columns[2], True)
        self.assertEqual(self.columns[1].header(), self.listctrl._getColumnHeader(1))
        self.assertEqual(self.columns[2].header(), self.listctrl._getColumnHeader(2))
        
    def testShowColumn_HideTwice(self):
        self.listctrl.showColumn(self.columns[2], False)
        self.listctrl.showColumn(self.columns[2], False)
        self.assertEqual(2, self.listctrl.GetColumnCount())
