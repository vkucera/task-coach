import wx, webbrowser, draganddrop


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


class SingleLineTextCtrlWithEnterButton(wx.Panel):
    def __init__(self, parent, *args, **kwargs):
        ''' SingleLineTextCtrlWithEnterButton provides a text control and a
            together with an 'enter' button. '''
        label = kwargs.pop('label')
        self.__onEnterCallback = kwargs.pop('onEnter')
        spacerWidth = kwargs.pop('spacerWidth', 5)
        super(SingleLineTextCtrlWithEnterButton, self).__init__(parent, -1, *args, **kwargs)
        self.__textCtrl = SingleLineTextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.__textCtrl.Bind(wx.EVT_TEXT, self.onTextCtrlChanged)
        self.__button = wx.Button(self, label=label)
        self.__button.Bind(wx.EVT_BUTTON, self.onEnter)
        dropTarget = draganddrop.TextDropTarget(self.onTextDrop)
        self.__textCtrl.SetDropTarget(dropTarget)
        self.__layoutControls(spacerWidth)
        self.onTextCtrlChanged()
        
    def __layoutControls(self, spacerWidth):
        self.__sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.__sizer.Add(self.__textCtrl, proportion=1, flag=wx.EXPAND)
        self.__sizer.Add((5,0))
        self.__sizer.Add(self.__button)
        self.SetSizerAndFit(self.__sizer)
    
    # forwarders
    
    def isButtonEnabled(self):
        return self.__button.IsEnabled()
    
    def SetValue(self, *args, **kwargs):
        return self.__textCtrl.SetValue(*args, **kwargs)
        
    def GetValue(self, *args, **kwargs):
        return self.__textCtrl.GetValue(*args, **kwargs)
    
    # callbacks
    
    def onTextCtrlChanged(self, *args, **kwargs):
        ''' Called when the contents of the textCtrl is changed. '''
        if self.__textCtrl.GetValue():
            self.__allowEnter()
        else:
            self.__disallowEnter()

    def onEnter(self, *args, **kwargs):
        ''' Called when the user hits enter or clicks the button. '''
        self.__onEnterCallback(self.__textCtrl.GetValue())
        self.__textCtrl.Clear()
    
    def onTextDrop(self, text):
        ''' Called when the user drags text and drops it on the textCtrl. '''
        self.__textCtrl.SetValue(text)
        
    # helper methods
                    
    def __allowEnter(self):
        ''' The textctrl contains text so allow the user to hit enter or click
            the button. '''
        if not self.__button.IsEnabled():
            self.__textCtrl.Bind(wx.EVT_TEXT_ENTER, self.onEnter)
            self.__button.Enable()
        
    def __disallowEnter(self):
        ''' The textctrl contains no text so disallow the user to hit enter
            or click the button. '''
        if self.__button.IsEnabled():
            self.__textCtrl.Unbind(wx.EVT_TEXT_ENTER)
            self.__button.Disable()
            
