import wx

class Book(object):
    _size = (16, 16)
    
    def __init__(self, parent, *args, **kwargs):
        super(Book, self).__init__(parent, -1, *args, **kwargs)
        self.Bind(self.pageChangedEvent, self.onPageChanged)
        self.createImageList()
        
    def createImageList(self):
        self.AssignImageList(wx.ImageList(*self._size))
        
    def __getitem__(self, index):
        if index < self.GetPageCount():
            return self.GetPage(index)
        else:
            raise IndexError

    def onPageChanged(self, event):
        event.Skip()    

    def AddPage(self, page, name, bitmap=None):
        if bitmap:
            imageList = self.GetImageList()
            imageList.Add(wx.ArtProvider_GetBitmap(bitmap, wx.ART_MENU, 
                self._size))
            imageId = imageList.GetImageCount()-1
        else:
            imageId = -1
        super(Book, self).AddPage(page, name, imageId=imageId)


class Notebook(Book, wx.Notebook):
    pageChangedEvent = wx.EVT_NOTEBOOK_PAGE_CHANGED
    

class Choicebook(Book, wx.Choicebook):
    pageChangedEvent = wx.EVT_CHOICEBOOK_PAGE_CHANGED


class Listbook(Book, wx.Listbook):
    _size = (22, 22)
    pageChangedEvent = wx.EVT_LISTBOOK_PAGE_CHANGED
