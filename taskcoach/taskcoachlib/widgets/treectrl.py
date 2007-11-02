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
        
    def OnGetItemExpanded(self, index):
        return self.getItemExpanded(index)

    def OnGetItemDescription(self, index, column=0):
        if column:
            return self.getItemDescription(index, column)
        else:
            return self.getItemDescription(index)

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
        self.Bind(wx.EVT_TREE_KEY_DOWN, self.onKeyDown)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.onItemActivated)
        # We deal with double clicks ourselves, to prevent the default behaviour
        # of collapsing or expanding nodes on double click. 
        self.Bind(wx.EVT_LEFT_DCLICK, self.onDoubleClick)
               
    def onKeyDown(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.editCommand(event)
        else:
            event.Skip()
         
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
        if not self._refreshing:
             # Use CallAfter to prevent handling the select while items are 
             # being deleted:
             wx.CallAfter(self.selectCommand) 
        event.Skip()
                    
    def onDoubleClick(self, event):
        if not self.isCollapseExpandButtonClicked(event):
            self.editCommand(event)
        event.Skip(False)
        
    def onItemActivated(self, event):
        self.editCommand(event)
        event.Skip(False)

    def isCollapseExpandButtonClicked(self, event):
        item, flags, column = self.HitTest(event.GetPosition(), 
                                           alwaysReturnColumn=True)
        return flags & wx.TREE_HITTEST_ONITEMBUTTON
        
    def getStyle(self):
        return wx.TR_DEFAULT_STYLE | wx.TR_HIDE_ROOT | wx.TR_MULTIPLE | \
            wx.TR_HAS_BUTTONS

    def setItemGetters(self, getItemText, getItemDescription, getItemImage, getItemAttr,
            getChildrenCount, getItemExpanded):
        self.getItemText = getItemText
        self.getItemDescription = getItemDescription
        self.getItemImage = getItemImage
        self.getItemAttr = getItemAttr
        self.getChildrenCount = getChildrenCount
        self.getItemExpanded = getItemExpanded
    
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
    def __init__(self, parent, getItemText, getItemDescription, getItemImage,
            getItemAttr, getChildrenCount, getItemExpanded, selectCommand, editCommand,
            dragAndDropCommand, itemPopupMenu=None, *args, **kwargs):
        super(TreeCtrl, self).__init__(parent, style=self.getStyle(), 
            itemPopupMenu=itemPopupMenu, *args, **kwargs)
        self.bindEventHandlers(selectCommand, editCommand, dragAndDropCommand)
        self.setItemGetters(getItemText, getItemDescription, getItemImage, getItemAttr,
            getChildrenCount, getItemExpanded)
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
    def __init__(self, parent, getItemText, getItemDescription, getItemImage,
            getItemAttr, getChildrenCount, getItemExpanded, selectCommand, editCommand,
            dragAndDropCommand, itemPopupMenu=None, *args, **kwargs):
        super(CustomTreeCtrl, self).__init__(parent, style=self.getStyle(), 
            itemPopupMenu=itemPopupMenu, *args, **kwargs)
        self.bindEventHandlers(selectCommand, editCommand, dragAndDropCommand)
        self.setItemGetters(getItemText, getItemDescription, getItemImage, getItemAttr,
            getChildrenCount, getItemExpanded)
        self.SetTreeStyle(self.getStyle()) # FIXME: Why is this necessary?
        self.refresh()
            
    # Adapters to make the CustomTreeCtrl API more like the TreeListCtrl API:
        
    def SelectAll(self):
        for item in self.GetItemChildren(recursively=True):
            if not self.IsSelected(item):
                self.SelectItem(item)
    
    def getStyle(self):
        return wx.TR_HAS_BUTTONS | wx.TR_HIDE_ROOT | wx.TR_MULTIPLE | \
            wx.WANTS_CHARS
            
    def onItemActivated(self, event):
        # Don't open the editor (see TreeMixin.onItemActivated) but let the 
        # default event handler (un)check the item:
        event.Skip()
    

class CheckTreeCtrl(CustomTreeCtrl):
    def __init__(self, parent, getItemText, getItemDescription, getItemImage,
            getItemAttr, getChildrenCount, getItemExpanded, getIsItemChecked,
            selectCommand, checkCommand, editCommand, dragAndDropCommand, 
            itemPopupMenu=None, *args, **kwargs):
        self.getIsItemChecked = getIsItemChecked
        super(CheckTreeCtrl, self).__init__(parent, getItemText, getItemDescription,
            getItemImage, getItemAttr, getChildrenCount, getItemExpanded,
            selectCommand, editCommand, dragAndDropCommand, 
            itemPopupMenu, *args, **kwargs)
        self.Bind(customtree.EVT_TREE_ITEM_CHECKED, checkCommand)
        
    def OnGetItemType(self, index):
        return 1
    
    def OnGetItemChecked(self, index):
        return self.getIsItemChecked(index)


class TreeListCtrl(itemctrl.CtrlWithItems, itemctrl.CtrlWithColumns, itemctrl.CtrlWithToolTip,
                   TreeMixin, gizmos.TreeListCtrl):
    # TreeListCtrl uses ALIGN_LEFT, ..., ListCtrl uses LIST_FORMAT_LEFT, ... for
    # specifying alignment of columns. This dictionary allows us to map from the 
    # ListCtrl constants to the TreeListCtrl constants:
    alignmentMap = {wx.LIST_FORMAT_LEFT: wx.ALIGN_LEFT, 
                    wx.LIST_FORMAT_CENTRE: wx.ALIGN_CENTRE,
                    wx.LIST_FORMAT_CENTER: wx.ALIGN_CENTER,
                    wx.LIST_FORMAT_RIGHT: wx.ALIGN_RIGHT}
    
    def __init__(self, parent, columns, getItemText, getItemDescription, getItemImage,
            getItemAttr, getChildrenCount, getItemExpanded, selectCommand, 
            editCommand, dragAndDropCommand,
            itemPopupMenu=None, columnPopupMenu=None, *args, **kwargs):    
        self.setItemGetters(getItemText, getItemDescription, getItemImage, getItemAttr,
            getChildrenCount, getItemExpanded)
        super(TreeListCtrl, self).__init__(parent, style=self.getStyle(), 
            columns=columns, resizeableColumn=0, itemPopupMenu=itemPopupMenu,
            columnPopupMenu=columnPopupMenu, *args, **kwargs)
        self.bindEventHandlers(selectCommand, editCommand, dragAndDropCommand)
        self.GetHeaderWindow().Bind(wx.EVT_LEFT_DOWN, 
            self.onHeaderWindowMouseClick)
        
    def onHeaderWindowMouseClick(self, event):
        # Mouse clicks in the header window seem not to be propagated to 
        # containing windows, but mouse clicks in the main window do. By 
        # simulating a mouse click in the main window we make sure that
        # if the TreeListCtrl is in a AUINotebook tab, the tab is properly
        # activated when the user clicks a column header.
        self.GetMainWindow().ProcessEvent(wx.MouseEvent(wx.wxEVT_LEFT_DOWN))
        event.Skip()

    # Extend CtrlWithColumns with TreeListCtrl specific behaviour:
        
    def _setColumns(self, *args, **kwargs):
        super(TreeListCtrl, self)._setColumns(*args, **kwargs)
        self.SetMainColumn(0)
                        
    # Extend TreeMixin with TreeListCtrl specific behaviour:

    def getStyle(self):
        return super(TreeListCtrl, self).getStyle() | wx.TR_FULL_ROW_HIGHLIGHT \
            | wx.WANTS_CHARS
        
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
