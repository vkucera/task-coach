''' Base classes for controls with items, such as ListCtrl, TreeCtrl, 
    and TreeListCtrl. '''


import wx, wx.lib.mixins.listctrl, draganddrop, autowidth


class _CtrlWithItems(object):
    ''' Base class for controls with items, such as ListCtrl, TreeCtrl,
        TreeListCtrl, etc. '''

    def _itemIsOk(self, item):
        try:
            return item.IsOk()          # for Tree(List)Ctrl
        except AttributeError:
            return item != wx.NOT_FOUND # for ListCtrl

    def SelectItem(self, item, **kwargs):
        try:
            # Tree(List)Ctrl:
            super(_CtrlWithItems, self).SelectItem(item, **kwargs)
        except AttributeError:
            # ListCtrl:
            select = kwargs.get('select', True)
            newState = wx.LIST_STATE_SELECTED
            if not select:
                newState = ~newState
            self.SetItemState(item, newState, wx.LIST_STATE_SELECTED)


class _CtrlWithPopupMenu(_CtrlWithItems):
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
        # Make sure the item under the mouse is selected because that
        # is what users expect and what is most user-friendly. Not all
        # widgets do this by default, e.g. the TreeListCtrl does not.
        item, flags, column = self.HitTest(event.GetPoint())
        if not self._itemIsOk(item):
            return
        if not self.IsSelected(item):
            self.UnselectAll()
            self.SelectItem(item)
        self.PopupMenu(self.__popupMenu)


class _CtrlWithColumnPopupMenu(_CtrlWithPopupMenu):
    ''' This class enables a right-click popup menu on column headers. The 
        popup menu should expect a public property columnIndex to be set so 
        that the control can tell the menu which column the user clicked to
        popup the menu. '''
    
    def __init__(self, *args, **kwargs):
        self.__popupMenu = kwargs.pop('columnPopupMenu')
        super(_CtrlWithColumnPopupMenu, self).__init__(*args, **kwargs)
        if self.__popupMenu is not None:
            self._attachPopupMenu(self, [wx.EVT_LIST_COL_RIGHT_CLICK],
                self.onColumnPopupMenu)
        
    def onColumnPopupMenu(self, event):
        # We store the columnIndex in the menu, because it's near to 
        # impossible for commands in the menu to determine on what column the
        # menu was popped up.
        columnIndex = event.GetColumn()
        self.__popupMenu.columnIndex = columnIndex
        self.PopupMenu(self.__popupMenu, event.GetPosition())
        

class _CtrlWithFileDropTarget(_CtrlWithItems):
    ''' Control that accepts files being dropped onto items. '''
    
    def __init__(self, *args, **kwargs):
        self.__onDropFilesCallback = kwargs.pop('onDropFiles', None)
        super(_CtrlWithFileDropTarget, self).__init__(*args, **kwargs)
        if self.__onDropFilesCallback:
            dropTarget = draganddrop.FileDropTarget(self.onDropFiles, self.onDragOver)
            self.GetMainWindow().SetDropTarget(dropTarget)

    def onDropFiles(self, x, y, filenames):
        item, flags, column = self.HitTest((x, y))
        if self._itemIsOk(item):
            self.__onDropFilesCallback(self.index(item), filenames)
        
    def onDragOver(self, x, y, defaultResult):
        item, flags, column = self.HitTest((x, y))
        if self._itemIsOk(item):
            if flags & wx.TREE_HITTEST_ONITEMBUTTON:
                self.Expand(item)
            return defaultResult
        else:
            return wx.DragNone
        
    def index(self, item):
        # Convert the item into an index. For ListCtrls this is not 
        # necessary, so an AttributeError will be raised. In that case the
        # item is already an index, so we can simply return the item.
        try:
            return super(_CtrlWithFileDropTarget, self).index(item)
        except AttributeError:
            return item

    def GetMainWindow(self):
        try:
            return super(_CtrlWithFileDropTarget, self).GetMainWindow()
        except AttributeError:
            return self
        
        
class CtrlWithItems(_CtrlWithItemPopupMenu, _CtrlWithFileDropTarget):
    pass


class Column(object):
    def __init__(self, columnHeader, *eventTypes, **kwargs):
        self.__columnHeader = columnHeader
        self.width = kwargs.pop('width', wx.gizmos.DEFAULT_COL_WIDTH)
        # The event types to use for registering an oberver that is
        # interested in changes that affect this column:
        self.__eventTypes = eventTypes
        self.__visibilitySetting = kwargs.pop('visibilitySetting', None)
        self.__sortKey = kwargs.pop('sortKey', None)
        self.__sortCallback = kwargs.pop('sortCallback', None)
        self.__renderCallback = kwargs.pop('renderCallback',
            self.defaultRenderer)
        self.__alignment = kwargs.pop('alignment', wx.LIST_FORMAT_LEFT)
        self.__imageIndexCallback = kwargs.pop('imageIndexCallback', 
            self.defaultImageIndex)
        # NB: because the header image is needed for sorting a fixed header
        # image cannot be combined with a sortable column
        self.__headerImageIndex = kwargs.pop('headerImageIndex', -1)
        
    def header(self):
        return self.__columnHeader
    
    def headerImageIndex(self):
        return self.__headerImageIndex

    def eventTypes(self):
        return self.__eventTypes

    def visibilitySetting(self):
        return self.__visibilitySetting

    def sortKey(self):
        return self.__sortKey
    
    def sort(self, *args, **kwargs):
        if self.__sortCallback:
            self.__sortCallback(*args, **kwargs)
        
    def render(self, *args, **kwargs):
        return self.__renderCallback(*args, **kwargs)

    def defaultRenderer(self, *args, **kwargs):
        return unicode(args[0])

    def alignment(self):
        return self.__alignment
    
    def defaultImageIndex(self, *args, **kwargs):
        return -1
    
    def imageIndex(self, *args, **kwargs):
        return self.__imageIndexCallback(*args, **kwargs)
        
    def __eq__(self, other):
        return self.header() == other.header()
        

class _BaseCtrlWithColumns(object):
    ''' A base class for all controls with columns. Note that this class and 
        its subclasses do not support addition or deletion of columns after 
        the initial setting of columns. '''

    def __init__(self, *args, **kwargs):
        self.__allColumns = kwargs.pop('columns')
        super(_BaseCtrlWithColumns, self).__init__(*args, **kwargs)
        self._setColumns()
        
    def _setColumns(self):
        for columnIndex, column in enumerate(self.__allColumns):
            self._insertColumn(columnIndex, column)
            
    def _insertColumn(self, columnIndex, column):
        print '_BaseCtrlWithColumns._insertColumn(columnIndex=%s, column=%s)'%(columnIndex, column.header())
        self.InsertColumn(columnIndex, column.header(), 
            format=column.alignment(), width=column.width)
        print '_BaseCtrlWithColumn._insertColumn after calling self.InsertColumn'
        columnInfo = self.GetColumn(columnIndex)
        columnInfo.SetImage(column.headerImageIndex())
        self.SetColumn(columnIndex, columnInfo)
        print '_BaseCtrlWithColumn._insertColumn done'
            
    def _allColumns(self):
        return self.__allColumns

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

        
class _CtrlWithHideableColumns(_BaseCtrlWithColumns):        
    ''' This class supports hiding columns. '''
    
    def showColumn(self, column, show=True):
        ''' showColumn shows or hides the column for column. 
            The column is actually removed or inserted into the control because 
            although TreeListCtrl supports hiding columns, ListCtrl does not. 
            '''
        columnIndex = self._getColumnIndex(column.header())
        if show and not self.isColumnVisible(column):
            self._insertColumn(columnIndex, column)
        elif not show and self.isColumnVisible(column):
            self.DeleteColumn(columnIndex)

    def isColumnVisible(self, column):
        return column in self.__visibleColumns()

    def _getColumnIndex(self, columnHeader):
        ''' _getColumnIndex returns the actual columnIndex of the column if it 
            is visible, or the position it would have if it were visible. '''
        columnIndexWhenAllColumnsVisible = super(_CtrlWithHideableColumns, self)._getColumnIndex(columnHeader)
        for columnIndex, visibleColumn in enumerate(self.__visibleColumns()):
            if super(_CtrlWithHideableColumns, self)._getColumnIndex(visibleColumn.header()) >= columnIndexWhenAllColumnsVisible:
                return columnIndex
        return self.GetColumnCount() # Column header not found
    
    def _getColumn(self, columnIndex):
        columnHeader = self._getColumnHeader(columnIndex)
        for column in self._allColumns():
            if columnHeader == column.header():
                return column
        raise IndexError

    def __visibleColumns(self):
        return [self._getColumn(columnIndex) for columnIndex in range(self.GetColumnCount())]


class _CtrlWithSortableColumns(_BaseCtrlWithColumns):
    ''' This class adds sort indicators and clickable column headers that 
        trigger callbacks to (re)sort the contents of the control. '''
    
    def __init__(self, *args, **kwargs):
        super(_CtrlWithSortableColumns, self).__init__(*args, **kwargs)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.onColumnClick)
        self.__currentSortColumn = self._getColumn(0)
        self.__currentSortImageIndex = -1
        
    def onColumnClick(self, event):
        self._getColumn(event.GetColumn()).sort(event)
        
    def showSortColumn(self, column):
        if column != self.__currentSortColumn:
            self._clearSortImage()
        self.__currentSortColumn = column
        self._showSortImage()

    def showSortOrder(self, imageIndex):
        self.__currentSortImageIndex = imageIndex
        self._showSortImage()
                
    def _clearSortImage(self):
        self.__setSortColumnImage(-1)
    
    def _showSortImage(self):
        self.__setSortColumnImage(self.__currentSortImageIndex)
            
    def _currentSortColumn(self):
        return self.__currentSortColumn
        
    def __setSortColumnImage(self, imageIndex):
        columnIndex = self._getColumnIndex(self.__currentSortColumn.header())
        columnInfo = self.GetColumn(columnIndex)
        if columnInfo.GetImage() == imageIndex:
            pass # The column is already showing the right image, so we're done
        else:
            columnInfo.SetImage(imageIndex)
            self.SetColumn(columnIndex, columnInfo)


class CtrlWithColumns(autowidth.AutoColumnWidthMixin, _CtrlWithHideableColumns,
                      _CtrlWithSortableColumns, _CtrlWithColumnPopupMenu):
    ''' CtrlWithColumns combines the functionality of its four parent classes: 
        automatic resizing of columns, hideable columns, columns with sort 
        indicators, and column popup menu's. '''
        
    def showColumn(self, column, show=True):
        super(CtrlWithColumns, self).showColumn(column, show)
        # Show sort indicator if the column that was just made visible is being sorted on
        if show and column == self._currentSortColumn():
            self._showSortImage()
            
    def _clearSortImage(self):
        # Only clear the sort image if the column in question is visible
        if self.isColumnVisible(self._currentSortColumn()):
            super(CtrlWithColumns, self)._clearSortImage()
            
    def _showSortImage(self):
        # Only show the sort image if the column in question is visible
        if self.isColumnVisible(self._currentSortColumn()):
            super(CtrlWithColumns, self)._showSortImage()
        
