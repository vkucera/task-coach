import wx, widgets
from i18n import _

class Dialog(wx.Dialog):
    def __init__(self, parent, title, bitmap='edit', *args, **kwargs):
        super(Dialog, self).__init__(parent, -1, title,
            style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        self.SetIcon(wx.ArtProvider_GetIcon(bitmap, wx.ART_FRAME_ICON,
            (16, 16)))
        self._verticalSizer = wx.BoxSizer(wx.VERTICAL)
        self._panel = wx.Panel(self, -1)
        self._panelSizer = wx.GridSizer(1, 1)
        self._panelSizer.Add(self._panel, flag=wx.EXPAND)
        self._interior = self.createInterior()
        self.fillInterior()
        self._verticalSizer.Add(self._interior, 1, flag=wx.EXPAND)
        self._buttonBox = widgets.ButtonBox(self._panel, (_('OK'), self.ok), 
                                      (_('Cancel'), self.cancel))
        self._verticalSizer.Add(self._buttonBox, 0, wx.ALIGN_CENTER)
        self._panel.SetSizerAndFit(self._verticalSizer)
        self.SetSizerAndFit(self._panelSizer)
        wx.CallAfter(self._panel.SetFocus)

    def fillInterior(self):
        pass
        
    def ok(self, *args, **kwargs):
        self.Close()
        
    def cancel(self, *args, **kwargs):
        self.Close()

    def disableOK(self):
        self._buttonBox.disable('OK')
        
    def enableOK(self):
        self._buttonBox.enable('OK')
          
           
class BookDialog(Dialog):    
    def fillInterior(self):
        self.addPages()
            
    def __getitem__(self, index):
        return self._interior[index]
       
    def ok(self, *args, **kwargs):
        for page in self._interior:
            page.ok()
        super(BookDialog, self).ok(*args, **kwargs)

    def addPages(self):
        raise NotImplementedError 
              
        
class NotebookDialog(BookDialog):
    def createInterior(self):
        return widgets.Notebook(self._panel)
        
class ListbookDialog(BookDialog):
    def createInterior(self):
        return widgets.Listbook(self._panel)