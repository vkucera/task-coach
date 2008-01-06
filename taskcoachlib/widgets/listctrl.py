import wx, itemctrl

class _ListCtrl(wx.ListCtrl):
    ''' Make ListCtrl API more like the TreeList and TreeListCtrl API '''
    
    def HitTest(self, (x,y), alwaysReturnColumn=False):
        ''' Return a three-tuple (item, flag, column) if alwaysReturnColumn is
        True. '''
        index, flags = super(_ListCtrl, self).HitTest((x,y))
        if alwaysReturnColumn:
            column = 0
            if self.InReportView():
                # Determine the column in which the user clicked
                cumulativeColumnWidth = 0
                for columnIndex in range(self.GetColumnCount()):
                    cumulativeColumnWidth += self.GetColumnWidth(columnIndex)
                    if x <= cumulativeColumnWidth:
                        column = columnIndex
                        break
            return index, flags, column
        else:
            return index, flags

    def ToggleItemSelection(self, index):
        currentState = self.GetItemState(index, wx.LIST_STATE_SELECTED)
        self.SetItemState(index, ~currentState, wx.LIST_STATE_SELECTED)
     
        
class VirtualListCtrl(itemctrl.CtrlWithItems, itemctrl.CtrlWithColumns, itemctrl.CtrlWithToolTip, _ListCtrl):
    def __init__(self, parent, columns, getItemText, getItemTooltipText, getItemImage,
            getItemAttr, selectCommand=None, editCommand=None, itemPopupMenu=None, 
            columnPopupMenu=None, resizeableColumn=0, *args, **kwargs):
        super(VirtualListCtrl, self).__init__(parent,
            style=wx.LC_REPORT|wx.LC_VIRTUAL, columns=columns, 
            resizeableColumn=resizeableColumn, itemPopupMenu=itemPopupMenu, 
            columnPopupMenu=columnPopupMenu, *args, **kwargs)
        self.getItemText = getItemText
        self.getItemTooltipText = getItemTooltipText
        self.getItemImage = getItemImage
        self.getItemAttr = getItemAttr
        self.bindEventHandlers(selectCommand, editCommand)
            
    def bindEventHandlers(self, selectCommand, editCommand):
        if selectCommand:
            self.selectCommand = selectCommand
            self.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.onSelect)
            self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)
            self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onSelect)
        if editCommand:
            self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, editCommand)  

    def OnGetItemText(self, rowIndex, columnIndex):
        return self.getItemText(rowIndex, columnIndex)

    def OnGetItemTooltipText(self, rowIndex, columnIndex):
        return self.getItemTooltipText(rowIndex, columnIndex)

    def OnGetItemImage(self, rowIndex):
        return self.getItemImage(rowIndex, wx.TreeItemIcon_Normal, 0)[0]
    
    def OnGetItemColumnImage(self, rowIndex, columnIndex):
        return self.getItemImage(rowIndex, wx.TreeItemIcon_Normal, columnIndex)

    def OnGetItemAttr(self, rowIndex):
        # We need to keep a reference to the item attribute to prevent it
        # from being garbage collected too soon.
        self.__itemAttribute = self.getItemAttr(rowIndex)
        return self.__itemAttribute
        
    def onSelect(self, event):
        self.selectCommand()

    def RefreshItems(self):
        if self.GetItemCount(): 
            # Only invoke RefreshItems if there's something to refresh
            # Note: RefreshItems will only refresh visible items, no need for
            # us to calculate which items are visible.
            super(VirtualListCtrl, self).RefreshItems(0, self.GetItemCount()-1)
        
    def refresh(self, count):
        ''' Refresh the contents of the (visible part of the) ListCtrl '''
        self.SetItemCount(count)
        if count == 0:
            self.DeleteAllItems()
        else:
            self.RefreshItems()
        
    def refreshItem(self, index):
        self.RefreshItem(index)
        
    def curselection(self):
        return wx.lib.mixins.listctrl.getListCtrlSelection(self)

    def select(self, indices):
        for index in range(self.GetItemCount()):
            self.Select(index, index in indices)
    
    def clearselection(self):
        for index in self.curselection():
            self.Select(index, False)

    def selectall(self):
        for index in range(self.GetItemCount()):
            self.Select(index)

    def invertselection(self):
        for index in range(self.GetItemCount()):
            self.ToggleItemSelection(index)
        self.selectCommand()            


class ListCtrl(VirtualListCtrl):
    pass
    
