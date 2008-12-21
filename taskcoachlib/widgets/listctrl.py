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
    def __init__(self, parent, columns, getItemText, getItemTooltipData, getItemImage,
            getItemAttr, selectCommand=None, editCommand=None, itemPopupMenu=None, 
            columnPopupMenu=None, resizeableColumn=0, *args, **kwargs):
        super(VirtualListCtrl, self).__init__(parent,
            style=wx.LC_REPORT|wx.LC_VIRTUAL, columns=columns, 
            resizeableColumn=resizeableColumn, itemPopupMenu=itemPopupMenu, 
            columnPopupMenu=columnPopupMenu, *args, **kwargs)
        self.getItemText = getItemText
        self.getItemTooltipData = getItemTooltipData
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
            self.editCommand = editCommand
            self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onItemActivated)  

    def OnGetItemText(self, rowIndex, columnIndex):
        return self.getItemText(rowIndex, columnIndex)

    def OnGetItemTooltipData(self, rowIndex, columnIndex):
        return self.getItemTooltipData(rowIndex, columnIndex)

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
        self.selectCommand(event)
        
    def onItemActivated(self, event):
        ''' Override default behavior to attach the column clicked on
            to the event so we can use it elsewhere. '''
        mousePosition = self.GetMainWindow().ScreenToClient(wx.GetMousePosition())
        index, flags, column = self.HitTest(mousePosition, alwaysReturnColumn=True)
        if index >= 0:
            # Only get the column name if the hittest returned an item,
            # otherwise the item was activated from the menu or by double 
            # clicking on a portion of the tree view not containing an item.
            column = max(0, column) # FIXME: Why can the column be -1?
            event.columnName = self._getColumn(column).name()
        self.editCommand(event)

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
        if self.curselection():
            self.Focus(self.GetFirstSelected())        
    
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
    
