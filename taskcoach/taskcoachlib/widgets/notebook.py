import wx, widgets

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
        super(BookPage, self).__init__(parent, -1, *args, **kwargs)
        self._sizer = wx.GridBagSizer(vgap=5, hgap=5)
        self._columns = columns
        self._position = GridCursor(columns)
        if growableColumn is None:
            growableColumn = columns - 1
        self._sizer.AddGrowableCol(growableColumn)
        self._borderWidth = 5
        self.SetSizerAndFit(self._sizer)
        
    def addEntry(self, labelText, *controls, **kwargs):
        controls = [control for control in controls if control is not None]
        if labelText is not None:
            if labelText: labelText += ':'
            label = wx.StaticText(self, -1, labelText)
            self._sizer.Add(label, self._position.next(),
                flag=wx.ALL|wx.ALIGN_RIGHT, border=self._borderWidth)
        for control in controls:
            if type(control) in [type(''), type(u'')]:
                control = wx.StaticText(self, -1, control)
            colspan = max(self._columns - len(controls), 1)
            self._sizer.Add(control, self._position.next(colspan), span=(1, colspan),
                flag=wx.ALIGN_LEFT|wx.EXPAND|wx.ALL, border=self._borderWidth)
        if 'growable' in kwargs and kwargs['growable']:
            self._sizer.AddGrowableRow(self._position.maxRow())

    def ok(self):
        pass
        

class Book(object):
    ''' Abstract base class for *book '''
    
    _bitmapSize = (16, 16)
    
    def __init__(self, parent, *args, **kwargs):
        super(Book, self).__init__(parent, -1, *args, **kwargs)
        self.Bind(self.pageChangedEvent, self.onPageChanged)
        self.createImageList()
        
    def createImageList(self):
        self.AssignImageList(wx.ImageList(*self._bitmapSize))
        
    def __getitem__(self, index):
        ''' More pythonic way to get a specific page, also useful if you 
            want to iterate over all pages, e.g: for page in notebook: ... '''
        if index < self.GetPageCount():
            return self.GetPage(index)
        else:
            raise IndexError

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


class Listbook(Book, wx.Listbook):
    _bitmapSize = (22, 22)
    pageChangedEvent = wx.EVT_LISTBOOK_PAGE_CHANGED
