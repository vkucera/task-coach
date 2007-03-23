import test, widgets, wx, sys
import unittests.dummy as dummy
        
class TreeCtrlTestCase(test.wxTestCase):
    def setTree(self, *items, **kwargs):
        self._tree = items
        if kwargs.get('refresh', True):
            self.treeCtrl.refresh()
            
    def getItem(self, index):
        item, children = 'root item', self._tree
        for i in index:
            try: 
                item, children = children[i]
            except ValueError:
                item, children = children[i], []
        return item, children
        
    def getItemText(self, index):
        return self.getItem(index)[0]

    def getItemImage(self, index, *args, **kwargs):
        if self.getChildrenCount(index):
            return 1
        else:
            return 0
        
    def getItemAttr(self, index):
        return wx.ListItemAttr()
                                
    def getChildrenCount(self, index):
        return len(self.getItem(index)[1])
            
    def onSelect(self, *args, **kwargs):
        pass
    
    def assertNodes(self, index, treeItem):
        self.assertEqual(self.getItemText(index), self.treeCtrl.GetItemText(treeItem))
        childrenCount = self.getChildrenCount(index)
        self.assertEqual(childrenCount, self.treeCtrl.GetChildrenCount(treeItem))
        for childIndex, treeChild in zip(range(childrenCount), self.treeCtrl.GetItemChildren(treeItem)):
            self.assertNodes(index + (childIndex,), treeChild)
    
    def assertTree(self, *items):
        self.setTree(*items)
        self.treeCtrl.expandAllItems()
        self.assertEqual(len(items), len(self.treeCtrl.GetItemChildren()))
        for index, treeItem in zip(range(len(self._tree)), self.treeCtrl.GetItemChildren()):            
            self.assertNodes((index,), treeItem)
            
    def assertSelection(self, selected=None, notSelected=None):
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
        self.assertTree()

    def testOneParentAndOneChild(self):
        self.assertTree(('item 0', ('item 1',)))

    '''
    def testOneParentAndTwoChildren(self):
        self.assertTree(('item 0', 2), 'item 1', 'item 2')
   
    def testAddOneChild(self):
        self.setTree(('parent', 1), 'child 1')
        self.assertTree(('parent', 2), 'child 1', 'child 2')

    def testAddingTheFirstChildExpandsParent(self):
        self.setTree('parent')
        self.setTree(('parent', 1), 'child')
        self.failUnless(self.treeCtrl.IsExpanded(self.treeCtrl[0]))
        
    def testAddingTheSecondChildExpandsParent(self):
        self.setTree(('parent', 1), 'child 1')
        self.failIf(self.treeCtrl.IsExpanded(self.treeCtrl[0]))
        self.setTree(('parent', 2), 'child 1', 'child 2')
        self.failUnless(self.treeCtrl.IsExpanded(self.treeCtrl[0]))

    def testDeleteOneChild(self):
        self.setTree(('parent', 2), 'child 1', 'child 2')
        self.assertTree(('parent', 1), 'child 2')
                
    def testReorderItems(self):
        self.setTree('item 0', 'item 1')
        self.assertTree('item 1', 'item 0')

    def testReorderChildren(self):
        self.setTree(('parent', 2), 'child 1', 'child 2')
        self.assertTree(('parent', 2), 'child 2', 'child 1')

    def testReorderParentsAndOneChild(self):
        self.assertTree(('parent', 1), 'child', 'item')
        self.assertTree('item', ('parent', 1), 'child')
        
    def testReorderParentsAndTwoChildren(self):
        self.assertTree(('parent 1', 2), 'child 1', 'child 2', 'parent 2')
        self.assertTree('parent 2', ('parent 1', 2), 'child 2', 'child 1')

    def testReorderParentsAndChildrenDoesNotCollapseParent(self):
        self.setTree('parent', 'item')
        self.setTree(('parent', 2), 'child 1', 'child 2', 'item')
        self.setTree('item', ('parent', 2), 'child 2', 'child 1')
        self.failUnless(self.treeCtrl.IsExpanded(self.treeCtrl[1]))
        
    def testRetainSelectionWhenEditingTask(self):
        self.setTree(('item', 0, 'id'))
        self.treeCtrl.SelectItem(self.treeCtrl[0])
        self.failUnless(self.treeCtrl.IsSelected(self.treeCtrl[0]))
        self.setTree(('new subject', 0, 'id'))
        self.assertSelection(selected=[0])

    def testRetainSelectionWhenEditingSubTask(self):
        self.setTree('parent')
        self.setTree(('parent', 1), ('child', 0, 'childId'))
        self.treeCtrl.SelectItem(self.treeCtrl[1])
        self.failUnless(self.treeCtrl.IsSelected(self.treeCtrl[1]))
        self.setTree(('parent', 1), ('new subject', 0, 'childId'))
        self.assertSelection(selected=[1], notSelected=[0])

    def testRetainSelectionWhenAddingSubTask(self):
        self.setTree('parent')
        self.treeCtrl.SelectItem(self.treeCtrl[0])
        self.setTree(('parent', 1), 'child')
        self.assertSelection(selected=[0], notSelected=[1])

    def testRetainSelectionWhenAddingSubTask_TwoToplevelTasks(self):
        self.setTree('parent', 'item')
        self.treeCtrl.SelectItem(self.treeCtrl[0])
        self.setTree(('parent', 1), 'child', 'item')
        self.assertSelection(selected=[0], notSelected=[1,2])

    def testRemovingASelectedItemDoesNotMakeAnotherOneSelected(self):
        self.setTree('item 1', 'item 2')
        self.treeCtrl.SelectItem(self.treeCtrl[0])
        self.setTree('item 2')
        self.assertSelection(selected=[], notSelected=[0])
        
    def testRefreshItem(self):
        self.setTree(('item', 0, 'itemId'))
        self.setTree(('new subject', 0, 'itemId'), refresh=False)
        self.treeCtrl.refreshItem(0)
        self.assertEqual(self.getItemText(0), self.treeCtrl.GetItemText(self.treeCtrl[0]))        
   
    def testIsSelectionCollapsable_EmptyTree(self):
        self.failIf(self.treeCtrl.isSelectionCollapsable())
    
    def testIsSelectionExpandable_EmptyTree(self):
        self.failIf(self.treeCtrl.isSelectionExpandable())
        
    def testIsSelectionCollapsable_OneUnselectedItem(self):
        self.setTree('item 1')
        self.failIf(self.treeCtrl.isSelectionCollapsable())
        
    def testIsSelectionExpandable_OneUnselectedItem(self):
        self.setTree('item 1')
        self.treeCtrl.UnselectAll()
        self.failIf(self.treeCtrl.isSelectionExpandable())
        
    def testIsSelectionCollapsable_OneSelectedItem(self):
        self.setTree('item 1')
        self.treeCtrl.SelectItem(self.treeCtrl[0])
        self.failIf(self.treeCtrl.isSelectionCollapsable())
        
    def testIsSelectionExpandable_OneSelectedItem(self):
        self.setTree('item 1')
        self.treeCtrl.SelectItem(self.treeCtrl[0])
        self.failIf(self.treeCtrl.isSelectionExpandable())
    
    def testIsSelectionCollapsable_SelectedExpandedParent(self):
        self.setTree(('parent', 1), 'child')
        self.treeCtrl.Expand(self.treeCtrl[0])
        self.treeCtrl.SelectItem(self.treeCtrl[0])
        self.failUnless(self.treeCtrl.isSelectionCollapsable())
        
    def testIsSelectionExpandable_SelectedExpandedParent(self):
        self.setTree(('parent', 1), 'child')
        self.treeCtrl.Expand(self.treeCtrl[0])
        self.treeCtrl.SelectItem(self.treeCtrl[0])
        self.failIf(self.treeCtrl.isSelectionExpandable())

    def testIsSelectionCollapsable_SelectedCollapsedParent(self):
        self.setTree(('parent', 1), 'child')
        self.treeCtrl.SelectItem(self.treeCtrl[0])
        self.failIf(self.treeCtrl.isSelectionCollapsable())

    def testIsSelectionExpandable_SelectedCollapsedParent(self):
        self.setTree(('parent', 1), 'child')
        self.treeCtrl.SelectItem(self.treeCtrl[0])
        self.failUnless(self.treeCtrl.isSelectionExpandable())
        
    def testIsSelectionCollapsable_CollapsedAndExpandedTasksInSelection(self):
        self.setTree(('parent1', 1), 'child 1', ('parent 2', 1), 'child 2')
        self.treeCtrl.Expand(self.treeCtrl[0])
        self.treeCtrl.SelectItem(self.treeCtrl[0])
        self.treeCtrl.SelectItem(self.treeCtrl[2])
        self.failUnless(self.treeCtrl.isSelectionCollapsable())
        
    def testIsSelectionExpandable_CollapsedAndExpandedTasksInSelection(self):
        self.setTree(('parent1', 1), 'child 1', ('parent 2', 1), 'child 2')
        self.treeCtrl.Expand(self.treeCtrl[0])
        self.treeCtrl.SelectItem(self.treeCtrl[0])
        self.treeCtrl.SelectItem(self.treeCtrl[2])
        self.failUnless(self.treeCtrl.isSelectionExpandable())

    def testIsAnyItemCollapsable_NoItems(self):
        self.failIf(self.treeCtrl.isAnyItemCollapsable())
        
    def testIsAnyItemExpandable_NoItems(self):
        self.failIf(self.treeCtrl.isAnyItemExpandable())
        
    def testIsAnyItemCollapsable_OneItem(self):
        self.setTree('item')
        self.failIf(self.treeCtrl.isAnyItemCollapsable())
        
    def testIsAnyItemExpandable_OneItem(self):
        self.setTree('item')
        self.failIf(self.treeCtrl.isAnyItemExpandable())
        
    def testIsAnyItemCollapsable_OneCollapsedParent(self):
        self.setTree(('parent', 1), 'child')
        self.failIf(self.treeCtrl.isAnyItemCollapsable())
        
    def testIsAnyItemExpandable_OneCollapsedParent(self):
        self.setTree(('parent', 1), 'child')
        self.failUnless(self.treeCtrl.isAnyItemExpandable())

    def testIsAnyItemCollapsable_OneExpandedParent(self):
        self.setTree(('parent', 1), 'child')
        self.treeCtrl.Expand(self.treeCtrl[0])
        self.failUnless(self.treeCtrl.isAnyItemCollapsable())
        
    def testIsAnyItemExpandable_OneExpandedParent(self):
        self.setTree(('parent', 1), 'child')
        self.treeCtrl.Expand(self.treeCtrl[0])
        self.failIf(self.treeCtrl.isAnyItemExpandable())
    '''

class TreeCtrlTest(TreeCtrlTestCase, CommonTests):            
    def setUp(self):
        super(TreeCtrlTest, self).setUp()
        self.treeCtrl = widgets.TreeCtrl(self.frame, self.getItemText,
            self.getItemImage, self.getItemAttr,
            self.getChildrenCount, self.onSelect, dummy.DummyUICommand(),
            dummy.DummyUICommand())
        imageList = wx.ImageList(16, 16)
        for bitmapName in ['task', 'tasks']:
            imageList.Add(wx.ArtProvider_GetBitmap(bitmapName, wx.ART_MENU, 
                          (16,16)))
        self.treeCtrl.AssignImageList(imageList)
        
        
class CustomTreeCtrlTest(TreeCtrlTestCase, CommonTests):
    def setUp(self):
        super(CustomTreeCtrlTest, self).setUp()
        self.treeCtrl = widgets.CustomTreeCtrl(self.frame, self.getItemText,
            self.getItemImage, self.getItemAttr,
            self.getChildrenCount, self.onSelect, dummy.DummyUICommand(),
            dummy.DummyUICommand())
        imageList = wx.ImageList(16, 16)
        for bitmapName in ['task', 'tasks']:
            imageList.Add(wx.ArtProvider_GetBitmap(bitmapName, wx.ART_MENU, 
                          (16,16)))
        self.treeCtrl.AssignImageList(imageList)
        
    def testIsSelectionCollapsable_CollapsedAndExpandedTasksInSelection(self):
        # This test only makes sense when the TreeCtrl supports wx.TR_EXTENDED, 
        # and CustomTreeCtrl does not support that.
        pass


class CheckTreeCtrlTest(TreeCtrlTestCase, CommonTests):
    def setUp(self):
        super(CheckTreeCtrlTest, self).setUp()
        self.treeCtrl = widgets.CheckTreeCtrl(self.frame, self.getItemText,
            self.getItemImage, self.getItemAttr, self.getChildrenCount, 
            self.getIsItemChecked, self.onSelect, self.onCheck, 
            dummy.DummyUICommand(), dummy.DummyUICommand())
    
    def getIsItemChecked(self, index):
        return False
    
    def onCheck(self, event):
        pass
    '''
    def testCheckParentDoesNotCheckChild(self):
        self.setTree(('parent', ('child',)))
        self.treeCtrl.ExpandAll()
        parent, cookie = self.treeCtrl.GetFirstChild(self.treeCtrl.GetRootItem())
        self.treeCtrl.CheckItem(parent)
        child, cookie = self.treeCtrl.GetFirstChild(parent)
        self.failIf(child.IsChecked())
    '''