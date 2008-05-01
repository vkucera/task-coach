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

import wx
import TreeCtrlTest
from unittests import dummy
from taskcoachlib import widgets


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
        
