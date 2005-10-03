import wx
from i18n import _

class ButtonBox(wx.Panel):
    stockItems = {_('OK'): wx.ID_OK, _('Cancel'): wx.ID_CANCEL }

    def __init__(self, parent, *buttons):
        super(ButtonBox, self).__init__(parent, -1)
        self._sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._buttons = {}
        for text, callback in buttons:
            self.createButton(text, callback)        
        self.SetSizerAndFit(self._sizer)

    def createButton(self, text, callback):
        id = self.stockItems.get(text, -1)
        self._buttons[text] = button = wx.Button(self, id, text)
        if id == wx.ID_OK:
            button.SetDefault()
        self.Bind(wx.EVT_BUTTON, callback, button)
        self._sizer.Add(button)
              
    def enable(self, buttonText):
        self._buttons[buttonText].Enable()
        
    def disable(self, buttonText):
        self._buttons[buttonText].Disable()
