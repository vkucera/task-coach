import test, widgets
import unittests.dummy as dummy
import wx.grid as grid

class Table(grid.PyGridTableBase):
    def GetRowLabelValue(self, row):
        return 'row %s'%row

        
class GridCtrlTest(test.wxTestCase):
    def setUp(self):
        self.onSelectCalled = False
        table = Table()
        self.gridCtrl = widgets.GridCtrl(self.frame, table, self.onSelect, dummy.DummyUICommand())
        
    def onSelect(self):
        self.onSelectCalled = True
        
    def testInitialSize(self):
        self.assertEqual(0, self.gridCtrl.GetItemCount())
    
    def testRefresh(self):
        self.gridCtrl.refresh(1)
        self.assertEqual('row 0', self.gridCtrl.GetRowLabelValue(0))
        
    def testOnSelect(self):
        self.gridCtrl.refresh(1)
        self.gridCtrl.SelectRow(0)
        self.failUnless(self.onSelectCalled)
