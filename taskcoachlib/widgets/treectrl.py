import wx, itemctrl
import wx.gizmos as gizmos
from wx.lib import customtreectrl as customtree
from thirdparty import treemixin
        
class TreeMixin(treemixin.VirtualTree, treemixin.DragAndDrop):
    ''' Methods common to both TreeCtrl and TreeListCtrl. '''
    
    def __init__(self, *args, **kwargs):
        self._refreshing = False
        super(TreeMixin, self).__init__(*args, **kwargs)
        
    def OnGetChildrenCount(self, index):
        return self.getChildrenCount(index)
        
    def OnGetItemText(self, index, column=0):
        if column:
            return self.getItemText(index, column)
        else:
            return self.getItemText(index)
        
    def OnGetItemImage(self, index, which, column=0):
        if column:
            return self.getItemImage(index, which, column)
        else:
            return self.getItemImage(index, which)
        
    def OnGetItemTextColour(self, index):
        return self.getItemAttr(index).GetTextColour()

    def bindEventHandlers(self, selectCommand, editCommand, dragAndDropCommand):
        self.selectCommand = selectCommand
        self.editCommand = editCommand
        self.dragAndDropCommand = dragAndDropCommand
        self.__settingFocus = False
        self.Bind(wx.EVT_SET_FOCUS, self.onSetFocus)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.onSelect)
        self.Bind(wx.EVT_TREE_SEL_CHANGING, self.onSelectionChanging)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, editCommand)
        # We deal with double clicks ourselves, to prevent the default behaviour
        # of collapsing or expanding nodes on double click. 
        self.Bind(wx.EVT_LEFT_DCLICK, self.onDoubleClick)
         
    def OnDrop(self, dropItem, dragItem):
        if dropItem == self.GetRootItem():
            dropItemIndex = -1
        else:
            dropItemIndex = self.GetIndexOfItem(dropItem)
        self.dragAndDropCommand(dropItemIndex, self.GetIndexOfItem(dragItem))
                
    def onSetFocus(self, event):
        # When the TreeCtrl gets focus sometimes the selection is changed.
        # We want to prevent that from happening, so we need to keep track
        # of the fact that we have just received a EVT_SET_FOCUS
        self.__settingFocus = True
        event.Skip()

    def onSelectionChanging(self, event):
        if self._refreshing or self.__settingFocus:
            self.__settingFocus = False
            event.Veto()
        else:
            event.Skip()
        
    def onSelect(self, event):
        #print 'onSelect:begin'
        if not self._refreshing:
            self.selectCommand()
        event.Skip()
        #print 'onSelect:end'
                    
    def onDoubleClick(self, event):
        if not self.isCollapseExpandButtonClicked(event):
            self.editCommand(event)
        event.Skip(False)

    def isCollapseExpandButtonClicked(self, event):
        item, flags, column = self.HitTest(event.GetPosition())
        return flags & wx.TREE_HITTEST_ONITEMBUTTON
    
    def __getitem__(self, index):
        ''' Return the item at position index in the *model* which is not
            necessarily the same index as in the Tree(List)Ctrl. '''
        for item in self.GetItemChildren(recursively=True):
            if self.GetIndexOfItem(item) == index:
                return item
        raise IndexError
        
    def GetItem(self, index):
        ''' Return the item at position index in the *Tree(List)Ctrl* which is
            not necessarily the same index as in the model. This method also 
            mimics the ListCtrl API. '''
        for cursorIndex, item in enumerate(self.GetItemChildren(recursively=True)):
            if index == cursorIndex:
                return item
        raise IndexError
        
    def getStyle(self):
        return wx.TR_HIDE_ROOT | wx.TR_MULTIPLE | wx.TR_HAS_BUTTONS

    def setItemGetters(self, getItemText, getItemImage, getItemAttr,
            getChildrenCount):
        self.getItemText = getItemText
        self.getItemImage = getItemImage
        self.getItemAttr = getItemAttr
        self.getChildrenCount = getChildrenCount
    
    def GetItemCount(self):
        return self.GetCount()

    def refresh(self, count=0):
        self.RefreshItems()
                 
    def expandAllItems(self):
        self.ExpandAll()

    def collapseAllItems(self):
        for item in self.GetItemChildren():
            self.CollapseAndReset(item)
            
    def expandSelectedItems(self):
        for item in self.GetSelections():
            self.Expand(item)
            for child in self.GetItemChildren(item, recursively=True):
                self.Expand(child)
                
    def collapseSelectedItems(self):
        for item in self.GetSelections():
            self.CollapseAndReset(item)

    def curselection(self):
        return [self.GetIndexOfItem(item) for item in self.GetSelections()]
        
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
        return self.isCollapsable(self.GetSelections())
    
    def isSelectionExpandable(self):
        return self.isExpandable(self.GetSelections())
    
    def isAnyItemCollapsable(self):
        return self.isCollapsable(self.GetItemChildren(recursively=True))
    
    def isAnyItemExpandable(self):
        return self.isExpandable(self.GetItemChildren(recursively=True))
    
    def isExpandable(self, items):
        for item in items:
            if self.ItemHasChildren(item) and not self.IsExpanded(item):
                return True
        return False
    
    def isCollapsable(self, items):
        for item in items:
            if self.ItemHasChildren(item) and self.IsExpanded(item):
                return True
        return False


class TreeCtrl(itemctrl.CtrlWithItems, TreeMixin, wx.TreeCtrl):
    def __init__(self, parent, getItemText, getItemImage, getItemAttr,
            getChildrenCount, selectCommand, editCommand, dragAndDropCommand,
            itemPopupMenu=None, *args, **kwargs):
        super(TreeCtrl, self).__init__(parent, style=self.getStyle(), 
            itemPopupMenu=itemPopupMenu, *args, **kwargs)
        self.bindEventHandlers(selectCommand, editCommand, dragAndDropCommand)
        self.setItemGetters(getItemText, getItemImage, getItemAttr,
            getChildrenCount)
        self.refresh()
     
    def getStyle(self):
        # Adding wx.TR_LINES_AT_ROOT is necessary to make the buttons 
        # (wx.TR_HAS_BUTTONS) appear. I think this is a bug in wx.TreeCtrl.
        return super(TreeCtrl, self).getStyle() | wx.TR_LINES_AT_ROOT

    # Adapters to make the TreeCtrl API more like the TreeListCtrl API:
        
    def SelectAll(self):
        for item in self.GetItemChildren(recursively=True):
            self.SelectItem(item)
    

class CustomTreeCtrl(itemctrl.CtrlWithItems, TreeMixin, customtree.CustomTreeCtrl): 
    def __init__(self, parent, getItemText, getItemImage, getItemAttr,
            getChildrenCount, selectCommand,
            editCommand, dragAndDropCommand, 
            itemPopupMenu=None, *args, **kwargs):
        super(CustomTreeCtrl, self).__init__(parent, style=self.getStyle(), 
            itemPopupMenu=itemPopupMenu, *args, **kwargs)
        self.bindEventHandlers(selectCommand, editCommand, dragAndDropCommand)
        self.setItemGetters(getItemText, getItemImage, getItemAttr,
            getChildrenCount)
        self.refresh()
            
    # Adapters to make the CustomTreeCtrl API more like the TreeListCtrl API:
        
    def SelectAll(self):
        for item in self.GetItemChildren(recursively=True):
            self.SelectItem(item)
    
    def getStyle(self):
        return super(CustomTreeCtrl, self).getStyle() & ~wx.TR_LINES_AT_ROOT


class CheckTreeCtrl(CustomTreeCtrl):
    def __init__(self, parent, getItemText, getItemImage, getItemAttr,
            getChildrenCount, getIsItemChecked,
            selectCommand, checkCommand, editCommand, dragAndDropCommand, 
            itemPopupMenu=None, *args, **kwargs):
        self.getIsItemChecked = getIsItemChecked
        super(CheckTreeCtrl, self).__init__(parent, getItemText, getItemImage, 
            getItemAttr, getChildrenCount, 
            selectCommand, editCommand, dragAndDropCommand, 
            itemPopupMenu, *args, **kwargs)
        self.Bind(customtree.EVT_TREE_ITEM_CHECKED, checkCommand)
    
    def OnGetItemType(self, index):
        return 1
    
    def OnGetItemChecked(self, index):
        return self.getIsItemChecked(index)
                

class TreeListCtrl(itemctrl.CtrlWithItems, itemctrl.CtrlWithColumns, TreeMixin, 
                   gizmos.TreeListCtrl):
    # TreeListCtrl uses ALIGN_LEFT, ..., ListCtrl uses LIST_FORMAT_LEFT, ... for
    # specifying alignment of columns. This dictionary allows us to map from the 
    # ListCtrl constants to the TreeListCtrl constants:
    alignmentMap = {wx.LIST_FORMAT_LEFT: wx.ALIGN_LEFT, 
                    wx.LIST_FORMAT_CENTRE: wx.ALIGN_CENTRE,
                    wx.LIST_FORMAT_CENTER: wx.ALIGN_CENTER,
                    wx.LIST_FORMAT_RIGHT: wx.ALIGN_RIGHT}
    
    def __init__(self, parent, columns, getItemText, getItemImage, getItemAttr,
            getChildrenCount, selectCommand, 
            editCommand, dragAndDropCommand,
            itemPopupMenu=None, columnPopupMenu=None, *args, **kwargs):    
        self.setItemGetters(getItemText, getItemImage, getItemAttr,
            getChildrenCount)
        super(TreeListCtrl, self).__init__(parent, style=self.getStyle(), 
            columns=columns, resizeableColumn=0, itemPopupMenu=itemPopupMenu,
            columnPopupMenu=columnPopupMenu, *args, **kwargs)
        self.bindEventHandlers(selectCommand, editCommand, dragAndDropCommand)
        self.refresh()
        
    # Extend CtrlWithColumns with TreeListCtrl specific behaviour:
        
    def _setColumns(self, *args, **kwargs):
        super(TreeListCtrl, self)._setColumns(*args, **kwargs)
        self.SetMainColumn(0)
                        
    # Extend TreeMixin with TreeListCtrl specific behaviour:

    def getStyle(self):
        return super(TreeListCtrl, self).getStyle() | wx.TR_FULL_ROW_HIGHLIGHT
        
    def allItems(self):
        for rowIndex in range(self._count):
            try:
                yield rowIndex, self[rowIndex]
            except IndexError:
                pass # Item is hidden
            
    # Adapters to make the TreeListCtrl API more like the TreeCtrl API:
        
    def SelectItem(self, item, select=True):
        ''' SelectItem takes an item and an optional boolean that indicates 
            whether the item should be selected (True, default) or unselected 
            (False). This makes SelectItem more similar to 
            TreeCtrl.SelectItem. '''
        if select:
            self.selectItems(item)
        elif not select and self.IsSelected(item):
            # Take the current selection and remove item from it. This is a
            # bit more wordy then I'd like, but TreeListCtrl has no 
            # UnselectItem.
            currentSelection = self.GetSelections()
            currentSelection.remove(item)
            self.UnselectAll()
            self.selectItems(*currentSelection)
    
    def selectItems(self, *items):
        for item in items:
            if not self.IsSelected(item):
                super(TreeListCtrl, self).SelectItem(item, unselect_others=False)
        
    def ToggleItemSelection(self, item):
        ''' TreeListCtrl doesn't have a ToggleItemSelection. '''
        self.SelectItem(item, not self.IsSelected(item))
        
    # Adapters to make the TreeListCtrl more like the ListCtrl
    
    def DeleteColumn(self, columnIndex):
        assert columnIndex < self.GetColumnCount()
        self.RemoveColumn(columnIndex)
        self.RefreshItems()
        
    def InsertColumn(self, columnIndex, columnHeader, *args, **kwargs):
        format = self.alignmentMap[kwargs.pop('format', wx.LIST_FORMAT_LEFT)]
        if columnIndex == self.GetColumnCount():
            self.AddColumn(columnHeader, *args, **kwargs)
        else:
            super(TreeListCtrl, self).InsertColumn(columnIndex, columnHeader, 
                *args, **kwargs)
        # Put a default value in the new column otherwise GetItemText will fail
        for item in self.GetItemChildren(recursively=True):
            self.SetItemText(item, '', columnIndex)
        self.SetColumnAlignment(columnIndex, format)
        print 'treectrl.TreeListCtrl.InsertColumn %s done, before refresh'%columnHeader
        self.RefreshItems()
        print 'treectrl.TreeListCtrl.InsertColumn %s done, after refresh'%columnHeader
    
    def GetCountPerPage(self):
        ''' ListCtrlAutoWidthMixin expects a GetCountPerPage() method,
            else it will throw an AttributeError. So for controls that have
            no such method (such as TreeListCtrl), we have to add it
            ourselves. '''
        count = 0
        item = self.GetFirstVisibleItem()
        while item:
            count += 1
            item = self.GetNextVisible(item)
        return count
