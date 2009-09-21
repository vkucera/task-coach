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

import wx, itemctrl, draganddrop
from taskcoachlib.thirdparty import hypertreelist
from taskcoachlib.thirdparty import customtreectrl as customtree

# pylint: disable-msg=E1101,E1103

class HyperTreeList(draganddrop.TreeCtrlDragAndDropMixin, 
                    hypertreelist.HyperTreeList):
    # pylint: disable-msg=W0223

    def GetSelections(self):
        ''' If the root item is hidden, it should never be selected, 
        unfortunately, CustomTreeCtrl and HyperTreeList allow it to be 
        selected. Override GetSelections to fix that. '''
        selections = super(HyperTreeList, self).GetSelections()
        if self.HasFlag(wx.TR_HIDE_ROOT):
            rootItem = self.GetRootItem()
            if rootItem and rootItem in selections:
                selections.remove(rootItem)
        return selections

    def GetMainWindow(self, *args, **kwargs):
        ''' Have a local GetMainWindow so we can create a MainWindow 
        property. '''
        return super(HyperTreeList, self).GetMainWindow(*args, **kwargs)
    
    MainWindow = property(fget=GetMainWindow)
    
    def HitTest(self, point):
        ''' Always return a three-tuple (item, flags, column). '''
        if type(point) == type(()):
            point = wx.Point(point[0], point[1])
        hitTestResult = super(HyperTreeList, self).HitTest(point)
        if len(hitTestResult) == 2:
            hitTestResult += (0,)
        if hitTestResult[0] is None:
            hitTestResult = (wx.TreeItemId(),) + hitTestResult[1:]
        return hitTestResult
    
    def isClickablePartOfNodeClicked(self, event):
        ''' Return whether the user double clicked some part of the node that
            can also receive regular mouse clicks. '''
        return self.isCollapseExpandButtonClicked(event)
    
    def isCollapseExpandButtonClicked(self, event):
        flags = self.HitTest(event.GetPosition())[1]
        return flags & wx.TREE_HITTEST_ONITEMBUTTON
            
    def isCheckBoxClicked(self, event):
        flags = self.HitTest(event.GetPosition())[1]
        return flags & customtree.TREE_HITTEST_ONITEMCHECKICON
      
    def expandAllItems(self):
        self.ExpandAll()

    def collapseAllItems(self):
        for item in self.GetItemChildren():
            self.Collapse(item)
            
    def expandSelectedItems(self):
        for item in self.GetSelections():
            self.Expand(item)
            for child in self.GetItemChildren(item, recursively=True):
                self.Expand(child)
                
    def collapseSelectedItems(self):
        for item in self.GetSelections():
            self.Collapse(item)

    def select(self, selection):
        for item in self.GetItemChildren(recursively=True):
            self.SelectItem(item, self.GetItemPyData(item) in selection)
        
    def clearselection(self):
        self.UnselectAll()
        self.selectCommand()

    def selectall(self):
        if self.GetCount() > 0:
            self.SelectAll()
        self.selectCommand()

    def invertselection(self):
        for item in self.GetItemChildren(recursively=True):
            self.ToggleItemSelection(item)
        self.selectCommand()
        
    def isSelectionCollapsable(self):
        for item in self.GetItemChildren(recursively=True):
            if item in self.GetSelections() and self.isItemCollapsable(item): 
                return True
        return False
    
    def isSelectionExpandable(self):
        for item in self.GetItemChildren(recursively=True):
            if item in self.GetSelections() and self.isItemExpandable(item): 
                return True
        return False
    
    def isAnyItemCollapsable(self):
        for item in self.GetItemChildren(recursively=True):
            if self.ItemHasChildren(item) and self.IsExpanded(item): 
                return True
        return False
    
    def isAnyItemExpandable(self):
        for item in self.GetItemChildren(recursively=True):
            if self.isItemExpandable(item): 
                return True
        return False
    
    def isExpandable(self, objects):
        for item in self.GetItemChildren(recursively=True):
            if self.GetItemPyData(item) in objects and self.isItemExpandable(item): 
                return True
        return False
    
    def isCollapsable(self, objects):
        for item in self.GetItemChildren(recursively=True):
            if self.GetItemPyData(item) in objects and self.isItemCollapsable(item): 
                return True
        return False
    
    def isItemExpandable(self, item):
        return self.ItemHasChildren(item) and not self.IsExpanded(item)
    
    def isItemCollapsable(self, item):
        return self.ItemHasChildren(item) and self.IsExpanded(item)
    

class TreeListCtrl(itemctrl.CtrlWithItemsMixin, itemctrl.CtrlWithColumnsMixin, 
                   itemctrl.CtrlWithToolTipMixin, HyperTreeList):
    # TreeListCtrl uses ALIGN_LEFT, ..., ListCtrl uses LIST_FORMAT_LEFT, ... for
    # specifying alignment of columns. This dictionary allows us to map from the 
    # ListCtrl constants to the TreeListCtrl constants:
    alignmentMap = {wx.LIST_FORMAT_LEFT: wx.ALIGN_LEFT, 
                    wx.LIST_FORMAT_CENTRE: wx.ALIGN_CENTRE,
                    wx.LIST_FORMAT_CENTER: wx.ALIGN_CENTER,
                    wx.LIST_FORMAT_RIGHT: wx.ALIGN_RIGHT}
    ct_type = 0
    
    def __init__(self, parent, columns, selectCommand, editCommand, 
                 dragAndDropCommand, itemPopupMenu=None, columnPopupMenu=None, 
                 *args, **kwargs):    
        self.__adapter = parent
        self.__selection = []
        super(TreeListCtrl, self).__init__(parent, style=self.getStyle(), 
            columns=columns, resizeableColumn=0, itemPopupMenu=itemPopupMenu,
            columnPopupMenu=columnPopupMenu, *args, **kwargs)
        self.bindEventHandlers(selectCommand, editCommand, dragAndDropCommand)

    def bindEventHandlers(self, selectCommand, editCommand, dragAndDropCommand):
        # pylint: disable-msg=W0201
        self.selectCommand = selectCommand
        self.editCommand = editCommand
        self.dragAndDropCommand = dragAndDropCommand
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.onSelect)
        self.Bind(wx.EVT_TREE_KEY_DOWN, self.onKeyDown)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.onItemActivated)
        # We deal with double clicks ourselves, to prevent the default behaviour
        # of collapsing or expanding nodes on double click. 
        self.GetMainWindow().Bind(wx.EVT_LEFT_DCLICK, self.onDoubleClick)
        
    def getItemTooltipData(self, item, column):
        return self.__adapter.getItemTooltipData(item, column)
    
    def curselection(self):
        return [self.GetItemPyData(item) for item in self.GetSelections()]
    
    def RefreshAllItems(self, count=0):
        self.DeleteAllItems()
        rootItem = self.GetRootItem()
        if not rootItem:
            rootItem = self.AddRoot('Hidden root')
        self._addObjectRecursively(rootItem)
            
    def RefreshItems(self, *objects):
        self._refreshTargetObjects(self.GetRootItem(), *objects)
            
    def _refreshTargetObjects(self, parentItem, *targetObjects):
        childItem, cookie = self.GetFirstChild(parentItem)
        while childItem:
            itemObject = self.GetItemPyData(childItem) 
            if itemObject in targetObjects:
                self._refreshObject(childItem, itemObject)
            self._refreshTargetObjects(childItem, *targetObjects)
            childItem, cookie = self.GetNextChild(parentItem, cookie)
            
    def _addObjectRecursively(self, parentItem, parentObject=None):
        for childObject in self.__adapter.children(parentObject):
            childItem = self.AppendItem(parentItem, '', self.ct_type, 
                                        data=childObject)
            self._refreshObject(childItem, childObject)
            self._addObjectRecursively(childItem, childObject)  
            if self.__adapter.getItemExpanded(childObject):
                self.Expand(childItem)
            
    def _refreshObject(self, item, domainObject):
        for columnIndex in range(self.GetColumnCount()):
            text = self.__adapter.getItemText(domainObject, columnIndex)
            if text:
                self.SetItemText(item, text, columnIndex)                
            for which in (wx.TreeItemIcon_Expanded, wx.TreeItemIcon_Normal):
                image = self.__adapter.getItemImage(domainObject, which, columnIndex)
                if image >= 0:
                    self.SetItemImage(item, image, 
                                      column=columnIndex, which=which)
        fgColor = self.__adapter.getColor(domainObject)
        if fgColor:
            self.SetItemTextColour(item, fgColor)
        bgColor = self.__adapter.getBackgroundColor(domainObject)
        if bgColor:
            self.SetItemBackgroundColour(item, bgColor)
        self.SelectItem(item, domainObject in self.__selection)

    # Event handlers
    
    def onSelect(self, event):
        # Use CallAfter to prevent handling the select while items are 
        # being deleted:
        self.__selection = self.curselection()
        wx.CallAfter(self.selectCommand) 
        event.Skip()

    def onKeyDown(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.editCommand(event)
        else:
            event.Skip()
         
    def OnDrop(self, dropItem, dragItem):
        dropItem = None if dropItem == self.GetRootItem() else \
                   self.GetItemPyData(dropItem)
        dragItem = self.GetItemPyData(dragItem)
        self.dragAndDropCommand(dropItem, dragItem)
                
    def onDoubleClick(self, event):
        if self.isClickablePartOfNodeClicked(event):
            event.Skip(False)
        else:
            self.onItemActivated(event)
        
    def onItemActivated(self, event):
        ''' Attach the column clicked on to the event so we can use it elsewhere. '''
        mousePosition = self.GetMainWindow().ScreenToClient(wx.GetMousePosition())
        item, _, column = self.HitTest(mousePosition)
        if item:
            # Only get the column name if the hittest returned an item,
            # otherwise the item was activated from the menu or by double 
            # clicking on a portion of the tree view not containing an item.
            column = max(0, column) # FIXME: Why can the column be -1?
            event.columnName = self._getColumn(column).name()
        self.editCommand(event)
        event.Skip(False)        
        
    # Override CtrlWithColumnsMixin with TreeListCtrl specific behaviour:
        
    def _setColumns(self, *args, **kwargs):
        super(TreeListCtrl, self)._setColumns(*args, **kwargs)
        self.SetMainColumn(0)
                        
    # Extend TreeMixin with TreeListCtrl specific behaviour:

    def getStyle(self):
        return (wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT | wx.TR_MULTIPLE \
            | wx.TR_HAS_BUTTONS | wx.TR_FULL_ROW_HIGHLIGHT | wx.WANTS_CHARS \
            | customtree.TR_HAS_VARIABLE_ROW_HEIGHT) & ~hypertreelist.TR_NO_HEADER 

    # Adapters to make the TreeListCtrl more like the ListCtrl
    
    def GetItemCount(self):
        return self.GetCount()
    
    def DeleteColumn(self, columnIndex):
        self.RemoveColumn(columnIndex)
        
    def InsertColumn(self, columnIndex, columnHeader, *args, **kwargs):
        format = self.alignmentMap[kwargs.pop('format', wx.LIST_FORMAT_LEFT)]
        if columnIndex == self.GetColumnCount():
            self.AddColumn(columnHeader, *args, **kwargs)
        else:
            super(TreeListCtrl, self).InsertColumn(columnIndex, columnHeader, 
                *args, **kwargs)
        # Put a default value in the new column otherwise GetItemText will fail
        for item in self.GetItemChildren(recursively=True):
            self.SetItemText(item, '', self.GetColumnCount()-1)
            self.SetItemImage(item, -1, column=self.GetColumnCount()-1)
        self.SetColumnAlignment(columnIndex, format)
    

class CheckTreeCtrl(TreeListCtrl):
    ct_type = 1
    
    def __init__(self, parent, columns, selectCommand, checkCommand, 
                 editCommand, dragAndDropCommand, itemPopupMenu=None, 
                 *args, **kwargs):
        super(CheckTreeCtrl, self).__init__(parent, columns,
            selectCommand, editCommand, dragAndDropCommand, 
            itemPopupMenu, *args, **kwargs)
        self.Bind(hypertreelist.EVT_TREE_ITEM_CHECKED, checkCommand)
        self.getIsItemChecked = parent.getIsItemChecked
        
    def _refreshObject(self, item, domainObject):
        super(CheckTreeCtrl, self)._refreshObject(item, domainObject)
        self.CheckItem(item, self.getIsItemChecked(domainObject))
        
    def onItemActivated(self, event):
        if self.isDoubleClicked(event):
            # Invoke super.onItemActivated to edit the item
            super(CheckTreeCtrl, self).onItemActivated(event)
        else:
            # Item is activated, let another event handler deal with the event 
            event.Skip()
            
    def isDoubleClicked(self, event):
        return hasattr(event, 'LeftDClick') and event.LeftDClick()
