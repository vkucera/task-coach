import wx, widgets
from i18n import _

class Dialog(wx.Dialog):
    def __init__(self, parent, title, bitmap='edit', *args, **kwargs):
        super(Dialog, self).__init__(parent, -1, title,
            style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        self.SetIcon(wx.ArtProvider_GetIcon(bitmap, wx.ART_FRAME_ICON,
            (16, 16)))

           
class TabbedDialog(Dialog):
    def __init__(self, *args, **kwargs):
        super(TabbedDialog, self).__init__(*args, **kwargs)
        self._panel = wx.Panel(self, -1)
        self._panelSizer = wx.GridSizer(1, 1)
        self._panelSizer.Add(self._panel, flag=wx.EXPAND)
        self._verticalSizer = wx.BoxSizer(wx.VERTICAL)
        self._notebook = widgets.Notebook(self._panel)
        self._verticalSizer.Add(self._notebook, 1, flag=wx.EXPAND)
        self.addPages()
        self._buttonBox = widgets.ButtonBox(self._panel, (_('OK'), self.ok), 
                                      (_('Cancel'), self.cancel))
        self._verticalSizer.Add(self._buttonBox, 0, wx.ALIGN_CENTER)
        self._panel.SetSizerAndFit(self._verticalSizer)
        self.SetSizerAndFit(self._panelSizer)
        wx.CallAfter(self._panel.SetFocus)

    def __getitem__(self, index):
        return self._notebook[index]

    def ok(self, *args):
        for page in self._notebook:
            page.ok()
        self.Close()

    def cancel(self, *args):
        self.Close()
    
    def addPages(self):
        raise NotImplementedError 
        
    def disableOK(self):
        self._buttonBox.disable('OK')
        
    def enableOK(self):
        self._buttonBox.enable('OK')