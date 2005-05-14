import wx

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


class Notebook(Book, wx.Notebook):
    pageChangedEvent = wx.EVT_NOTEBOOK_PAGE_CHANGED
    

class Choicebook(Book, wx.Choicebook):
    pageChangedEvent = wx.EVT_CHOICEBOOK_PAGE_CHANGED


class Listbook(Book, wx.Listbook):
    _bitmapSize = (22, 22)
    pageChangedEvent = wx.EVT_LISTBOOK_PAGE_CHANGED
