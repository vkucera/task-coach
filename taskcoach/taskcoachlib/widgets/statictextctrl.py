import wx


class StaticTextCtrl(wx.TextCtrl):
    def __init__(self, parent, render=str, *args, **kwargs):
        kwargs['style'] = wx.TE_READONLY|wx.TE_RICH
        super(StaticTextCtrl, self).__init__(parent, -1, *args, **kwargs)
        self._render = render
        textAttr = wx.TextAttr()
        textAttr.SetTextColour(wx.NamedColour('LIGHT GREY'))
        self.SetDefaultStyle(textAttr)
        
    def SetValue(self, value):
        ''' Need to call AppendText or WriteText to get the right
        colour '''
        self.Clear()
        self.AppendText(self._render(value))
