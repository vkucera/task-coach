import test, widgets

class VirtualListCtrlTestCase(test.wxTestCase):
    def setUp(self):
        self.listctrl = widgets.listctrl.VirtualListCtrl(self.frame, 
            ['column1', 'column2', 'column3'], None, None, None)
            
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