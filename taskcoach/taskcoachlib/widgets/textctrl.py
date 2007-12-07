import wx, webbrowser, draganddrop, i18n


UNICODE_CONTROL_CHARACTERS_TO_WEED = {}
for ordinal in range(0x20):
    if chr(ordinal) not in '\t\r\n':
        UNICODE_CONTROL_CHARACTERS_TO_WEED[ordinal] = None


class BaseTextCtrl(wx.TextCtrl):
    def __init__(self, parent, *args, **kwargs):
        super(BaseTextCtrl, self).__init__(parent, -1, *args, **kwargs)
        self.__data = None

    def GetValue(self, *args, **kwargs):
        value = super(BaseTextCtrl, self).GetValue(*args, **kwargs)
        # Don't allow unicode control characters:
        return value.translate(UNICODE_CONTROL_CHARACTERS_TO_WEED)

    def SetData(self, data):
        self.__data = data

    def GetData(self):
        return self.__data


class SingleLineTextCtrl(BaseTextCtrl):
    pass


class MultiLineTextCtrl(BaseTextCtrl):
    CheckSpelling = True
    
    def __init__(self, parent, text='', *args, **kwargs):
        if i18n.Translator().currentLanguageIsRightToLeft():
            style = wx.TE_MULTILINE
        else:
            style = wx.TE_MULTILINE|wx.TE_RICH|wx.TE_AUTO_URL
        super(MultiLineTextCtrl, self).__init__(parent, style=style, 
                                                *args, **kwargs)#
        self.__initializeText(text)
        self.Bind(wx.EVT_TEXT_URL, self.onURLClicked)
        try:
            self.__webbrowser = webbrowser.get()
        except:
            self.__webbrowser = None
        self.MacCheckSpelling(self.CheckSpelling)
        
    def onURLClicked(self, event):
        mouseEvent = event.GetMouseEvent()
        if mouseEvent.ButtonDown() and self.__webbrowser:
            url = self.GetRange(event.GetURLStart(), event.GetURLEnd())
            self.__webbrowser.open(url)
     
    def __initializeText(self, text):
        self.AppendText(text)
        self.SetInsertionPoint(0)


class StaticTextWithToolTip(wx.StaticText):
    def __init__(self, *args, **kwargs):
        super(StaticTextWithToolTip, self).__init__(*args, **kwargs)
        label = kwargs['label']
        self.SetToolTip(wx.ToolTip(label))


class SingleLineTextCtrlWithEnterButton(wx.Panel):
    def __init__(self, parent, *args, **kwargs):
        ''' SingleLineTextCtrlWithEnterButton provides a text control 
            together with an 'enter' button. '''
        label = kwargs.pop('label')
        self.__onEnterCallback = kwargs.pop('onEnter')
        spacerWidth = kwargs.pop('spacerWidth', 5)
        super(SingleLineTextCtrlWithEnterButton, self).__init__(parent, 
            *args, **kwargs)
        self.__createControls(label)
        self.__bindEventHandlers()
        self.__layoutControls(spacerWidth)
        self.onTextCtrlChanged()

    def __createControls(self, label):
        self.__textCtrl = SingleLineTextCtrl(self, style=wx.TE_PROCESS_ENTER)
        self.__button = wx.Button(self, label=label)

    def __bindEventHandlers(self):
        self.__textCtrl.Bind(wx.EVT_TEXT, self.onTextCtrlChanged)
        self.__button.Bind(wx.EVT_BUTTON, self.onEnter)
        dropTarget = draganddrop.TextDropTarget(self.onTextDrop)
        self.__textCtrl.SetDropTarget(dropTarget)

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

    def SetData(self, *args, **kwargs):
        return self.__textCtrl.SetData(*args, **kwargs)

    def GetData(self, *args, **kwargs):
        return self.__textCtrl.GetData(*args, **kwargs)

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
        # TextCtrl.Clear() does not fire an EVT_TEXT event on all platforms
        # so we call onTextCtrlChanged ourselves to be sure that the button 
        # is correctly enabled or disabled.
        self.onTextCtrlChanged()
    
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

