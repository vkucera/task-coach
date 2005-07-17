import test, widgets, dummy, wx
        
class TreeCtrlTest(test.wxTestCase):
        
    def setItemTexts(self, indexToTextMapping):
        self._itemTexts.update(indexToTextMapping)
        
    def getItemText(self, index):
        return self._itemTexts.get(index, 'item %d'%self.getItemId(index))

    def getItemImage(self, index):
        if self.getItemChildrenCount(index) > 0:
            return 0, 0
        else:
            return 1, 1
        
    def getItemAttr(self, index):
        return wx.ListItemAttr()
    
    def setItemChildrenCount(self, index, nrChildren):
        self._childrenCount[self.getItemId(index)] = nrChildren
        for childIndex in range(nrChildren):
            self._childIndex[index+1+childIndex] = childIndex
            
    def getItemChildrenCount(self, index, recursive=False):
        return self._childrenCount.get(self.getItemId(index), 0)
    
    def setItemIds(self, indexToItemIdMapping):
        self._itemIds.update(indexToItemIdMapping)
        
    def getItemId(self, index):
        return self._itemIds.get(index, index)
           
    def getItemChildIndex(self, index):
        return self._childIndex.get(index, index)
            
    def onSelect(self, *args, **kwargs):
        pass

    def assertItems(self, *items):
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
        for index in selected or []:
            self.failUnless(self.treeCtrl.IsSelected(self.treeCtrl[index]))
        for index in notSelected or []:
            self.failIf(self.treeCtrl.IsSelected(self.treeCtrl[index]))
    
    def setUp(self):
        self._childrenCount = {}
        self._childIndex = {}
        self._itemIds = {}
        self._itemTexts = {}
        self.treeCtrl = widgets.TreeCtrl(self.frame, self.getItemText,
            self.getItemImage, self.getItemAttr, self.getItemChildrenCount,
            self.getItemId, self.getItemChildIndex, self.onSelect, 
            dummy.DummyUICommand())
        imageList = wx.ImageList(16, 16)
        imageList.Add(wx.ArtProvider_GetBitmap('task', wx.ART_MENU, (16,16)))
        self.treeCtrl.AssignImageList(imageList)
        
    def testCreate(self):
        self.assertItems()
        
    def testOneItem(self):
        self.treeCtrl.refresh(1)
        self.assertItems('item 0')
        
    def testTwoItems(self):
        self.treeCtrl.refresh(2)
        self.assertItems('item 0', 'item 1')
        
    def testRemoveAllItems(self):
        self.treeCtrl.refresh(2)
        self.treeCtrl.refresh(0)
        self.assertItems()
        
    def testOneParentAndOneChild(self):
        self.setItemChildrenCount(0, 1)
        self.treeCtrl.refresh(2)
        self.assertItems(('item 0', 1), 'item 1')
        
    def testOneParentAndTwoChildren(self):
        self.setItemChildrenCount(0, 2)
        self.treeCtrl.refresh(3)
        self.assertItems(('item 0', 2), 'item 1', 'item 2')
        
    def testAddOneChild(self):
        self.setItemChildrenCount(0, 1)
        self.treeCtrl.refresh(2)
        self.setItemChildrenCount(0, 2)
        self.treeCtrl.refresh(3)
        self.assertItems(('item 0', 2), 'item 1', 'item 2')
        
    def testAddingTheFirstChildExpandsParent(self):
        self.treeCtrl.refresh(1)
        self.setItemChildrenCount(0, 1)
        self.treeCtrl.refresh(2)
        self.failUnless(self.treeCtrl.IsExpanded(self.treeCtrl[0]))
        
    def testAddingTheSecondChildExpandsParent(self):
        self.setItemChildrenCount(0, 1)
        self.treeCtrl.refresh(2)
        self.failIf(self.treeCtrl.IsExpanded(self.treeCtrl[0]))
        self.setItemChildrenCount(0, 2)
        self.treeCtrl.refresh(3)
        self.failUnless(self.treeCtrl.IsExpanded(self.treeCtrl[0]))
        
    def testDeleteOneChild(self):
        self.setItemChildrenCount(0, 2)
        self.treeCtrl.refresh(3)
        self.setItemChildrenCount(0, 1)
        self.treeCtrl.refresh(2)
        self.assertItems(('item 0', 1), 'item 1')
                
    def testReorderItems(self):
        self.treeCtrl.refresh(2)
        self.assertItems('item 0', 'item 1')
        self.setItemIds({1: 0, 0: 1})
        self.treeCtrl.refresh(2)
        self.assertItems('item 1', 'item 0')

    def testReorderChildren(self):
        self.setItemChildrenCount(0, 2)
        self.treeCtrl.refresh(3)
        self.assertItems(('item 0', 2), 'item 1', 'item 2')
        self.setItemIds({2: 1, 1: 2})
        self.treeCtrl.refresh(3)
        self.assertItems(('item 0', 2), 'item 2', 'item 1')
        
    def testReorderParentsAndChildren(self):
        self.setItemChildrenCount(0, 2)
        self.treeCtrl.refresh(4)
        self.assertItems(('item 0', 2), 'item 1', 'item 2', 'item 3')
        self.setItemIds({0: 3, 1: 0, 2: 2, 3: 1})
        self.treeCtrl.refresh(4)
        self.assertItems('item 3', ('item 0', 2), 'item 2', 'item 1')
        
    def testReorderParentsAndChildrenDoesNotCollapsParent(self):
        self.treeCtrl.refresh(2)
        self.setItemChildrenCount(0, 2)
        self.treeCtrl.refresh(4)
        self.setItemIds({0: 3, 1: 0, 2: 2, 3: 1})
        self.treeCtrl.refresh(4)
        self.failUnless(self.treeCtrl.IsExpanded(self.treeCtrl[1]))

    def testRetainSelectionWhenEditingTask(self):
        self.treeCtrl.refresh(1)
        self.treeCtrl.SelectItem(self.treeCtrl[0])
        self.failUnless(self.treeCtrl.IsSelected(self.treeCtrl[0]))
        self.setItemTexts({0: 'new subject'})
        self.treeCtrl.refresh(1)
        self.assertSelection(selected=[0])
        
    def testRetainSelectionWhenEditingSubTask(self):
        self.treeCtrl.refresh(1)
        self.setItemChildrenCount(0, 1)
        self.treeCtrl.refresh(2)
        self.treeCtrl.SelectItem(self.treeCtrl[1])
        self.failUnless(self.treeCtrl.IsSelected(self.treeCtrl[1]))
        self.setItemTexts({1: 'new subject'})
        self.treeCtrl.refresh(2)
        self.assertSelection(selected=[1], notSelected=[0])
        
    def testRetainSelectionWhenAddingSubTask(self):
        self.treeCtrl.refresh(1)
        self.treeCtrl.SelectItem(self.treeCtrl[0])
        self.setItemChildrenCount(0, 1)
        self.treeCtrl.refresh(2)
        self.assertSelection(selected=[0], notSelected=[1])
        
    def testRetainSelectionWhenAddingSubTask_TwoToplevelTasks(self):
        self.treeCtrl.refresh(2)
        self.treeCtrl.SelectItem(self.treeCtrl[0])
        self.setItemChildrenCount(0, 1)
        self.treeCtrl.refresh(3)
        self.assertSelection(selected=[0], notSelected=[1,2])
        
    def testRemovingASelectedItemDoesNotMakeAnotherOneSelected(self):
        self.treeCtrl.refresh(2)
        self.treeCtrl.SelectItem(self.treeCtrl[0])
        self.setItemIds({0: 1})
        self.treeCtrl.refresh(1)
        self.treeCtrl.SetFocus()
        self.assertSelection(selected=[], notSelected=[0])
        
    def testRefreshItem(self):
        self.treeCtrl.refresh(1)
        self.setItemTexts({0: 'Hi'})
        self.treeCtrl.refreshItem(0)
        self.assertEqual(self.getItemText(0), self.treeCtrl.GetItemText(self.treeCtrl[0]))