import wx, wx.html, widgets, os
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
        self._buttonBox = self.createButtonBox()
        self._verticalSizer.Add(self._buttonBox, 0, wx.ALIGN_CENTER)
        self._panel.SetSizerAndFit(self._verticalSizer)
        self.SetSizerAndFit(self._panelSizer)
        wx.CallAfter(self._panel.SetFocus)

    def createButtonBox(self):
        return widgets.ButtonBox(self._panel, (_('OK'), self.ok), 
                                 (_('Cancel'), self.cancel))

    def fillInterior(self):
        pass
        
    def ok(self, *args, **kwargs):
        self.Close()
        
    def cancel(self, *args, **kwargs):
        self.Close()

    def disableOK(self):
        self._buttonBox.disable(_('OK'))
        
    def enableOK(self):
        self._buttonBox.enable(_('OK'))
          
           
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


class HtmlWindowThatUsesWebBrowserForExternalLinks(wx.html.HtmlWindow):
    def OnLinkClicked(self, linkInfo):
        openedLinkInExternalBrowser = False
        if linkInfo.GetTarget() == '_blank':
            import webbrowser
            try:
                webbrowser.open(linkInfo.GetHref())
                openedLinkInExternalBrowser = True
            except Error:
                pass
        if not openedLinkInExternalBrowser:
            self.base_OnLinkClicked(linkInfo)


class HTMLDialog(Dialog):
    def __init__(self, title, htmlText, *args, **kwargs):
        self._htmlText = htmlText
        super(HTMLDialog, self).__init__(None, title, *args, **kwargs)
        
    def createInterior(self):
        return HtmlWindowThatUsesWebBrowserForExternalLinks(self._panel, 
            -1, size=(550,400))
        
    def fillInterior(self):
        self._interior.AppendToPage(self._htmlText)
        
    def createButtonBox(self):
        return widgets.ButtonBox(self._panel, (_('OK'), self.ok))
    
    def OnLinkClicked(self, linkInfo):
        print linkInfo
        
        
def AttachmentSelector(**callerKeywordArguments):
    kwargs = {'message': _('Add attachment'),
              'default_path' : os.getcwd(), 
              'wildcard' : _('All files (*.*)|*'), 
              'flags': wx.OPEN}
    kwargs.update(callerKeywordArguments)
    return wx.FileSelector(**kwargs)