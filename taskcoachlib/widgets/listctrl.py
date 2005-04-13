import wx, wx.lib.mixins.listctrl


class VirtualListCtrl(wx.ListCtrl, wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin):
    def __init__(self, parent, columns, getItemText, getItemImage, getItemAttr, 
            selectCommand=None, editCommand=None, popupMenu=None, *args, **kwargs):
        super(VirtualListCtrl, self).__init__(parent, -1, 
            style=wx.LC_REPORT|wx.LC_VIRTUAL, *args, **kwargs)
        wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin.__init__(self)
        for index, column in enumerate(columns):
            self.InsertColumn(index, column)
        self.setResizeColumn(self.getResizableColumn())
        self.getItemText = getItemText
        self.getItemImage = getItemImage
        self.getItemAttr = getItemAttr
        if selectCommand:
            self.selectCommand = selectCommand
            self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)
        if editCommand:
            self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, editCommand.onCommandActivate)
        if popupMenu:
            self.popupMenu = popupMenu
            self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.onPopup)
    
    def getResizableColumn(self):
        return 1
        
    def SetColumnWidth(self, column, width, *args, **kwargs):
        minwidth = 80
        if width != 0 and width < minwidth: width = minwidth
        super(VirtualListCtrl, self).SetColumnWidth(column, width, *args, **kwargs)
        if column != self.getResizableColumn() and width == 0:
            self.resizeColumn(self.getResizableColumn())
        
    def OnGetItemText(self, index, column):
        return self.getItemText(index, column)

    def OnGetItemImage(self, index):
        return self.getItemImage(index)

    def OnGetItemAttr(self, index):
        return self.getItemAttr(index)

    def onPopup(self, event):
        self.PopupMenu(self.popupMenu, event.GetPoint())    

    def onSelect(self, event):
        self.selectCommand()
        event.Skip()

    def refresh(self, count):
        ''' Refresh the contents of the (visible part of the) ListCtrl '''
        self.SetItemCount(count)
        if count == 0:
            self.DeleteAllItems()
        else:
            startRow = self.GetTopItem()
            stopRow = min(startRow + self.GetCountPerPage(), self.GetItemCount() - 1)
            self.RefreshItems(startRow, stopRow) 
            self.Refresh()

    def curselection(self):
        return wx.lib.mixins.listctrl.getListCtrlSelection(self)

    def select(self, indices):
        for index in range(self.GetItemCount()):
            self.Select(index, index in indices)
        if indices:
            self.EnsureVisible(indices[0])        
    
    def clearselection(self):
        for index in self.curselection():
            self.Select(index, False)

    def selectall(self):
        for index in range(self.GetItemCount()):
            self.Select(index)

    def invertselection(self):
        for index in range(self.GetItemCount()):
            currentState = self.GetItemState(index, wx.LIST_STATE_SELECTED)
            self.SetItemState(index, ~currentState, wx.LIST_STATE_SELECTED)
        self.selectCommand()            


class ListCtrl(VirtualListCtrl):
    def __init__(self, parent, columns, getItemText, getItemImage,
            getItemAttr, selectCommand, editCommand, popupMenu=None):
        super(ListCtrl, self).__init__(parent, columns, getItemText, getItemImage, 
            getItemAttr, selectCommand, editCommand, popupMenu)
        self.Bind(wx.EVT_LIST_COL_BEGIN_DRAG, self.onBeginColumnDrag)
        
    def onBeginColumnDrag(self, event):
        # FIXME: if the user sets the width of a column to 0 she can't
        # make it wider anymore. 
        column = event.GetColumn()
        if column >= 0 and self.GetColumnWidth(column) == 0:
            event.Veto()


class EffortListCtrl(VirtualListCtrl):
    def __init__(self, parent, columns, getItemText, getItemImage, getItemAttr, 
            selectCommand=None, editCommand=None, popupMenu=None, *args, **kwargs):
        super(EffortListCtrl, self).__init__(parent, columns, getItemText, getItemImage, 
            getItemAttr, selectCommand, editCommand, popupMenu, *args, **kwargs)
        
    def getResizableColumn(self):
        return 2