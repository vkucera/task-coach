import test, wx, widgets

class CtrlWithColumnsTestCase(test.wxTestCase):
    def setUp(self):
        self.column1 = widgets.Column('Column 1', 'eventType1')
        self.column2 = widgets.Column('Column 2', 'eventType2')
        self.control = self.createControl()


class CtrlWithHideableColumnsUnderTest(widgets.itemctrl._CtrlWithHideableColumns, wx.ListCtrl):
    pass


class CtrlWithHideableColumnsTests(object):
    def testColumnIsVisibleByDefault(self):
        self.failUnless(self.control.isColumnVisible(self.column1))
        
    def testHideColumn(self):
        self.control.showColumn(self.column1, show=False)
        self.failIf(self.control.isColumnVisible(self.column1))
        
    def testShowColumn(self):
        self.control.showColumn(self.column1, show=False)
        self.control.showColumn(self.column1, show=True)
        self.failUnless(self.control.isColumnVisible(self.column1))
        
        
class CtrlWithHideableColumnsTest(CtrlWithColumnsTestCase, 
                                  CtrlWithHideableColumnsTests):
    def createControl(self):
        return CtrlWithHideableColumnsUnderTest(self.frame, style=wx.LC_REPORT,
            columns=[self.column1, self.column2])
                
        
class CtrlWithSortableColumnsUnderTest( \
        widgets.itemctrl._CtrlWithSortableColumns, wx.ListCtrl):
    pass


class CtrlWithSortableColumnsTests(object):
    def testDefaultSortColumn(self):
        self.assertEqual(self.column1, self.control._currentSortColumn())
        
    def testShowSortColumn(self):
        self.control.showSortColumn(self.column2)
        self.assertEqual(self.column2, self.control._currentSortColumn())


class CtrlWithSortableColumnsTest(CtrlWithColumnsTestCase, CtrlWithSortableColumnsTests):
    def createControl(self):
        return CtrlWithSortableColumnsUnderTest(self.frame, style=wx.LC_REPORT,
            columns=[self.column1, self.column2])            
        
        
class CtrlWithColumnsUnderTest(widgets.itemctrl.CtrlWithColumns, wx.ListCtrl):
    pass


class CtrlWithColumnsTest(CtrlWithColumnsTestCase, 
        CtrlWithHideableColumnsTests, CtrlWithSortableColumnsTests):
    def createControl(self):
	# NOTE: the resizeableColumn is the column that is not hidden
        return CtrlWithColumnsUnderTest(self.frame, style=wx.LC_REPORT,
            columns=[self.column1, self.column2], resizeableColumn=1, 
            columnPopupMenu=None)
                
