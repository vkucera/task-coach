'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2009 Frank Niessink <frank@niessink.com>

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

import wx
import test
from unittests import dummy
from taskcoachlib import widgets

        
class TreeCtrlTestCase(test.wxTestCase):
    onSelect = None
    
    def getFirstTreeItem(self):
        # pylint: disable-msg=E1101
        return self.treeCtrl.GetFirstChild(self.treeCtrl.GetRootItem())[0]
                
    def setUp(self):
        super(TreeCtrlTestCase, self).setUp()
        self.children = dict()
        self.frame.children = lambda item: self.children.get(item, [])
        self.frame.getItemText = lambda item, column: item
        self.frame.getItemImage = lambda item, which, column: -1
        self.frame.getColor = lambda item: None
        self.frame.getBackgroundColor = lambda item: None
        self.frame.getIsItemChecked = lambda item: False
        self.frame.getItemExpanded = lambda item: False
        
        
class CommonTestsMixin(object):
    ''' Tests for all types of trees. '''

    def testCreate(self):
        self.assertEqual(0, len(self.treeCtrl.GetItemChildren()))
    
    def testOneItem(self):
        self.children[None] = ['item 0']
        self.treeCtrl.RefreshAllItems(1)
        self.assertEqual(1, len(self.treeCtrl.GetItemChildren()))
    
    def testTwoItems(self):
        self.children[None] = ['item 0', 'item 1']
        self.treeCtrl.RefreshAllItems(2)
        self.assertEqual(2, len(self.treeCtrl.GetItemChildren()))
    
    def testRemoveAllItems(self):
        self.children[None] = ['item 0', 'item 1']
        self.treeCtrl.RefreshAllItems(2)
        self.children[None] = []
        self.treeCtrl.RefreshAllItems(0)
        self.assertEqual(0, len(self.treeCtrl.GetItemChildren()))
        
    def testOneParentAndOneChild(self):
        self.children[None] = ['item 0']
        self.children['item 0'] = ['item 0.0']
        self.treeCtrl.RefreshAllItems(2)
        self.assertEqual(1, len(self.treeCtrl.GetItemChildren()))
        self.assertEqual(1, len(self.treeCtrl.GetItemChildren(self.getFirstTreeItem())))
        
    def testOneParentAndTwoChildren(self):
        self.children[None] = ['item 0']
        self.children['item 0'] = ['item 0.0', 'item 0.1']
        self.treeCtrl.RefreshAllItems(3)
        self.assertEqual(1, len(self.treeCtrl.GetItemChildren()))
        self.assertEqual(2, len(self.treeCtrl.GetItemChildren(self.getFirstTreeItem())))

    def testAddOneChild(self):
        self.children[None] = ['item 0']
        self.children['item 0'] = ['item 0.0']
        self.treeCtrl.RefreshAllItems(2)
        self.children['item 0'] = ['item 0.0', 'item 0.1']
        self.treeCtrl.RefreshAllItems(3)
        self.assertEqual(1, len(self.treeCtrl.GetItemChildren()))
        self.assertEqual(2, len(self.treeCtrl.GetItemChildren(self.getFirstTreeItem())))        
             
    def testDeleteOneChild(self):
        self.children[None] = ['item 0']
        self.children['item 0'] = ['item 0.0', 'item 0.1']
        self.treeCtrl.RefreshAllItems(3)
        self.children['item 0'] = ['item 0.0']
        self.treeCtrl.RefreshAllItems(2)
        self.assertEqual(1, len(self.treeCtrl.GetItemChildren()))
        self.assertEqual(1, len(self.treeCtrl.GetItemChildren(self.getFirstTreeItem())))
    
    def testReorderItems(self):
        self.children[None] = ['item 0', 'item 1']
        self.treeCtrl.RefreshAllItems(2)
        self.children[None] = ['item 1', 'item 0']
        self.treeCtrl.RefreshAllItems(2)
        self.assertEqual('item 1', self.treeCtrl.GetItemText(self.getFirstTreeItem()))
    
    def testReorderChildren(self):
        self.children[None] = ['item 0']
        self.children['item 0'] = ['item 0.0', 'item 0.1']
        self.treeCtrl.RefreshAllItems(3)
        self.children['item 0'] = ['item 0.1', 'item 0.0']
        self.treeCtrl.RefreshAllItems(3)
        self.assertEqual('item 0.1', self.treeCtrl.GetItemText(self.treeCtrl.GetFirstChild(self.getFirstTreeItem())[0]))
        
    def testReorderParentsAndOneChild(self):
        self.children[None] = ['item 0', 'item 1']
        self.children['item 0'] = ['item 0.0']
        self.treeCtrl.RefreshAllItems(3)
        self.children[None] = ['item 1', 'item 0']
        self.treeCtrl.RefreshAllItems(3)
        self.assertEqual('item 1', self.treeCtrl.GetItemText(self.getFirstTreeItem()))
    
    def testReorderParentsAndTwoChildren(self):
        self.children[None] = ['item 0', 'item 1']
        self.children['item 0'] = ['item 0.0', 'item 0.1']
        self.treeCtrl.RefreshAllItems(4)
        self.children[None] = ['item 1', 'item 0']
        self.children['item 0'] = ['item 0.1', 'item 0.0']
        self.treeCtrl.RefreshAllItems(4)
        self.assertEqual('item 1', self.treeCtrl.GetItemText(self.getFirstTreeItem()))
        self.assertEqual(0, len(self.treeCtrl.GetItemChildren(self.getFirstTreeItem())))
    
    def testRetainSelectionWhenEditingTask(self):
        self.children[None] = ['item 0']
        self.treeCtrl.RefreshAllItems(1)
        item = self.getFirstTreeItem()
        self.treeCtrl.SelectItem(item)
        self.failUnless(self.treeCtrl.IsSelected(item))
        self.children[None] = ['item 0']
        self.treeCtrl.RefreshAllItems(1)
        item = self.getFirstTreeItem()
        self.failUnless(self.treeCtrl.IsSelected(item))
 
    def testRetainSelectionWhenEditingSubTask(self):
        self.children[None] = ['item 0']
        self.children['item 0'] = ['item 0.0']
        self.treeCtrl.RefreshAllItems(2)
        item = self.getFirstTreeItem()
        self.treeCtrl.SelectItem(item)
        self.failUnless(self.treeCtrl.IsSelected(item))
        self.children['item 0'] = ['item 0.0']
        self.treeCtrl.RefreshAllItems(2)
        item = self.getFirstTreeItem()
        self.failUnless(self.treeCtrl.IsSelected(item))
    
    def testRetainSelectionWhenAddingSubTask(self):
        self.children[None] = ['item 0']
        self.treeCtrl.RefreshAllItems(1)
        item = self.getFirstTreeItem()
        self.treeCtrl.SelectItem(item)
        self.failUnless(self.treeCtrl.IsSelected(item))
        self.children['item 0'] = ['item 0.0']
        self.treeCtrl.RefreshAllItems(2)
        item = self.getFirstTreeItem()        
        self.failUnless(self.treeCtrl.IsSelected(item))

    def testRetainSelectionWhenAddingSubTask_TwoToplevelTasks(self):
        self.children[None] = ['item 0', 'item 1']
        self.treeCtrl.RefreshAllItems(2)
        item = self.getFirstTreeItem()
        self.treeCtrl.SelectItem(item)
        self.failUnless(self.treeCtrl.IsSelected(item))
        self.children['item 0'] = ['item 0.0']
        self.treeCtrl.RefreshAllItems(3)
        item = self.getFirstTreeItem()        
        self.failUnless(self.treeCtrl.IsSelected(item))
        
    def testRemovingASelectedItemDoesNotMakeAnotherOneSelected(self):
        self.children[None] = ['item 0', 'item 1']
        self.treeCtrl.RefreshAllItems(2)
        item = self.getFirstTreeItem()
        self.treeCtrl.SelectItem(item)
        self.failUnless(self.treeCtrl.IsSelected(item))
        self.children[None] = ['item 1']
        self.treeCtrl.RefreshAllItems(1)
        self.failIf(self.treeCtrl.curselection())
        
    def testRefreshItem(self):
        self.children[None] = ['item 0']
        self.treeCtrl.RefreshAllItems(1)
        self.treeCtrl.RefreshItems('item 0')
        item = self.getFirstTreeItem()
        self.assertEqual('item 0', self.treeCtrl.GetItemText(item))        

    def testIsSelectionCollapsable_EmptyTree(self):
        self.failIf(self.treeCtrl.isSelectionCollapsable())
    
    def testIsSelectionExpandable_EmptyTree(self):
        self.failIf(self.treeCtrl.isSelectionExpandable())
       
    def testIsSelectionCollapsable_OneUnselectedItem(self):
        self.children[None] = ['item 0']
        self.treeCtrl.RefreshAllItems(1)
        self.failIf(self.treeCtrl.isSelectionCollapsable())
    
    def testIsSelectionExpandable_OneUnselectedItem(self):
        self.children[None] = ['item 0']
        self.treeCtrl.RefreshAllItems(1)
        self.failIf(self.treeCtrl.isSelectionExpandable())
    
    def testIsSelectionCollapsable_OneSelectedItem(self):
        self.children[None] = ['item 0']
        self.treeCtrl.RefreshAllItems(1)
        item = self.getFirstTreeItem()
        self.treeCtrl.SelectItem(item)
        self.failIf(self.treeCtrl.isSelectionCollapsable())
    
    def testIsSelectionExpandable_OneSelectedItem(self):
        self.children[None] = ['item 0']
        self.treeCtrl.RefreshAllItems(1)
        item = self.getFirstTreeItem()
        self.treeCtrl.SelectItem(item)
        self.failIf(self.treeCtrl.isSelectionExpandable())
    
    def testIsSelectionCollapsable_SelectedExpandedParent(self):
        self.children[None] = ['item 0']
        self.children['item 0'] = ['item 0.0']
        self.treeCtrl.RefreshAllItems(2)
        parent = self.getFirstTreeItem()
        self.treeCtrl.Expand(parent)
        self.treeCtrl.SelectItem(parent)
        self.failUnless(self.treeCtrl.isSelectionCollapsable())
    
    def testIsSelectionExpandable_SelectedExpandedParent(self):
        self.children[None] = ['item 0']
        self.children['item 0'] = ['item 0.0']
        self.treeCtrl.RefreshAllItems(2)
        parent = self.getFirstTreeItem()
        self.treeCtrl.Expand(parent)
        self.treeCtrl.SelectItem(parent)
        self.failIf(self.treeCtrl.isSelectionExpandable())
    
    def testIsSelectionCollapsable_SelectedCollapsedParent(self):
        self.children[None] = ['item 0']
        self.children['item 0'] = ['item 0.0']
        self.treeCtrl.RefreshAllItems(2)
        parent = self.getFirstTreeItem()
        self.treeCtrl.SelectItem(parent)
        self.failIf(self.treeCtrl.isSelectionCollapsable())
    
    def testIsSelectionExpandable_SelectedCollapsedParent(self):
        self.children[None] = ['item 0']
        self.children['item 0'] = ['item 0.0']
        self.treeCtrl.RefreshAllItems(2)
        parent = self.getFirstTreeItem()
        self.treeCtrl.SelectItem(parent)
        self.failUnless(self.treeCtrl.isSelectionExpandable())
    
    def testIsSelectionCollapsable_CollapsedAndExpandedTasksInSelection(self):
        self.children[None] = ['item 0', 'item 1']
        self.children['item 0'] = ['item 0.0']
        self.children['item 1'] = ['item 1.0']
        self.treeCtrl.RefreshAllItems(4)
        parent1, cookie = self.treeCtrl.GetFirstChild(self.treeCtrl.GetRootItem())
        self.treeCtrl.Expand(parent1)
        self.treeCtrl.SelectItem(parent1)
        parent2, cookie = self.treeCtrl.GetNextChild(self.treeCtrl.GetRootItem(), cookie)
        self.treeCtrl.SelectItem(parent2)
        self.failUnless(self.treeCtrl.isSelectionCollapsable())
    
    def testIsSelectionExpandable_CollapsedAndExpandedTasksInSelection(self):
        self.children[None] = ['item 0', 'item 1']
        self.children['item 0'] = ['item 0.0']
        self.children['item 1'] = ['item 1.0']
        self.treeCtrl.RefreshAllItems(4)
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
        self.children[None] = ['item 0']
        self.treeCtrl.RefreshAllItems(1)
        self.failIf(self.treeCtrl.isAnyItemCollapsable())
   
    def testIsAnyItemExpandable_OneItem(self):
        self.children[None] = ['item 0']
        self.treeCtrl.RefreshAllItems(1)
        self.failIf(self.treeCtrl.isAnyItemExpandable())
        
    def testIsAnyItemCollapsable_OneCollapsedParent(self):
        self.children[None] = ['item 0']
        self.children['item 0'] = ['item 0.0']
        self.treeCtrl.RefreshAllItems(2)
        self.failIf(self.treeCtrl.isAnyItemCollapsable())
       
    def testIsAnyItemExpandable_OneCollapsedParent(self):
        self.children[None] = ['item 0']
        self.children['item 0'] = ['item 0.0']
        self.treeCtrl.RefreshAllItems(2)
        self.failUnless(self.treeCtrl.isAnyItemExpandable())
    
    def testIsAnyItemCollapsable_OneExpandedParent(self):
        self.children[None] = ['item 0']
        self.children['item 0'] = ['item 0.0']
        self.treeCtrl.RefreshAllItems(2)
        parent = self.getFirstTreeItem()
        self.treeCtrl.Expand(parent)
        self.failUnless(self.treeCtrl.isAnyItemCollapsable())
           
    def testIsAnyItemExpandable_OneExpandedParent(self):
        self.children[None] = ['item 0']
        self.children['item 0'] = ['item 0.0']
        self.treeCtrl.RefreshAllItems(2)
        parent = self.getFirstTreeItem()
        self.treeCtrl.Expand(parent)
        self.failIf(self.treeCtrl.isAnyItemExpandable())

        
class TreeListCtrlTest(TreeCtrlTestCase, CommonTestsMixin):
    def setUp(self):
        super(TreeListCtrlTest, self).setUp()
        columns = [widgets.Column('subject', 'Subject')]
        self.treeCtrl = widgets.TreeListCtrl(self.frame, columns, self.onSelect, 
            dummy.DummyUICommand(), dummy.DummyUICommand(), dummy.DummyUICommand())
        imageList = wx.ImageList(16, 16)
        for bitmapName in ['task', 'tasks']:
            imageList.Add(wx.ArtProvider_GetBitmap(bitmapName, wx.ART_MENU, 
                          (16,16)))
        self.treeCtrl.AssignImageList(imageList) # pylint: disable-msg=E1101
    

class CheckTreeCtrlTest(TreeCtrlTestCase, CommonTestsMixin):
    def setUp(self):
        self.frame.getItemParentHasExclusiveChildren = lambda item: item.startswith('mutual')
        super(CheckTreeCtrlTest, self).setUp()
        columns = [widgets.Column('subject', 'Subject')]
        self.treeCtrl = widgets.CheckTreeCtrl(self.frame, columns,
            self.onSelect, self.onCheck, 
            dummy.DummyUICommand(), dummy.DummyUICommand())
        
    def getIsItemChecked(self, item): # pylint: disable-msg=W0613
        return False
    
    def onCheck(self, event):
        pass

    def testCheckParentDoesNotCheckChild(self):
        self.children[None] = ['item 0']
        self.children['item 0'] = ['item 0.0']
        self.treeCtrl.RefreshAllItems(2)
        self.treeCtrl.ExpandAll()
        parent = self.getFirstTreeItem()
        self.treeCtrl.CheckItem(parent)
        child = self.treeCtrl.GetItemChildren(parent)[0]
        self.failIf(child.IsChecked())
        
    def testCheckParentOfMutualExclusiveChildrenUnchecksAllChildren(self):
        self.children[None] = ['parent']
        self.children['parent'] = ['mutual 1', 'mutual 2']
        self.treeCtrl.RefreshAllItems(3)
        self.treeCtrl.ExpandAll()
        parent = self.getFirstTreeItem()
        children = self.treeCtrl.GetItemChildren(parent)
        self.treeCtrl.CheckItem(children[0])
        self.treeCtrl.CheckItem(parent)
        for child in children:
            self.failIf(child.IsChecked())
        
    def testCheckParentOfMutualExclusiveChildrenUnchecksAllChildrenRecursively(self):
        self.children[None] = ['parent']
        self.children['parent'] = ['mutual 1', 'mutual 2']
        self.children['mutual 1'] = ['1.1']
        self.treeCtrl.RefreshAllItems(4)
        self.treeCtrl.ExpandAll()
        parent = self.getFirstTreeItem()
        children = self.treeCtrl.GetItemChildren(parent, recursively=True)
        grandchild = children[1]
        self.treeCtrl.CheckItem(grandchild)
        self.treeCtrl.CheckItem(parent)
        self.failIf(grandchild.IsChecked())
        
    def testCheckMutualExclusiveChildUnchecksParent(self):
        self.children[None] = ['parent']
        self.children['parent'] = ['mutual 1', 'mutual 2']
        self.treeCtrl.RefreshAllItems(3)
        self.treeCtrl.ExpandAll()
        parent = self.getFirstTreeItem()
        children = self.treeCtrl.GetItemChildren(parent)
        self.treeCtrl.CheckItem(parent)
        self.treeCtrl.CheckItem(children[0])
        self.failIf(self.treeCtrl.IsItemChecked(parent))
