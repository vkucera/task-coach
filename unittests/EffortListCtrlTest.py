import test, widgets, task, wx, dummy

class EffortListCtrlTest(test.wxTestCase):
    def getItemText(self, index, column):
        return 'Dummy text'
    
    def getItemImage(self, index):
        return -1
    
    def getItemAttr(self, index):
        return wx.ListItemAttr()
        
    def onSelect(self, *args):
        pass
        
    def createListCtrl(self, nrColumns=3):
        return widgets.EffortListCtrl(self.frame, ['Column header']*nrColumns,
            self.getItemText, self.getItemImage, self.getItemAttr, self.onSelect, 
            dummy.DummyUICommand())
            
    def testOneTaskWithEffort(self):
        listctrl = self.createListCtrl()
        listctrl.refresh(1)
        self.assertEqual(1, listctrl.GetItemCount())

    def testShowTask(self):
        listctrl = self.createListCtrl(nrColumns=4)
        self.assertEqual(4, listctrl.GetColumnCount())