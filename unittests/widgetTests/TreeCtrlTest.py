import test, widgets, wx
import unittests.dummy as dummy
        
class TreeCtrlTestCase(test.wxTestCase):
    def setTree(self, *items):
        self._tree = []
        for item in items:
            if type(item) == type(''):
                itemInfo = (item, 0, item) # subject, nrChildren, Id
            elif len(item) == 2:
                itemInfo = (item[0], item[1], item[0])
            else:
                itemInfo = item
            self._tree.append(itemInfo)
        
    def getItemText(self, index):
        return self._tree[index][0]

    def getItemImage(self, index):
        if self.getChildIndices(index):
            return 1, 1
        else:
            return 0, 0
        
    def getItemAttr(self, index):
        return wx.ListItemAttr()
                        
    def getItemId(self, index):
        return self._tree[index][2]
               
    def getRootIndices(self):
        allIndices = range(len(self._tree))
        allChildIndices = []
        for index in allIndices:
            allChildIndices.extend(self.getChildIndices(index))
        rootIndices = [index for index in allIndices \
                       if index not in allChildIndices]
        return rootIndices
        
    def getChildIndices(self, index):
        nrChildren = self._tree[index][1]
        childIndices = []
        childIndex = index+1
        while nrChildren > 0:
            childIndices.append(childIndex)
            childIndex += self._tree[childIndex][1] + 1
            nrChildren -= 1
        return childIndices
        
    def onSelect(self, *args, **kwargs):
        pass

    def assertTree(self, *items):
        self.setTree(*items)
        self.treeCtrl.refresh()
        self.treeCtrl.expandAllItems()
        self.assertEqual(len(items), self.treeCtrl.GetItemCount())    
        for index, itemInfo in enumerate(items):
            if type(itemInfo) != type((),):
                itemInfo = (itemInfo, 0)
            itemText, nrChildren = itemInfo
            item = self.treeCtrl[index]
            self.assertEqual(itemText, self.treeCtrl.GetItemText(item))
            self.assertEqual(nrChildren, self.treeCtrl.GetChildrenCount(item))
    
    def assertSelection(self, selected=None, notSelected=None):
        if '__WXMAC__' in wx.PlatformInfo:
            wx.Yield()
        for index in selected or []:
            self.failUnless(self.treeCtrl.IsSelected(self.treeCtrl[index]))
        for index in notSelected or []:
            self.failIf(self.treeCtrl.IsSelected(self.treeCtrl[index]))
    
    def setUp(self):
        self._tree = []
        
        
class CommonTests(object):
    ''' Tests common to TreeCtrlTest and TreeListCtrlTest. '''
    
    def testCreate(self):
        self.assertTree()

    def testOneItem(self):
        self.assertTree('item 0')
        
    def testTwoItems(self):
        self.assertTree('item 0', 'item 1')
        
    def testRemoveAllItems(self):
        self.setTree('item 0', 'item 1')
        self.treeCtrl.refresh()
        self.assertTree()

    def testOneParentAndOneChild(self):
        self.assertTree(('item 0', 1), 'item 1')

    def testOneParentAndTwoChildren(self):
        self.assertTree(('item 0', 2), 'item 1', 'item 2')

    def testAddOneChild(self):
        self.setTree(('parent', 1), 'child 1')
        self.treeCtrl.refresh()
        self.assertTree(('parent', 2), 'child 1', 'child 2')

    def testAddingTheFirstChildExpandsParent(self):
        self.setTree('parent')
        self.treeCtrl.refresh()
        self.setTree(('parent', 1), 'child')
        self.treeCtrl.refresh()
        self.failUnless(self.treeCtrl.IsExpanded(self.treeCtrl[0]))
        
    def testAddingTheSecondChildExpandsParent(self):
        self.setTree(('parent', 1), 'child 1')
        self.treeCtrl.refresh()
        self.failIf(self.treeCtrl.IsExpanded(self.treeCtrl[0]))
        self.setTree(('parent', 2), 'child 1', 'child 2')
        self.treeCtrl.refresh()
        self.failUnless(self.treeCtrl.IsExpanded(self.treeCtrl[0]))

    def testDeleteOneChild(self):
        self.setTree(('parent', 2), 'child 1', 'child 2')
        self.treeCtrl.refresh()
        self.assertTree(('parent', 1), 'child 2')
                
    def testReorderItems(self):
        self.setTree('item 0', 'item 1')
        self.treeCtrl.refresh()
        self.assertTree('item 1', 'item 0')

    def testReorderChildren(self):
        self.setTree(('parent', 2), 'child 1', 'child 2')
        self.treeCtrl.refresh()
        self.assertTree(('parent', 2), 'child 2', 'child 1')

    def testReorderParentsAndOneChild(self):
        self.assertTree(('parent', 1), 'child', 'item')
        self.assertTree('item', ('parent', 1), 'child')
        
    def testReorderParentsAndTwoChildren(self):
        self.assertTree(('parent 1', 2), 'child 1', 'child 2', 'parent 2')
        self.assertTree('parent 2', ('parent 1', 2), 'child 2', 'child 1')

    def testReorderParentsAndChildrenDoesNotCollapseParent(self):
        self.setTree('parent', 'item')
        self.treeCtrl.refresh()
        self.setTree(('parent', 2), 'child 1', 'child 2', 'item')
        self.treeCtrl.refresh()
        self.setTree('item', ('parent', 2), 'child 2', 'child 1')
        self.treeCtrl.refresh()
        self.failUnless(self.treeCtrl.IsExpanded(self.treeCtrl[1]))
        
    def testRetainSelectionWhenEditingTask(self):
        self.setTree(('item', 0, 'id'))
        self.treeCtrl.refresh()
        self.treeCtrl.SelectItem(self.treeCtrl[0])
        self.failUnless(self.treeCtrl.IsSelected(self.treeCtrl[0]))
        self.setTree(('new subject', 0, 'id'))
        self.treeCtrl.refresh()
        self.assertSelection(selected=[0])

    def testRetainSelectionWhenEditingSubTask(self):
        self.setTree('parent')
        self.treeCtrl.refresh()
        self.setTree(('parent', 1), ('child', 0, 'childId'))
        self.treeCtrl.refresh()
        self.treeCtrl.SelectItem(self.treeCtrl[1])
        self.failUnless(self.treeCtrl.IsSelected(self.treeCtrl[1]))
        self.setTree(('parent', 1), ('new subject', 0, 'childId'))
        self.treeCtrl.refresh()
        self.assertSelection(selected=[1], notSelected=[0])

    def testRetainSelectionWhenAddingSubTask(self):
        self.setTree('parent')
        self.treeCtrl.refresh()
        self.treeCtrl.SelectItem(self.treeCtrl[0])
        self.setTree(('parent', 1), 'child')
        self.treeCtrl.refresh()
        self.assertSelection(selected=[0], notSelected=[1])

    def testRetainSelectionWhenAddingSubTask_TwoToplevelTasks(self):
        self.setTree('parent', 'item')
        self.treeCtrl.refresh()
        self.treeCtrl.SelectItem(self.treeCtrl[0])
        self.setTree(('parent', 1), 'child', 'item')
        self.treeCtrl.refresh()
        self.assertSelection(selected=[0], notSelected=[1,2])

    def testRemovingASelectedItemDoesNotMakeAnotherOneSelected(self):
        self.setTree('item 1', 'item 2')
        self.treeCtrl.refresh()
        self.treeCtrl.SelectItem(self.treeCtrl[0])
        self.setTree('item 2')
        self.treeCtrl.refresh()
        self.assertSelection(selected=[], notSelected=[0])
        
    def testRefreshItem(self):
        self.setTree(('item', 0, 'itemId'))
        self.treeCtrl.refresh()
        self.setTree(('new subject', 0, 'itemId'))
        self.treeCtrl.refreshItem(0)
        self.assertEqual(self.getItemText(0), self.treeCtrl.GetItemText(self.treeCtrl[0]))        
    
    
class TreeCtrlTest(TreeCtrlTestCase, CommonTests):            
    def setUp(self):
        super(TreeCtrlTest, self).setUp()
        self.treeCtrl = widgets.TreeCtrl(self.frame, self.getItemText,
            self.getItemImage, self.getItemAttr,
            self.getItemId, self.getRootIndices,
            self.getChildIndices, self.onSelect, dummy.DummyUICommand(),
            dummy.DummyUICommand())
        imageList = wx.ImageList(16, 16)
        for bitmapName in ['task', 'tasks']:
            imageList.Add(wx.ArtProvider_GetBitmap(bitmapName, wx.ART_MENU, 
                          (16,16)))
        self.treeCtrl.AssignImageList(imageList)
