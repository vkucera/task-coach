import wx

class ButtonBox(wx.Panel):
    def __init__(self, parent, *buttons):
        super(ButtonBox, self).__init__(parent, -1)
        self._sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._buttons = {}
        for text, callback in buttons:
            self.createButton(text, callback)
        self.SetSizerAndFit(self._sizer)

    def createButton(self, text, callback):
        self._buttons[text] = button = wx.Button(self, -1, text)
        self.Bind(wx.EVT_BUTTON, callback, button)
        self._sizer.Add(button)
        
    def enable(self, buttonText):
        self._buttons[buttonText].Enable()
        
    def disable(self, buttonText):
        self._buttons[buttonText].Disable()
