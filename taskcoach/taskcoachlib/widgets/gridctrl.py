import wx.grid as grid
import wx

class GridCtrl(grid.Grid):
    def __init__(self, parent, gridTable, *args, **kwargs):
        super(GridCtrl, self).__init__(parent, *args, **kwargs)
        self.gridTable = gridTable
        self.SetTable(gridTable, True)
        self.SetLabelFont(wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT))
        self._rows, self._cols = gridTable.GetNumberRows(), gridTable.GetNumberCols()
        
    def GetItemCount(self):
        return self.GetNumberRows()
        
    def refresh(self, count=0):
        table = self.GetTable()
        self.BeginBatch()
        for current, new, delmsg, addmsg in [
            (self._rows, table.GetNumberRows(), grid.GRIDTABLE_NOTIFY_ROWS_DELETED, grid.GRIDTABLE_NOTIFY_ROWS_APPENDED),
            (self._cols, table.GetNumberCols(), grid.GRIDTABLE_NOTIFY_COLS_DELETED, grid.GRIDTABLE_NOTIFY_COLS_APPENDED),
        ]:
            if new < current:
                msg = grid.GridTableMessage(table, delmsg, new, current-new)
                self.ProcessTableMessage(msg)
            elif new > current:
                msg = grid.GridTableMessage(table, addmsg, new-current)
                self.ProcessTableMessage(msg)
                self.UpdateValues()
        self.EndBatch()
        self._rows, self._cols = table.GetNumberRows(), table.GetNumberCols()
        # update the scrollbars and the displayed part of the grid
        self.AdjustScrollbars()
        self.ForceRefresh()

    def refreshItem(self, row):
        self.refresh()
        
    def UpdateValues(self):
        # This sends an event to the grid table to update all of the values
        msg = grid.GridTableMessage(self.GetTable(), grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        self.ProcessTableMessage(msg)


        