import wx, itemctrl

class _ListCtrl(wx.ListCtrl):
    ''' Make ListCtrl API more like the TreeList and TreeListCtrl API '''
    
    def HitTest(self, (x,y)):
        ''' Allways return a three-tuple (item, flag, column). '''
        index, flags = super(_ListCtrl, self).HitTest((x,y))
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

    def ToggleItemSelection(self, index):
        currentState = self.GetItemState(index, wx.LIST_STATE_SELECTED)
        self.SetItemState(index, ~currentState, wx.LIST_STATE_SELECTED)
     
        
class VirtualListCtrl(itemctrl.CtrlWithItems, itemctrl.CtrlWithColumns, _ListCtrl):
    def __init__(self, parent, columns, getItemText, getItemImage, getItemAttr, 
            selectCommand=None, editCommand=None, itemPopupMenu=None, 
            columnPopupMenu=None, resizeableColumn=1, *args, **kwargs):
        super(VirtualListCtrl, self).__init__(parent, -1, 
            style=wx.LC_REPORT|wx.LC_VIRTUAL, columns=columns, 
            resizeableColumn=resizeableColumn, itemPopupMenu=itemPopupMenu, 
            columnPopupMenu=columnPopupMenu, *args, **kwargs)
        self.getItemText = getItemText
        self.getItemImage = getItemImage
        self.getItemAttr = getItemAttr
        self.bindEventHandlers(selectCommand, editCommand)
            
    def bindEventHandlers(self, selectCommand, editCommand):
        if selectCommand:
            self.selectCommand = selectCommand
            self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)
            self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onSelect)
        if editCommand:
            self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, editCommand)  

    def OnGetItemText(self, rowIndex, columnIndex):
        return self.getItemText(rowIndex, self._getColumn(columnIndex))

    def OnGetItemImage(self, index):
        return self.getItemImage(index)

    def OnGetItemAttr(self, index):
        return self.getItemAttr(index)
        
    def onSelect(self, event):
        self.selectCommand()
        
    def refresh(self, count):
        ''' Refresh the contents of the (visible part of the) ListCtrl '''
        self.SetItemCount(count)
        if count == 0:
            self.DeleteAllItems()
        else:
            startRow = self.GetTopItem()
            stopRow = min(startRow + self.GetCountPerPage(), 
                          self.GetItemCount() - 1)
            self.RefreshItems(startRow, stopRow) 
            self.Refresh() # FIXME: Refresh not necessary?

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
    
