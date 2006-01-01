import wx, webbrowser


class SingleLineTextCtrl(wx.TextCtrl):
    def __init__(self, parent, *args, **kwargs):
        super(SingleLineTextCtrl, self).__init__(parent, -1, *args, **kwargs)


class MultiLineTextCtrl(wx.TextCtrl):
    def __init__(self, parent, text='', *args, **kwargs):
        super(MultiLineTextCtrl, self).__init__(parent, -1,
            style=wx.TE_MULTILINE|wx.TE_RICH|wx.TE_AUTO_URL, *args, **kwargs)
        self.__initializeText(text)
        self.Bind(wx.EVT_TEXT_URL, self.onURLClicked)
        self.__webbrowser = webbrowser.get()
        
    def onURLClicked(self, event):
        mouseEvent = event.GetMouseEvent()
        if mouseEvent.ButtonDown():
            url = self.GetRange(event.GetURLStart(), event.GetURLEnd())
            self.__webbrowser.open(url)
     
    def __initializeText(self, text):
        # Work around a bug in wxPython 2.6.0 and 2.6.1 that causes a
        # wx._core.PyAssertionError: C++ assertion "ucf.GotUpdate()" failed in 
        # ..\..\src\msw\textctrl.cpp(813): EM_STREAMIN didn't send EN_UPDATE?
        # when text is empty.
        if text == '':
            text = ' '
        self.AppendText(text)
        self.SetInsertionPoint(0)

    def GetValue(self, *args, **kwargs):
        value = super(MultiLineTextCtrl, self).GetValue(*args, **kwargs)
        return value.translate({ord(u'\x01'): None})
    
            
class StaticText(wx.Window):
    def __init__(self, parent, text, helpText=None, *args, **kwargs):
        super(StaticText, self).__init__(parent, -1, *args, **kwargs)
        label = wx.StaticText(self, -1, text)
        self.SetSize(label.GetSize())
        if helpText:
            self.SetToolTipString(helpText)