import wx, webbrowser

class TextCtrl(wx.TextCtrl):
    def __init__(self, parent, text='', *args, **kwargs):
        super(TextCtrl, self).__init__(parent, -1,
            style=wx.TE_MULTILINE|wx.TE_RICH|wx.TE_AUTO_URL, *args, **kwargs)
        self.AppendText(text)
        self.Bind(wx.EVT_TEXT_URL, self.onURLClicked)
        self._webbrowser = webbrowser.get()
        
    def onURLClicked(self, event):
        mouseEvent = event.GetMouseEvent()
        if mouseEvent.ButtonDown():
            url = self.GetRange(event.GetURLStart(), event.GetURLEnd())
            self._webbrowser.open(url)