import wx, wx.lib.mixins.listctrl


class VirtualListCtrl(wx.ListCtrl, wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin):
    def __init__(self, parent, columns, getItemText, getItemImage, getItemAttr, 
            selectCommand=None, editCommand=None, popupMenu=None, 
            columnPopupMenu=None, sorters=None, sortOrderCommand=None, 
            resizeableColumn=1, *args, **kwargs):
        super(VirtualListCtrl, self).__init__(parent, -1, 
            style=wx.LC_REPORT|wx.LC_VIRTUAL, *args, **kwargs)
        wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin.__init__(self)
        self._resizeableColumn = resizeableColumn
        self.setColumns(columns, sorters or [])
        self.getItemText = getItemText
        self.getItemImage = getItemImage
        self.getItemAttr = getItemAttr
        if selectCommand:
            self.selectCommand = selectCommand
            self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)
            self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onSelect)
        if editCommand:
            self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, editCommand.onCommandActivate)
        if popupMenu:
            self.popupMenu = popupMenu
            self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.onPopup)
        if columnPopupMenu is not None:
            self.columnPopupMenu = columnPopupMenu
            self.Bind(wx.EVT_LIST_COL_RIGHT_CLICK, self.onColumnPopup)
        if sorters is not None:
            self.Bind(wx.EVT_LIST_COL_CLICK, self.onColumnClick)
            
    def setColumns(self, columns, sorters):
        self.allColumnHeaders = columns
        for columnIndex, columnHeader in enumerate(columns):
            self.InsertColumn(columnIndex, columnHeader)
        self.setResizeColumn(self._resizeableColumn)
        self.sorters = {}
        for columnIndex, columnSorter in enumerate(sorters):
            self.sorters[self.getColumnHeader(columnIndex)] = columnSorter
                       
    def OnGetItemText(self, rowIndex, columnIndex):
        return self.getItemText(rowIndex, self.getColumnHeader(columnIndex))

    def OnGetItemImage(self, index):
        return self.getItemImage(index)

    def OnGetItemAttr(self, index):
        return self.getItemAttr(index)

    def onPopup(self, event):
        self.PopupMenu(self.popupMenu, event.GetPoint())    

    def onColumnPopup(self, event):
        self.PopupMenu(self.columnPopupMenu, event.GetPoint())
        
    def onSelect(self, event):
        self.selectCommand()
        
    def onColumnClick(self, event):
        self.sorters[self.getColumnHeader(event.GetColumn())].onCommandActivate(event)
    
    def _clearColumnImages(self):
        for columnIndex in range(self.GetColumnCount()):
            listItem = self.GetColumn(columnIndex)
            listItem.SetImage(-1)
            self.SetColumn(columnIndex, listItem)
            
    def showSort(self, columnHeader, imageIndex):
        columnIndex = self.getColumnIndex(columnHeader)
        listItem = self.GetColumn(columnIndex)
        if self.isColumnVisible(columnHeader) and listItem.GetImage() == imageIndex:
            return
        self._clearColumnImages()
        self.showColumn(columnHeader)
        listItem.SetImage(imageIndex)
        self.SetColumn(columnIndex, listItem)

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

    def showColumn(self, columnHeader, show=True):
        if columnHeader not in self.allColumnHeaders:
            raise ValueError
        columnIndex = self.getColumnIndex(columnHeader)
        if show and not self.isColumnVisible(columnHeader):
            self.InsertColumn(columnIndex, columnHeader)
        elif not show and self.isColumnVisible(columnHeader):
            self.DeleteColumn(columnIndex)
            self.resizeColumn(self._resizeableColumn)

    def getColumnHeader(self, columnIndex):
        return self.GetColumn(columnIndex).GetText()
        
    def getColumnIndex(self, columnHeader):
        for columnIndex in range(self.GetColumnCount()):
            displayedHeader = self.getColumnHeader(columnIndex)
            if self.allColumnHeaders.index(displayedHeader) >= self.allColumnHeaders.index(columnHeader):
                return columnIndex
        return self.GetColumnCount() # Not found

    def isColumnVisible(self, columnHeader):
        for columnIndex in range(self.GetColumnCount()):
            displayedHeader = self.getColumnHeader(columnIndex)
            if displayedHeader == columnHeader:
                return True
        return False

                
class ListCtrl(VirtualListCtrl):
    pass
    
    
class EffortListCtrl(VirtualListCtrl):
    def __init__(self, *args, **kwargs):
        kwargs['resizeableColumn'] = 2
        super(EffortListCtrl, self).__init__(*args, **kwargs)   
