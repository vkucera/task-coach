'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>
Copyright (C) 2007 Jerome Laheurte <fraca7@free.fr>

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

''' Base classes for controls with items, such as ListCtrl, TreeCtrl, 
    and TreeListCtrl. '''


import wx, wx.lib.mixins.listctrl, operator, draganddrop, autowidth, tooltip

class _CtrlWithItems(object):
    ''' Base class for controls with items, such as ListCtrl, TreeCtrl,
        TreeListCtrl, etc. '''

    def _itemIsOk(self, item):
        try:
            return item.IsOk()          # for Tree(List)Ctrl
        except AttributeError:
            return item != wx.NOT_FOUND # for ListCtrl

    def SelectItem(self, item, *args, **kwargs):
        try:
            # Tree(List)Ctrl:
            super(_CtrlWithItems, self).SelectItem(item, *args, **kwargs)
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
        # Make sure the window this control is in has focus:
        event.GetEventObject().MainWindow.SetFocus()
        # Make sure the item under the mouse is selected because that
        # is what users expect and what is most user-friendly. Not all
        # widgets do this by default, e.g. the TreeListCtrl does not.
        item, flags, column = self.HitTest(event.GetPoint(), 
                                           alwaysReturnColumn=True)
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
        # Because right-clicking on column headers does not automatically give
        # focus to the control, we force the focus:
        event.GetEventObject().MainWindow.SetFocus()
        self.PopupMenu(self.__popupMenu, event.GetPosition())
        event.Skip()
        

class _CtrlWithDropTarget(_CtrlWithItems):
    ''' Control that accepts files, e-mails or URLs being dropped onto items. '''
    
    def __init__(self, *args, **kwargs):
        self.__onDropURLCallback = kwargs.pop('onDropURL', None)
        self.__onDropFilesCallback = kwargs.pop('onDropFiles', None)
        self.__onDropMailCallback = kwargs.pop('onDropMail', None)
        super(_CtrlWithDropTarget, self).__init__(*args, **kwargs)
        if self.__onDropURLCallback or self.__onDropFilesCallback or self.__onDropMailCallback:
            dropTarget = draganddrop.DropTarget(self.onDropURL,
                                                self.onDropFiles,
                                                self.onDropMail,
                                                self.onDragOver)
            self.GetMainWindow().SetDropTarget(dropTarget)

    def onDropURL(self, x, y, url):
        item, flags, column = self.HitTest((x, y), alwaysReturnColumn=True)
        if self.__onDropURLCallback:
            if self._itemIsOk(item):
                self.__onDropURLCallback(self.GetIndexOfItem(item), url)
            else:
                self.__onDropURLCallback(None, url)

    def onDropFiles(self, x, y, filenames):
        item, flags, column = self.HitTest((x, y), alwaysReturnColumn=True)
        if self.__onDropFilesCallback:
            if self._itemIsOk(item):
                self.__onDropFilesCallback(self.GetIndexOfItem(item), filenames)
            else:
                self.__onDropFilesCallback(None, filenames)

    def onDropMail(self, x, y, mail):
        item, flags, column = self.HitTest((x, y), alwaysReturnColumn=True)
        if self.__onDropMailCallback:
            if self._itemIsOk(item):
                self.__onDropMailCallback(self.GetIndexOfItem(item), mail)
            else:
                self.__onDropMailCallback(None, mail)

    def onDragOver(self, x, y, defaultResult):
        item, flags, column = self.HitTest((x, y), alwaysReturnColumn=True)
        if self._itemIsOk(item):
            if flags & wx.TREE_HITTEST_ONITEMBUTTON:
                self.Expand(item)
        return defaultResult
        
    def GetIndexOfItem(self, item):
        # Convert the item into an index. For ListCtrls this is not 
        # necessary, so an AttributeError will be raised. In that case the
        # item is already an index, so we can simply return the item.
        try:
            return super(_CtrlWithDropTarget, self).GetIndexOfItem(item)
        except AttributeError:
            return item

    def GetMainWindow(self):
        try:
            return super(_CtrlWithDropTarget, self).GetMainWindow()
        except AttributeError:
            return self


class CtrlWithToolTip(_CtrlWithItems, tooltip.ToolTipMixin):
    ''' Control that has a different tooltip for each item '''
    def __init__(self, *args, **kwargs):
        super(CtrlWithToolTip, self).__init__(*args, **kwargs)
        self.__tip = tooltip.SimpleToolTip(self)
        
    def GetIndexOfItem(self, item):
        try:
            return super(CtrlWithToolTip, self).GetIndexOfItem(item)
        except AttributeError:
            return item

    def OnBeforeShowToolTip(self, x, y):
        item, flags, column = self.HitTest((x, y), alwaysReturnColumn=True)
        if self._itemIsOk(item):
            tooltipData = self.OnGetItemTooltipData(self.GetIndexOfItem(item), column)
            doShow = reduce(operator.__or__,
                            map(bool, [data[1] for data in tooltipData]),
                            False)
            if doShow:
                self.__tip.SetData(tooltipData)
                return self.__tip
        return None


class CtrlWithItems(_CtrlWithItemPopupMenu, _CtrlWithDropTarget):
    pass


class Column(object):
    def __init__(self, name, columnHeader, *eventTypes, **kwargs):
        self.__name = name
        self.__columnHeader = columnHeader
        self.width = kwargs.pop('width', wx.gizmos.DEFAULT_COL_WIDTH)
        # The event types to use for registering an oberver that is
        # interested in changes that affect this column:
        self.__eventTypes = eventTypes
        self.__sortCallback = kwargs.pop('sortCallback', None)
        self.__renderCallback = kwargs.pop('renderCallback',
            self.defaultRenderer)
        self.__renderDescriptionCallback = kwargs.pop('renderDescriptionCallback',
            self.defaultDescriptionRenderer)
        self.__resizeCallback = kwargs.pop('resizeCallback', None)
        self.__alignment = kwargs.pop('alignment', wx.LIST_FORMAT_LEFT)
        self.__imageIndexCallback = kwargs.pop('imageIndexCallback', 
            self.defaultImageIndex)
        # NB: because the header image is needed for sorting a fixed header
        # image cannot be combined with a sortable column
        self.__headerImageIndex = kwargs.pop('headerImageIndex', -1)
        
    def name(self):
        return self.__name
        
    def header(self):
        return self.__columnHeader
    
    def headerImageIndex(self):
        return self.__headerImageIndex

    def eventTypes(self):
        return self.__eventTypes
    
    def setWidth(self, width):
        self.width = width
        if self.__resizeCallback:
            self.__resizeCallback(self, width)

    def sort(self, *args, **kwargs):
        if self.__sortCallback:
            self.__sortCallback(*args, **kwargs)
        
    def render(self, *args, **kwargs):
        return self.__renderCallback(*args, **kwargs)

    def renderDescription(self, *args, **kwargs):
        return self.__renderDescriptionCallback(*args, **kwargs)

    def defaultRenderer(self, *args, **kwargs):
        return unicode(args[0])

    def defaultDescriptionRenderer(self, *args, **kwargs):
        return None

    def alignment(self):
        return self.__alignment
    
    def defaultImageIndex(self, *args, **kwargs):
        return -1
    
    def imageIndex(self, *args, **kwargs):
        return self.__imageIndexCallback(*args, **kwargs)
        
    def __eq__(self, other):
        return self.name() == other.name()
        

class _BaseCtrlWithColumns(object):
    ''' A base class for all controls with columns. Note that this class and 
        its subclasses do not support addition or deletion of columns after 
        the initial setting of columns. '''

    def __init__(self, *args, **kwargs):
        self.__allColumns = kwargs.pop('columns')
        super(_BaseCtrlWithColumns, self).__init__(*args, **kwargs)
        # This  is  used to  keep  track  of  which column  has  which
        # index. The only  other way would be (and  was) find a column
        # using its header, which causes problems when several columns
        # have the same header. It's a list of (index, column) tuples.
        self.__indexMap = []
        self._setColumns()

    def _setColumns(self):
        for columnIndex, column in enumerate(self.__allColumns):
            self._insertColumn(columnIndex, column)
            
    def _insertColumn(self, columnIndex, column):
        newMap = []
        for colIndex, col in self.__indexMap:
            if colIndex >= columnIndex:
                newMap.append((colIndex + 1, col))
            else:
                newMap.append((colIndex, col))
        newMap.append((columnIndex, column))
        self.__indexMap = newMap

        self.InsertColumn(columnIndex, column.header(), 
            format=column.alignment(), width=column.width)

        columnInfo = self.GetColumn(columnIndex)
        columnInfo.SetImage(column.headerImageIndex())
        self.SetColumn(columnIndex, columnInfo)

    def _deleteColumn(self, columnIndex):
        newMap = []
        for colIndex, col in self.__indexMap:
            if colIndex > columnIndex:
                newMap.append((colIndex - 1, col))
            elif colIndex < columnIndex:
                newMap.append((colIndex, col))
        self.__indexMap = newMap

        self.DeleteColumn(columnIndex)

    def _allColumns(self):
        return self.__allColumns

    def _getColumn(self, columnIndex):
        for colIndex, col in self.__indexMap:
            if colIndex == columnIndex:
                return col
        raise IndexError
   
    def _getColumnHeader(self, columnIndex):
        ''' The currently displayed column header in the column with index 
            columnIndex. '''
        return self.GetColumn(columnIndex).GetText()

    def _getColumnIndex(self, column):
        ''' The current column index of the column 'column'. '''
        try:
            return self.__allColumns.index(column) # Uses overriden __eq__
        except ValueError:
            raise ValueError, '%s: unknown column' % column.name()

        
class _CtrlWithHideableColumns(_BaseCtrlWithColumns):        
    ''' This class supports hiding columns. '''
    
    def showColumn(self, column, show=True):
        ''' showColumn shows or hides the column for column. 
            The column is actually removed or inserted into the control because 
            although TreeListCtrl supports hiding columns, ListCtrl does not. 
            '''
        columnIndex = self._getColumnIndex(column)
        if show and not self.isColumnVisible(column):
            self._insertColumn(columnIndex, column)
        elif not show and self.isColumnVisible(column):
            self._deleteColumn(columnIndex)

    def isColumnVisible(self, column):
        return column in self._visibleColumns()

    def _getColumnIndex(self, column):
        ''' _getColumnIndex returns the actual columnIndex of the column if it 
            is visible, or the position it would have if it were visible. '''
        columnIndexWhenAllColumnsVisible = super(_CtrlWithHideableColumns, self)._getColumnIndex(column)
        for columnIndex, visibleColumn in enumerate(self._visibleColumns()):
            if super(_CtrlWithHideableColumns, self)._getColumnIndex(visibleColumn) >= columnIndexWhenAllColumnsVisible:
                return columnIndex
        return self.GetColumnCount() # Column header not found

    def _visibleColumns(self):
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
        event.Skip()
        columnIndex = event.GetColumn()
        if columnIndex >= self.GetColumnCount():
            return
        column = self._getColumn(columnIndex)
        # Make sure the window this control is in has focus:
        event.GetEventObject().MainWindow.SetFocus()
        if 0 <= event.GetColumn() < self.GetColumnCount():
            column = self._getColumn(event.GetColumn())
            # Use CallAfter to make sure the window this control is in is 
            # activated before we process the column click:
            wx.CallAfter(column.sort, event)
        
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
        columnIndex = self._getColumnIndex(self.__currentSortColumn)
        columnInfo = self.GetColumn(columnIndex)
        if columnInfo.GetImage() == imageIndex:
            pass # The column is already showing the right image, so we're done
        else:
            columnInfo.SetImage(imageIndex)
            self.SetColumn(columnIndex, columnInfo)


class _CtrlWithAutoResizedColumns(autowidth.AutoColumnWidthMixin):
    def DoResize(self, *args, **kwargs):
        super(_CtrlWithAutoResizedColumns, self).DoResize(*args, **kwargs)
        for index, column in enumerate(self._visibleColumns()):
            column.setWidth(self.GetColumnWidth(index))


class CtrlWithColumns(_CtrlWithAutoResizedColumns, _CtrlWithHideableColumns,
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
            

