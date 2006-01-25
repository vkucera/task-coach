import wx, webbrowser

UNICODE_CONTROL_CHARACTERS_TO_WEED = {}
for ordinal in range(0x20):
    if chr(ordinal) not in '\t\r\n':
        UNICODE_CONTROL_CHARACTERS_TO_WEED[ordinal] = None


class BaseTextCtrl(wx.TextCtrl):
    def __init__(self, parent, *args, **kwargs):
        super(BaseTextCtrl, self).__init__(parent, -1, *args, **kwargs)

    def GetValue(self, *args, **kwargs):
        value = super(BaseTextCtrl, self).GetValue(*args, **kwargs)
        # don't allow unicode control characters:
        return value.translate(UNICODE_CONTROL_CHARACTERS_TO_WEED)


class SingleLineTextCtrl(BaseTextCtrl):
    pass


class MultiLineTextCtrl(BaseTextCtrl):
    def __init__(self, parent, text='', *args, **kwargs):
        super(MultiLineTextCtrl, self).__init__(parent,
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
        # when text is empty. Also see GetValue() below.
        if text == '':
            text = ' '
        self.AppendText(text)
        self.SetInsertionPoint(0)

    def GetValue(self, *args, **kwargs):
        value = super(MultiLineTextCtrl, self).GetValue(*args, **kwargs)
        if value == ' ':
            value = ''
        return value
    
            
class StaticText(wx.Window):
    def __init__(self, parent, text, helpText=None, *args, **kwargs):
        super(StaticText, self).__init__(parent, -1, *args, **kwargs)
        label = wx.StaticText(self, -1, text)
        self.SetSize(label.GetSize())
        if helpText:
            self.SetToolTipString(helpText)