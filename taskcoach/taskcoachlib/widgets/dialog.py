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

import wx, wx.html, os
from taskcoachlib.i18n import _
import buttonbox, notebook


class Dialog(wx.Dialog):
    def __init__(self, parent, title, bitmap='edit', 
                 direction=None, *args, **kwargs):
        # On wxGTK, calling Raise() on the dialog causes it to be shown, which
        # is rather undesirable during testing, so provide a way to instruct 
        # the dialog to not call self.Raise():
        raiseDialog = kwargs.pop('raiseDialog', True)  
        super(Dialog, self).__init__(parent, -1, title,
            style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
        self.SetIcon(wx.ArtProvider_GetIcon(bitmap, wx.ART_FRAME_ICON,
            (16, 16)))
        self._verticalSizer = wx.BoxSizer(wx.VERTICAL)
        self._panel = wx.Panel(self)
        self._panelSizer = wx.GridSizer(1, 1)
        self._panelSizer.Add(self._panel, flag=wx.EXPAND)
        self._direction = direction
        self._interior = self.createInterior()
        self.fillInterior()
        self._verticalSizer.Add(self._interior, 1, flag=wx.EXPAND)
        self._buttonBox = self.createButtonBox()
        self._verticalSizer.Add(self._buttonBox, 0, wx.ALIGN_CENTER)
        self._panel.SetSizerAndFit(self._verticalSizer)
        self.SetSizerAndFit(self._panelSizer)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        if raiseDialog:
            wx.CallAfter(self.Raise)
        wx.CallAfter(self._panel.SetFocus)
        
    def createButtonBox(self):
        return buttonbox.ButtonBox(self._panel, (_('OK'), self.ok), 
                                   (_('Cancel'), self.cancel))

    def fillInterior(self):
        pass
        
    def ok(self, event=None):
        if event:
            event.Skip()
        self.Close(True)
        self.Destroy()
        
    def cancel(self, event=None):
        if event:
            event.Skip()
        self.Close(True)
        self.Destroy()
        
    def onClose(self, event):
        event.Skip()
        self.Destroy()
        
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
        return notebook.Notebook(self._panel)

        
class ListbookDialog(BookDialog):
    def createInterior(self):
        return notebook.Listbook(self._panel)


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
            super(HtmlWindowThatUsesWebBrowserForExternalLinks, 
                  self).OnLinkClicked(linkInfo)


class HTMLDialog(Dialog):
    def __init__(self, title, htmlText, *args, **kwargs):
        self._htmlText = htmlText
        super(HTMLDialog, self).__init__(None, title, *args, **kwargs)
        
    def createInterior(self):
        interior = HtmlWindowThatUsesWebBrowserForExternalLinks(self._panel, 
            -1, size=(550,400))
        if self._direction:
            interior.SetLayoutDirection(self._direction)
        return interior
        
    def fillInterior(self):
        self._interior.AppendToPage(self._htmlText)
        
    def createButtonBox(self):
        return buttonbox.ButtonBox(self._panel, (_('OK'), self.ok))
    
    def OnLinkClicked(self, linkInfo):
        pass
        
        
def AttachmentSelector(**callerKeywordArguments):
    kwargs = {'message': _('Add attachment'),
              'default_path' : os.getcwd(), 
              'wildcard' : _('All files (*.*)|*'), 
              'flags': wx.OPEN}
    kwargs.update(callerKeywordArguments)
    return wx.FileSelector(**kwargs)


class SyncConflictDialog(wx.Dialog):
    def __init__(self, msg, parent, *args, **kwargs):
        super(SyncConflictDialog, self).__init__(parent, wx.ID_ANY, *args, **kwargs)

        btnRemote = wx.Button(self, wx.ID_ANY, _('Remote'))
        btnLocal = wx.Button(self, wx.ID_ANY, _('Local'))

        vsz = wx.BoxSizer(wx.VERTICAL)
        vsz.Add(wx.StaticText(self, wx.ID_ANY, msg), 1, wx.EXPAND|wx.ALL, 3)

        hsz = wx.BoxSizer(wx.HORIZONTAL)
        hsz.Add(btnRemote, 1, wx.ALL, 3)
        hsz.Add(btnLocal, 1, wx.ALL, 3)
        vsz.Add(hsz, 0, wx.EXPAND)

        self.SetSizer(vsz)

        wx.EVT_BUTTON(btnRemote, wx.ID_ANY, self.OnRemote)
        wx.EVT_BUTTON(btnLocal, wx.ID_ANY, self.OnLocal)

    def OnRemote(self, evt):
        self.EndModal(wx.ID_OK)

    def OnLocal(self, evt):
        self.EndModal(wx.ID_CANCEL)
