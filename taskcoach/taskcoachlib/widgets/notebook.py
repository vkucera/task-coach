import wx, widgets, draganddrop

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
    def __init__(self, parent, columns, growableColumn=None, *args, **kwargs):
        super(BookPage, self).__init__(parent, style=wx.TAB_TRAVERSAL, *args, **kwargs)
        self._sizer = wx.GridBagSizer(vgap=5, hgap=5)
        self._columns = columns
        self._position = GridCursor(columns)
        if growableColumn is None:
            growableColumn = columns - 1
        if growableColumn > -1:
            self._sizer.AddGrowableCol(growableColumn)
        self._borderWidth = 5
        self.SetSizerAndFit(self._sizer)

    def __defaultFlags(self, controls):
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
        # NB: HitTest is currently only implemented under wxMSW and wxUniv.
        # FIXME: This will probably give errors on Linux and Mac, need to test.
        pageSelectionArea = pageSelectionArea or self
        pageIndex, flags = pageSelectionArea.HitTest((x, y))
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
    
