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
            
            
class StaticText(wx.Window):
    def __init__(self, parent, text, helpText=None, *args, **kwargs):
        super(StaticText, self).__init__(parent, -1, *args, **kwargs)
        label = wx.StaticText(self, -1, text)
        self.SetSize(label.GetSize())
        if helpText:
            self.SetToolTipString(helpText)