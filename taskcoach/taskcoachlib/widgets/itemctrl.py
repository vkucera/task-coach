''' Base classes for controls with items, such as ListCtrl, TreeCtrl, 
    and TreeListCtrl. '''


import wx, wx.lib.mixins.listctrl


class _CtrlWithPopupMenu(object):
    ''' Base class for controls with popupmenu's. '''
    
    @staticmethod
    def _attachPopupMenu(eventSource, eventTypes, eventHandler):
        for eventType in eventTypes:
            eventSource.Bind(eventType, eventHandler)


class _CtrlWithItemPopupMenu(_CtrlWithPopupMenu):
    ''' Popupmenu's on items. '''

    def __init__(self, *args, **kwargs):
        self.__popupMenu = kwargs.pop('itemPopupMenu')
        super(_CtrlWithItemPopupMenu, self).__init__(*args, **kwargs)
        if self.__popupMenu is not None:
            self._attachPopupMenu(self,
                (wx.EVT_LIST_ITEM_RIGHT_CLICK, wx.EVT_TREE_ITEM_RIGHT_CLICK), 
                self.onItemPopupMenu)

    def onItemPopupMenu(self, event):
        self.PopupMenu(self.__popupMenu)


class _CtrlWithColumnPopupMenu(_CtrlWithPopupMenu):
    ''' This class enables a right-click popup menu on column headers. '''
    
    def __init__(self, *args, **kwargs):
        self.__popupMenu = kwargs.pop('columnPopupMenu')
        super(_CtrlWithColumnPopupMenu, self).__init__(*args, **kwargs)
        if self.__popupMenu is not None:
            self._attachPopupMenu(self.GetHeaderWindow(), [wx.EVT_LIST_COL_RIGHT_CLICK],
                self.onColumnPopupMenu)
        
    def onColumnPopupMenu(self, event):
        self.PopupMenu(self.__popupMenu, event.GetPosition())
        
    def GetHeaderWindow(self):
        ''' This method is automatically overridden by TreeListCtrl.GetHeaderWindow(),
            which returns the window containing the column headers, when this class 
            is mixed in with TreeListCtrl. '''
        return self



class CtrlWithItems(_CtrlWithItemPopupMenu):
    pass


class Column(object):
    def __init__(self, columnHeader):
        self.__columnHeader = columnHeader
        
    def header(self):
        return self.__columnHeader
        
    def __eq__(self, other):
        return self.header() == other.header()
        

class _BaseCtrlWithColumns(object):
    ''' A base class for all controls with columns. Note that most manipulation of
        columns (in derived classes) is done by use of the column header instead of 
        a column index. This class provides two utility methods to help converting
        column indices to column headers and vice versa. Note that this class and its 
        subclasses do not support addition or deletion of columns after the initial 
        setting of columns. '''

    def __init__(self, *args, **kwargs):
        self.__allColumns = kwargs.pop('columnHeaders')
        super(_BaseCtrlWithColumns, self).__init__(*args, **kwargs)
        self._setColumns()

    def _setColumns(self):
        for columnIndex, column in enumerate(self.__allColumns):
            self.InsertColumn(columnIndex, column.header())

    def _getColumn(self, columnIndex):
        return self.__allColumns[columnIndex]
   
    def _getColumnHeader(self, columnIndex):
        ''' The currently displayed column header in the column with index columnIndex. '''
        return self.GetColumn(columnIndex).GetText()

    def _getColumnIndex(self, columnHeader):
        ''' The current column index of the column with the column header columnHeader. '''
        for columnIndex, column in enumerate(self.__allColumns):
            if column.header() == columnHeader:
                return columnIndex
        raise ValueError, '%s: unknown column header'%columnHeader

 
class _CtrlWithAutoResizeableColumns(_BaseCtrlWithColumns, wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin):
    ''' This class is responsible for automatic resizing of a column. The 
        resizeable column should be passed as resizeableColumn keyword argument
        to the constructor. '''
        
    def __init__(self, *args, **kwargs):
        self.__resizeableColumn = kwargs.pop('resizeableColumn')
        self.__minColumnWidth = 80 # Some rather arbitrary minimum width
        super(_CtrlWithAutoResizeableColumns, self).__init__(*args, **kwargs)
      
    def _setColumns(self, *args, **kwargs):
        # We initialize ListCtrlAutoWidthMixin here, because _setColumns() is
        # invoked by _BaseCtrlWithColumns.__init__() and ListCtrlAutoWidthMixin
        # must be initialized before the first column is added (which happens in
        # _BaseCtrlWithColumns._setColumns().
        wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin.__init__(self)
        super(_CtrlWithAutoResizeableColumns, self)._setColumns(*args, **kwargs)
        self.setResizeColumn(self.__resizeableColumn)
    
    def __getattribute__(self, attribute):
        ''' Return a wrapper method that first calls InsertColumn or DeleteColumn on the
            super class and then resizes the resizeable column. '''
        if attribute in ['InsertColumn', 'DeleteColumn']:
            def manipulateColumnAndResize(*args, **kwargs):
                # First, get method from super class and call it
                super(_CtrlWithAutoResizeableColumns, self).__getattribute__(attribute)(*args, **kwargs)
                # Next, resize the column(s)
                self.resizeColumn(self.__minColumnWidth)
            return manipulateColumnAndResize
        else:
            return super(_CtrlWithAutoResizeableColumns, self).__getattribute__(attribute)


class _CtrlWithHideableColumns(_BaseCtrlWithColumns):        
    ''' This class supports hiding columns. '''
    
    def showColumn(self, columnHeader, show=True):
        ''' showColumn shows or hides the column for columnHeader. 
            The column is actually removed or inserted into the control because although
            TreeListCtrl supports hiding columns, ListCtrl does not. '''
        columnIndex = self._getColumnIndex(columnHeader)
        if show and not self.isColumnVisible(columnHeader):
            self.InsertColumn(columnIndex, columnHeader)
        elif not show and self.isColumnVisible(columnHeader):
            self.DeleteColumn(columnIndex)

    def isColumnVisible(self, columnHeader):
        return columnHeader in self.__visibleColumnHeaders()

    def _getColumnIndex(self, columnHeader):
        ''' _getColumnIndex returns the actual columnIndex of the column if it is visible, or
            the position it would have if it were visible. '''
        columnIndexWhenAllColumnsVisible = super(_CtrlWithHideableColumns, self)._getColumnIndex(columnHeader)
        for columnIndex, visibleColumnHeader in enumerate(self.__visibleColumnHeaders()):
            if super(_CtrlWithHideableColumns, self)._getColumnIndex(visibleColumnHeader) >= columnIndexWhenAllColumnsVisible:
                return columnIndex
        return self.GetColumnCount() # Not found

    def __visibleColumnHeaders(self):
        return [self._getColumnHeader(columnIndex) for columnIndex in range(self.GetColumnCount())]



class _CtrlWithSortableColumns(_BaseCtrlWithColumns):
    ''' This class adds sort indicators and clickable column headers that trigger
        callbacks to (re)sort the contents of the control. '''
    
    def __init__(self, *args, **kwargs):
        ''' _CtrlWithSortableColumns(columnSortCommands={columnHeader:sorter, columnHeader:sorter, ...})
            The columnSortCommands dictionary contains one callable for each column header. 
            The callbacks should expect one argument: the event. '''
        
        self.__sorters = kwargs.pop('columnSortCommands')
        super(_CtrlWithSortableColumns, self).__init__(*args, **kwargs)
        self.__attachColumnSortCommands()
        
    def __attachColumnSortCommands(self):
        ''' columnSortCommands is a list of callables, one for each column and in
            the same order as the columns were passed to setColumns. The callbacks
            should expect one argument: the event. '''
        if self.__sorters is not None:
            self.Bind(wx.EVT_LIST_COL_CLICK, self.onColumnClick)
        self.__currentSortColumnHeader = self._getColumnHeader(0)
        self.__currentSortImageIndex = -1
        
    def onColumnClick(self, event):
        self.__sorters[self._getColumnHeader(event.GetColumn())](event)
        
    def showSort(self, columnHeader, imageIndex):
        if columnHeader != self.__currentSortColumnHeader:
            self._clearSortImage()
        self.__currentSortColumnHeader = columnHeader
        self.__currentSortImageIndex = imageIndex
        self._showSortImage()

    def showSortColumn(self, columnHeader):
        if columnHeader != self.__currentSortColumnHeader:
            self._clearSortImage()
        self.__currentSortColumnHeader = columnHeader
        self._showSortImage()

    def showSortOrder(self, imageIndex):
        self.__currentSortImageIndex = imageIndex
        self._showSortImage()
                
    def _clearSortImage(self):
        self.__setSortColumnImage(-1)
    
    def _showSortImage(self):
        self.__setSortColumnImage(self.__currentSortImageIndex)
        
    def _currentSortColumnHeader(self):
        return self.__currentSortColumnHeader
        
    def __setSortColumnImage(self, imageIndex):
        columnIndex = self._getColumnIndex(self.__currentSortColumnHeader)
        columnInfo = self.GetColumn(columnIndex)
        if columnInfo.GetImage() == imageIndex:
            pass # The column is already showing the right image, so we're done
        else:
            columnInfo.SetImage(imageIndex)
            self.SetColumn(columnIndex, columnInfo)


class CtrlWithColumns(_CtrlWithAutoResizeableColumns, _CtrlWithHideableColumns,
                      _CtrlWithSortableColumns, _CtrlWithColumnPopupMenu):
    ''' CtrlWithColumns combines the functionality of its four parent classes: automatic
        resizing of columns, hideable columns, columns with sort indicators, and
        column popup menu's. '''
        
    def showColumn(self, columnHeader, show=True):
        super(CtrlWithColumns, self).showColumn(columnHeader, show)
        # Show sort indicator if the column that was just made visible is being sorted on
        if show and columnHeader == self._currentSortColumnHeader():
            self._showSortImage()
            
    def _clearSortImage(self):
        # Only clear the sort image if the column in question is visible
        if self.isColumnVisible(self._currentSortColumnHeader()):
            super(CtrlWithColumns, self)._clearSortImage()
            
    def _showSortImage(self):
        # Only show the sort image if the column in question is visible
        if self.isColumnVisible(self._currentSortColumnHeader()):
            super(CtrlWithColumns, self)._showSortImage()
        