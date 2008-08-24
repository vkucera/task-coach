'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>

Task Coach is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Task Coach is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import wx, sys
import test
from unittests import dummy
from taskcoachlib import widgets

        
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
        
    def getItemExpanded(self, index):
        return False
    
    def getItemText(self, index):
        return self.getItem(index)[0]

    def getItemTooltipText(self, index):
        return None

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
                
    def setUp(self):
        super(TreeCtrlTestCase, self).setUp()
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

    def testOneParentAndTwoChildren(self):
        self.assertTree(('item 0', ('item 1', 'item 2')))
    
    def testAddOneChild(self):
        self.setTree(('parent', ('child 1',)))
        self.assertTree(('parent', ('child 1', 'child 2')))

    def testDeleteOneChild(self):
        self.setTree(('parent', ('child 1', 'child 2')))
        self.assertTree(('parent', ('child 2',)))
        
    def testReorderItems(self):
        self.setTree('item 0', 'item 1')
        self.assertTree('item 1', 'item 0')

    def testReorderChildren(self):
        self.setTree(('parent', ('child 1', 'child 2')))
        self.assertTree(('parent', ('child 2', 'child 1')))

    def testReorderParentsAndOneChild(self):
        self.assertTree(('parent', ('child',)), 'item')
        self.assertTree('item', ('parent', ('child',)))

    def testReorderParentsAndTwoChildren(self):
        self.assertTree(('parent 1', ('child 1', 'child 2')), 'parent 2')
        self.assertTree('parent 2', ('parent 1', ('child 2', 'child 1')))

    def testRetainSelectionWhenEditingTask(self):
        self.setTree('item')
        item, cookie = self.treeCtrl.GetFirstChild(self.treeCtrl.GetRootItem())
        self.treeCtrl.SelectItem(item)
        self.failUnless(self.treeCtrl.IsSelected(item))
        self.setTree('new subject')
        item, cookie = self.treeCtrl.GetFirstChild(self.treeCtrl.GetRootItem())
        self.failUnless(self.treeCtrl.IsSelected(item))

    def testRetainSelectionWhenEditingSubTask(self):
        self.setTree(('parent', ('child',)))
        item, cookie = self.treeCtrl.GetFirstChild(self.treeCtrl.GetRootItem())
        self.treeCtrl.SelectItem(item)
        self.failUnless(self.treeCtrl.IsSelected(item))
        self.setTree(('parent', ('new subject',)))
        item, cookie = self.treeCtrl.GetFirstChild(self.treeCtrl.GetRootItem())
        self.failUnless(self.treeCtrl.IsSelected(item))

    def testRetainSelectionWhenAddingSubTask(self):
        self.setTree('parent')
        item, cookie = self.treeCtrl.GetFirstChild(self.treeCtrl.GetRootItem())
        self.treeCtrl.SelectItem(item)
        self.setTree(('parent', ('child',)))
        self.failUnless(self.treeCtrl.IsSelected(item))

    def testRetainSelectionWhenAddingSubTask_TwoToplevelTasks(self):
        self.setTree('parent', 'item')
        item, cookie = self.treeCtrl.GetFirstChild(self.treeCtrl.GetRootItem())
        self.treeCtrl.SelectItem(item)
        self.setTree(('parent', ('child',)), 'item')
        self.failUnless(self.treeCtrl.IsSelected(item))

    def testRemovingASelectedItemMakesAnotherOneSelected(self):
        self.setTree('item 1', 'item 2')
        item, cookie = self.treeCtrl.GetFirstChild(self.treeCtrl.GetRootItem())
        self.treeCtrl.SelectItem(item)
        self.setTree('item 2')
        self.failUnless(self.treeCtrl.IsSelected(item))
        
    def testRefreshItem(self):
        self.setTree('item')
        self.setTree('new subject', refresh=False)
        self.treeCtrl.RefreshItem((0,))
        item, cookie = self.treeCtrl.GetFirstChild(self.treeCtrl.GetRootItem())
        self.assertEqual(self.getItemText((0,)), self.treeCtrl.GetItemText(item))        

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
        item, cookie = self.treeCtrl.GetFirstChild(self.treeCtrl.GetRootItem())
        self.treeCtrl.SelectItem(item)
        self.failIf(self.treeCtrl.isSelectionCollapsable())
    
    def testIsSelectionExpandable_OneSelectedItem(self):
        self.setTree('item 1')
        item, cookie = self.treeCtrl.GetFirstChild(self.treeCtrl.GetRootItem())
        self.treeCtrl.SelectItem(item)
        self.failIf(self.treeCtrl.isSelectionExpandable())
    
    def testIsSelectionCollapsable_SelectedExpandedParent(self):
        self.setTree(('parent', ('child',)))
        parent, cookie = self.treeCtrl.GetFirstChild(self.treeCtrl.GetRootItem())
        self.treeCtrl.Expand(parent)
        self.treeCtrl.SelectItem(parent)
        self.failUnless(self.treeCtrl.isSelectionCollapsable())
    
    def testIsSelectionExpandable_SelectedExpandedParent(self):
        self.setTree(('parent', ('child',)))
        parent, cookie = self.treeCtrl.GetFirstChild(self.treeCtrl.GetRootItem())
        self.treeCtrl.Expand(parent)
        self.treeCtrl.SelectItem(parent)
        self.failIf(self.treeCtrl.isSelectionExpandable())
    
    def testIsSelectionCollapsable_SelectedCollapsedParent(self):
        self.setTree(('parent', ('child',)))
        parent, cookie = self.treeCtrl.GetFirstChild(self.treeCtrl.GetRootItem())
        self.treeCtrl.SelectItem(parent)
        self.failIf(self.treeCtrl.isSelectionCollapsable())
    
    def testIsSelectionExpandable_SelectedCollapsedParent(self):
        self.setTree(('parent', ('child',)))
        parent, cookie = self.treeCtrl.GetFirstChild(self.treeCtrl.GetRootItem())
        self.treeCtrl.SelectItem(parent)
        self.failUnless(self.treeCtrl.isSelectionExpandable())
    
    def testIsSelectionCollapsable_CollapsedAndExpandedTasksInSelection(self):
        self.setTree(('parent1', ('child 1',)), ('parent 2', ('child 2',)))
        parent1, cookie = self.treeCtrl.GetFirstChild(self.treeCtrl.GetRootItem())
        self.treeCtrl.Expand(parent1)
        self.treeCtrl.SelectItem(parent1)
        parent2, cookie = self.treeCtrl.GetNextChild(self.treeCtrl.GetRootItem(), cookie)
        self.treeCtrl.SelectItem(parent2)
        self.failUnless(self.treeCtrl.isSelectionCollapsable())
    
    def testIsSelectionExpandable_CollapsedAndExpandedTasksInSelection(self):
        self.setTree(('parent1', ('child 1',)), ('parent 2', ('child 2',)))
        parent1, cookie = self.treeCtrl.GetFirstChild(self.treeCtrl.GetRootItem())
        self.treeCtrl.Expand(parent1)
        self.treeCtrl.SelectItem(parent1)
        parent2, cookie = self.treeCtrl.GetNextChild(self.treeCtrl.GetRootItem(), cookie)
        self.treeCtrl.SelectItem(parent2)
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
        self.setTree(('parent', ('child',)))
        self.failIf(self.treeCtrl.isAnyItemCollapsable())
    
    def testIsAnyItemExpandable_OneCollapsedParent(self):
        self.setTree(('parent', ('child',)))
        self.failUnless(self.treeCtrl.isAnyItemExpandable())

    def testIsAnyItemCollapsable_OneExpandedParent(self):
        self.setTree(('parent', ('child',)))
        parent, cookie = self.treeCtrl.GetFirstChild(self.treeCtrl.GetRootItem())
        self.treeCtrl.Expand(parent)
        self.failUnless(self.treeCtrl.isAnyItemCollapsable())
        
    def testIsAnyItemExpandable_OneExpandedParent(self):
        self.setTree(('parent', ('child',)))
        parent, cookie = self.treeCtrl.GetFirstChild(self.treeCtrl.GetRootItem())
        self.treeCtrl.Expand(parent)
        self.failIf(self.treeCtrl.isAnyItemExpandable())


class TreeCtrlTest(TreeCtrlTestCase, CommonTests):            
    def setUp(self):
        super(TreeCtrlTest, self).setUp()
        self.treeCtrl = widgets.TreeCtrl(self.frame, self.getItemText,
            self.getItemTooltipText, self.getItemImage, self.getItemAttr,
            self.getChildrenCount, self.getItemExpanded, self.onSelect, 
            dummy.DummyUICommand(), dummy.DummyUICommand())
        imageList = wx.ImageList(16, 16)
        for bitmapName in ['task', 'tasks']:
            imageList.Add(wx.ArtProvider_GetBitmap(bitmapName, wx.ART_MENU, 
                          (16,16)))
        self.treeCtrl.AssignImageList(imageList)
        
        
class CustomTreeCtrlTest(TreeCtrlTestCase, CommonTests):
    def setUp(self):
        super(CustomTreeCtrlTest, self).setUp()
        self.treeCtrl = widgets.CustomTreeCtrl(self.frame, self.getItemText,
            self.getItemTooltipText, self.getItemImage, self.getItemAttr,
            self.getChildrenCount, self.getItemExpanded, self.onSelect, 
            dummy.DummyUICommand(), dummy.DummyUICommand())
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
            self.getItemTooltipText, self.getItemImage, self.getItemAttr,
            self.getChildrenCount, self.getItemExpanded, self.getIsItemChecked, 
            self.onSelect, self.onCheck, 
            dummy.DummyUICommand(), dummy.DummyUICommand())
    
    def getIsItemChecked(self, index):
        return False
    
    def onCheck(self, event):
        pass

    def testCheckParentDoesNotCheckChild(self):
        self.setTree(('parent', ('child',)))
        self.treeCtrl.ExpandAll()
        parent, cookie = self.treeCtrl.GetFirstChild(self.treeCtrl.GetRootItem())
        self.treeCtrl.CheckItem(parent)
        child, cookie = self.treeCtrl.GetFirstChild(parent)
        self.failIf(child.IsChecked())
