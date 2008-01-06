import widgets, wx, TreeCtrlTest
import unittests.dummy as dummy

class TreeListCtrlTestCase(TreeCtrlTest.TreeCtrlTestCase):
    def setUp(self):
        super(TreeListCtrlTestCase, self).setUp()
        self.createColumns()
        self.treeCtrl = widgets.TreeListCtrl(self.frame, self.columns(), 
            self.getItemText, self.getItemTooltipText, self.getItemImage,
            self.getItemAttr, self.getChildrenCount, self.getItemExpanded,
            self.onSelect, dummy.DummyUICommand(), dummy.DummyUICommand())
        imageList = wx.ImageList(16, 16)
        for bitmapName in ['task', 'tasks']:
            imageList.Add(wx.ArtProvider_GetBitmap(bitmapName, wx.ART_MENU, 
                          (16,16)))
        self.treeCtrl.AssignImageList(imageList)

    def createColumns(self):
        names = ['treeColumn'] + ['column%d'%index for index in range(1, 5)]
        self._columns = [widgets.Column(name, name, ('view', 'whatever'), None) for name in names]
        
    def columns(self):
        return self._columns
    
    def getItemText(self, index, column=None):
        itemText = super(TreeListCtrlTestCase, self).getItemText(index)
        if column is None:
            return itemText
        else:
            return '%s in column %s'%(itemText, column)
    
    def getItemImage(self, index, which, column=None):
        return super(TreeListCtrlTestCase, self).getItemImage(index)
    
    
class TreeListCtrlTest(TreeListCtrlTestCase, TreeCtrlTest.CommonTests):
    pass


class TreeListCtrlColumnsTest(TreeListCtrlTestCase):
    def setUp(self):
        super(TreeListCtrlColumnsTest, self).setUp()
        self.setTree('item')
        self.treeCtrl.refresh(1)
        self.visibleColumns = self.columns()[1:]
        
    def assertColumns(self):
        self.assertEqual(len(self.visibleColumns)+1, self.treeCtrl.GetColumnCount())
        item, cookie = self.treeCtrl.GetFirstChild(self.treeCtrl.GetRootItem())
        for columnIndex in range(1, len(self.visibleColumns)):
            self.assertEqual(self.getItemText((0,), columnIndex), 
                             self.treeCtrl.GetItemText(item, columnIndex))
    
    def showColumn(self, name, show=True):
        column = widgets.Column(name, name, ('view', 'whatever'), None)
        self.treeCtrl.showColumn(column, show)
        if show:
            index = self.columns()[1:].index(column)
            self.visibleColumns.insert(index, column)
        else:
            self.visibleColumns.remove(column)
    
    def testAllColumnsVisible(self):
        self.assertColumns()
        
    def testHideColumn(self):
        self.showColumn('column1', False)
        self.assertColumns()
        
    def testHideLastColumn(self):
        lastColumnHeader = 'column%d'%len(self.visibleColumns)
        self.showColumn(lastColumnHeader, False)
        self.assertColumns()
        
    def testShowColumn(self):
        self.showColumn('column2', False)
        self.showColumn('column2', True)
        self.assertColumns()
        
