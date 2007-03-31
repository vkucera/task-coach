import wx

class AutoColumnWidthMixin(object):
    """ A mix-in class that automatically resizes one column to take up
        the remaining width of a control with columns (i.e. ListCtrl, 
        TreeListCtrl).

        This causes the control to automatically take up the full width 
        available, without either a horizontal scroll bar (unless absolutely
        necessary) or empty space to the right of the last column.

        NOTE:    When using this mixin with a ListCtrl, make sure the ListCtrl
                 is in report mode.

        WARNING: If you override the EVT_SIZE event in your control, make
                 sure you call event.Skip() to ensure that the mixin's
                 OnResize method is called.
    """
    def __init__(self, *args, **kwargs):
        self.ResizeColumn = kwargs.pop('resizeableColumn', -1)
        self.ResizeColumnMinWidth = kwargs.pop('resizeableColumnMinWidth', 50)
        super(AutoColumnWidthMixin, self).__init__(*args, **kwargs)
        self.Bind(wx.EVT_SIZE, self.OnResize)
        self.Bind(wx.EVT_LIST_COL_BEGIN_DRAG, self.OnBeginColumnDrag)
        self.Bind(wx.EVT_LIST_COL_END_DRAG, self.OnEndColumnDrag)
        
    def OnBeginColumnDrag(self, event):
        if event.GetColumn() == self.ResizeColumn:
            event.Veto()
        else:
            # Temporarily unbind the EVT_SIZE to prevent resizing during dragging
            self.Unbind(wx.EVT_SIZE)
            if '__WXMAC__' not in wx.PlatformInfo:
                event.Skip()
        
    def OnEndColumnDrag(self, event):
        self.Bind(wx.EVT_SIZE, self.OnResize)
        self.OnResize(event)
        event.Skip()
        
    def OnResize(self, event):
        if '__WXMSW__' in wx.PlatformInfo:
            wx.CallAfter(self.DoResize)
        else:
            self.DoResize()
        event.Skip()

    def DoResize(self):
        if not self:
            return # Avoid a potential PyDeadObject error
        if self.GetSize().height < 32:
            return # Avoid an endless update bug when the height is small.
        if self.GetColumnCount() == 0:
            return # Nothing to resize.

        resizeColumnWidth = self.ResizeColumnMinWidth
        unusedWidth = max(self.AvailableWidth - self.NecessaryWidth, 0)
        resizeColumnWidth += unusedWidth
        self.SetColumnWidth(self.ResizeColumn, resizeColumnWidth)
        
    def GetResizeColumn(self):
        if self._resizeColumn == -1:
            return self.GetColumnCount() - 1
        else:
            return self._resizeColumn
        
    def SetResizeColumn(self, columnIndex):
        self._resizeColumn = columnIndex

    ResizeColumn = property(GetResizeColumn, SetResizeColumn)
    
    def GetAvailableWidth(self):
        # NOTE: on GTK, the scrollbar is included in the client size, but on
        # Windows it is not included
        availableWidth = self.GetClientSize().width
        if self.GetItemCount() > self.GetCountPerPage():
            if (wx.Platform != '__WXMSW__') or (wx.Platform == '__WXMSW__' and \
                    isinstance(self, wx.gizmos.TreeListCtrl)):
                scrollbarWidth = wx.SystemSettings_GetMetric(wx.SYS_VSCROLL_X)
                availableWidth -= scrollbarWidth
        return availableWidth
    
    AvailableWidth = property(GetAvailableWidth)
    
    def GetNecessaryWidth(self):
        necessaryWidth = 0
        for columnIndex in range(self.GetColumnCount()):
            if columnIndex == self._resizeColumn:
                necessaryWidth += self.ResizeColumnMinWidth
            else:
                necessaryWidth += self.GetColumnWidth(columnIndex)
        return necessaryWidth
    
    NecessaryWidth = property(GetNecessaryWidth)
   
    # Override all methods that manipulate columns to be able to resize the
    # columns after any additions or removals. 
   
    def InsertColumn(self, *args, **kwargs):
        ''' Insert the new column and then resize. '''
        result = super(AutoColumnWidthMixin, self).InsertColumn(*args, **kwargs)
        self.DoResize()
        return result
        
    def DeleteColumn(self, *args, **kwargs):
        ''' Delete the column and then resize. '''
        result = super(AutoColumnWidthMixin, self).DeleteColumn(*args, **kwargs)
        self.DoResize()
        return result
        
    def RemoveColumn(self, *args, **kwargs):
        ''' Remove the column and then resize. '''
        result = super(AutoColumnWidthMixin, self).RemoveColumn(*args, **kwargs)
        self.DoResize()
        return result

    def AddColumn(self, *args, **kwargs):
        ''' Add the column and then resize. '''
        result = super(AutoColumnWidthMixin, self).AddColumn(*args, **kwargs)
        self.DoResize()
        return result

        