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

import wx, wx.aui
import draganddrop


class GridCursor:
    ''' Utility class to help when adding controls to a GridBagSizer. '''
    
    def __init__(self, columns):
        self.__columns = columns
        self.__nextPosition = (0, 0)
    
    def __updatePosition(self, colspan):
        ''' Update the position of the cursor, taking colspan into account. '''
        row, column = self.__nextPosition
        if column == self.__columns - colspan:
            row += 1
            column = 0
        else:
            column += colspan
        self.__nextPosition = (row, column)
                    
    def next(self, colspan=1):
        row, column = self.__nextPosition
        self.__updatePosition(colspan)
        return row, column

    def maxRow(self):
        row, column = self.__nextPosition
        if column == 0:
            return max(0, row-1)
        else:
            return row


class BookPage(wx.Panel):
    ''' A page in a notebook. '''
    def __init__(self, parent, columns, growableColumn=None, *args, **kwargs):
        super(BookPage, self).__init__(parent, style=wx.TAB_TRAVERSAL, 
            *args, **kwargs)
        self._sizer = wx.GridBagSizer(vgap=5, hgap=5)
        self._columns = columns
        self._position = GridCursor(columns)
        if growableColumn is None:
            growableColumn = columns - 1
        if growableColumn > -1:
            self._sizer.AddGrowableCol(growableColumn)
        self._borderWidth = 5

    def fit(self):
        self.SetSizerAndFit(self._sizer)

    def __defaultFlags(self, controls):
        ''' Return the default flags for placing a list of controls. '''
        labelInFirstColumn = type(controls[0]) in [type(''), type(u'')]
        flags = []
        for columnIndex in range(len(controls)):
            if columnIndex == 0 and labelInFirstColumn:
                flag = wx.ALL|wx.ALIGN_LEFT
            else:
                flag = wx.ALL|wx.ALIGN_RIGHT|wx.EXPAND
            flags.append(flag)
        return flags

    def __determineFlags(self, controls, flagsPassed):
        ''' Return a merged list of flags by overriding the default
            flags with flags passed by the caller. '''
        flagsPassed = flagsPassed or [None] * len(controls)
        defaultFlags = self.__defaultFlags(controls)
        flags = []
        for flagPassed, defaultFlag in zip(flagsPassed, defaultFlags):
            if flagPassed is None:
                flag = defaultFlag
            else:
                flag = flagPassed
            flags.append(flag)
        return flags
        '''
        # If we drop support for Python 2.4, change above lines to this:
        return [defaultFlag if flagPassed is None else flagPassed 
                for flagPassed, defaultFlag in zip(flagsPassed, defaultFlags)]
        '''
    def __addControl(self, columnIndex, control, flag, lastColumn):
        if type(control) in [type(''), type(u'')]:
            control = wx.StaticText(self, label=control)
        if lastColumn:
            colspan = max(self._columns - columnIndex, 1)
        else:
            colspan = 1
        self._sizer.Add(control, self._position.next(colspan),
            span=(1, colspan), flag=flag, border=self._borderWidth)
            
    def addEntry(self, *controls, **kwargs):
        ''' Add a number of controls to the page. All controls are
            placed on one row, and together they form one entry. E.g. a
            label, a text field and an explanatory label. The default
            flags for placing the controls can be overridden by
            providing a keyword parameter 'flags'. flags should be a
            list of flags (wx.ALIGN_LEFT and the like). The list may
            contain None for controls that should be placed using the default
            flag. If the flags list is shorter than the number of
            controls it is extended with as much 'None's as needed.
            So, addEntry(aLabel, aTextCtrl, flags=[None, wx.ALIGN_LEFT]) 
            will place the label with the default flag and will place the 
            textCtrl left aligned. '''
        controls = [control for control in controls if control is not None]
        flags = self.__determineFlags(controls, kwargs.get('flags', None))
        lastColumnIndex = len(controls) - 1
        for columnIndex, control in enumerate(controls):
            self.__addControl(columnIndex, control, flags[columnIndex], 
                lastColumn=columnIndex==lastColumnIndex)
        if kwargs.get('growable', False):
            self._sizer.AddGrowableRow(self._position.maxRow())

    def ok(self):
        pass


class BoxedBookPage(BookPage):
    def __init__(self, *args, **kwargs):
        super(BoxedBookPage, self).__init__(*args, **kwargs)
        self.__boxSizers = {}

    def addBox(self, label):
        box = wx.StaticBox(self, label=label)
        boxSizer = wx.StaticBoxSizer(box, wx.HORIZONTAL)
        gridBagSizer = wx.GridBagSizer()
        boxSizer.Add(gridBagSizer, flag=wx.EXPAND|wx.ALL)
        self.__boxSizers[label] = gridBagSizer
        self._sizer.Add(boxSizer, self._position.next(self._columns),
                        span=(1, self._columns), flag=wx.EXPAND|wx.ALL)

    def addEntry(self, *args, **kwargs):
        self._sizer = self.__boxSizers[kwargs['box']]
        super(BoxedBookPage, self).addEntry(*args, **kwargs)
        

class Book(object):
    ''' Abstract base class for *book '''
    
    _bitmapSize = (16, 16)
    
    def __init__(self, parent, *args, **kwargs):
        super(Book, self).__init__(parent, -1, *args, **kwargs)
        dropTarget = draganddrop.FileDropTarget(onDragOverCallback=self.onDragOver)
        self.SetDropTarget(dropTarget)
        self.Bind(self.pageChangedEvent, self.onPageChanged)
        self.createImageList()
        
    def createImageList(self):
        self.AssignImageList(wx.ImageList(*self._bitmapSize))
        
    def __getitem__(self, index):
        ''' More pythonic way to get a specific page, also useful for iterating
            over all pages, e.g: for page in notebook: ... '''
        if index < self.GetPageCount():
            return self.GetPage(index)
        else:
            raise IndexError
        
    def onDragOver(self, x, y, defaultResult, pageSelectionArea=None):
        ''' When the user drags something (currently limited to files because
            the DropTarget created in __init__ is a FileDropTarget) over a tab
            raise the appropriate page. '''
        # FIXME: HitTest doesn't seem to work with wx.aui.AuiNotebook
        pageSelectionArea = pageSelectionArea or self
        pageIndex = pageSelectionArea.HitTest((x, y))
        if type(pageIndex) == type((),):
            pageIndex = pageIndex[0]
        if pageIndex != wx.NOT_FOUND:
            self.SetSelection(pageIndex)
        return wx.DragNone
    
    def onPageChanged(self, event):
        ''' Can be overridden in a subclass to do something useful '''
        event.Skip()    

    def AddPage(self, page, name, bitmap=None):
        if bitmap:
            imageList = self.GetImageList()
            imageList.Add(wx.ArtProvider_GetBitmap(bitmap, wx.ART_MENU, 
                self._bitmapSize))
            imageId = imageList.GetImageCount()-1
        else:
            imageId = -1
        super(Book, self).AddPage(page, name, imageId=imageId)

    def ok(self):
        for page in self:
            page.ok()
            

class Notebook(Book, wx.Notebook):
    pageChangedEvent = wx.EVT_NOTEBOOK_PAGE_CHANGED
    

class Choicebook(Book, wx.Choicebook):
    pageChangedEvent = wx.EVT_CHOICEBOOK_PAGE_CHANGED
    
    def createImageList(self):
        pass # Choicebooks have no icons

    def onDragOver(self, *args, **kwargs):
        ''' onDragOver cannot work for Choicebooks because the choice control
            widget that is used to switch between pages has no HitTest 
            method. '''
        return wx.DragNone


class Listbook(Book, wx.Listbook):
    _bitmapSize = (22, 22)
    pageChangedEvent = wx.EVT_LISTBOOK_PAGE_CHANGED

    def onDragOver(self, x, y, defaultResult):
        ''' onDragOver will only work for Listbooks if we query the list 
            control (instead of the Listbook itself) with HitTest, so we pass
            the result of self.GetListView() as pageSelectionArea to 
            super.onDragOver. '''
        return super(Listbook, self).onDragOver(x, y, defaultResult, 
            pageSelectionArea=self.GetListView())
    
    
class AUINotebook(Book, wx.aui.AuiNotebook):
    pageChangedEvent = wx.aui.EVT_AUINOTEBOOK_PAGE_CHANGED
    
    def __init__(self, *args, **kwargs):
        kwargs['style'] = kwargs.get('style', wx.aui.AUI_NB_DEFAULT_STYLE) & ~wx.aui.AUI_NB_CLOSE_ON_ACTIVE_TAB
        super(AUINotebook, self).__init__(*args, **kwargs)
        self.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.onClosePage)
        self.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CHANGING, self.onPageChanging)
        
    def onPageChanging(self, event):
        # On Windows, the AuiNotebook changes its pages when other applications
        # are minimized. Prevent this by vetoing PAGE_CHANGING events when our
        # top level window is not active:
        if '__WXMSW__' in wx.PlatformInfo and \
                not self.GetTopLevelParent().IsActive():
            event.Veto()
        else:
            event.Skip()
                    
    def onClosePage(self, event):
        if self.GetPageCount() <= 2:
            # Prevent last tab from being closed
            self.ToggleWindowStyle(wx.aui.AUI_NB_CLOSE_ON_ACTIVE_TAB)
            
    def createImageList(self):
        pass
    
    def AddPage(self, page, name, bitmap=''):
        bitmap = wx.ArtProvider_GetBitmap(bitmap, wx.ART_MENU, self._bitmapSize)
        wx.aui.AuiNotebook.AddPage(self, page, name, bitmap=bitmap)
        if self.GetPageCount() > 1:
            self.SetWindowStyle(self.GetWindowStyleFlag() | wx.aui.AUI_NB_CLOSE_ON_ACTIVE_TAB)

    def AdvanceSelection(self, forward=True):
        ''' This method is part of the Notebook API but missing from the 
            AuiNotebook API. '''
        if self.PageCount <= 1:
            return # Not enough viewers to advance selection
        if forward:
            if 0 <= self.Selection < self.PageCount - 1:
                self.Selection += 1
            else:
                self.Selection = 0
        else:
            if 1 <= self.Selection < self.PageCount:
                self.Selection -= 1
            else:
                self.Selection = self.PageCount - 1
