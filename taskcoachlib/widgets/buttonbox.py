import wx
from i18n import _

class ButtonBox(wx.Panel):
    stockItems = {_('OK'): wx.ID_OK, _('Cancel'): wx.ID_CANCEL }

    def __init__(self, parent, *buttons, **kwargs):
        super(ButtonBox, self).__init__(parent, -1)
        self.__borderWidth = kwargs.pop('borderWidth', 5)
        self.__sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.__buttons = {}
        for text, callback in buttons:
            self.createButton(text, callback)        
        self.SetSizerAndFit(self.__sizer)
        
    def __getitem__(self, buttonLabel):
        return self.__buttons[buttonLabel]

    def createButton(self, text, callback):
        id = self.stockItems.get(text, -1)
        self.__buttons[text] = button = wx.Button(self, id, text)
        if id == wx.ID_OK:
            button.SetDefault()
        button.Bind(wx.EVT_BUTTON, callback)
        self.__sizer.Add(button, border=self.__borderWidth, flag=wx.ALL)
        
    def setDefault(self, buttonText):
        self.__buttons[buttonText].SetDefault()
              
    def enable(self, buttonText):
        self.__buttons[buttonText].Enable()
        
    def disable(self, buttonText):
        self.__buttons[buttonText].Disable()
