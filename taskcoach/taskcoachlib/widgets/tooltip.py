
import wx


#==============================================================================
#

class ToolTipMixin(object):
    """Subclass this and override OnBeforeShowToolTip to provide
    dynamic tooltip over a control."""

    def __init__(self, *args, **kwargs):
        super(ToolTipMixin, self).__init__(*args, **kwargs)

        self.__timer = wx.Timer(self, wx.NewId())

        self.__tip = None
        self.__position = (0, 0)
        self.__text = None

        wx.EVT_MOTION(self, self.__OnMotion)
        wx.EVT_LEAVE_WINDOW(self, self.__OnLeave)
        wx.EVT_TIMER(self, self.__timer.GetId(), self.__OnTimer)

    def ShowTip(self, x, y):
        self.__tip.MoveXY(x, y)
        if '__WXMSW__' not in wx.PlatformInfo:
            self.__tip.Show()

    def HideTip(self):
        if '__WXMSW__' in wx.PlatformInfo:
            self.__tip.MoveXY(32767, 32767)
        else:
            self.__tip.Hide()

    def OnBeforeShowToolTip(self, x, y):
        """Should return a wx.Frame instance that will be displayed as
        the tooltip, or None."""
        raise NotImplementedError

    def __OnMotion(self, evt):
        x, y = evt.GetPosition()

        self.__timer.Stop()

        if self.__tip is not None:
            self.HideTip()
            self.__tip = None

        ret = self.OnBeforeShowToolTip(x, y)

        if ret is not None:
            self.__tip = ret
            self.__position = (x + 3, y + 10)
            self.__timer.Start(200, True)

        evt.Skip()

    def __OnLeave(self, evt):
        self.__timer.Stop()

        if self.__tip is not None:
            self.HideTip()
            self.__tip = None

        evt.Skip()

    def __OnTimer(self, evt):
        self.ShowTip(*self.ClientToScreenXY(*self.__position))


#==============================================================================
#

class SimpleToolTip(wx.Frame):
    def __init__(self, parent):
        super(SimpleToolTip, self).__init__(parent, wx.ID_ANY, 'Tooltip',
                                            style=wx.FRAME_NO_TASKBAR| \
                                            wx.FRAME_FLOAT_ON_PARENT| \
                                            wx.NO_BORDER)

        if '__WXMSW__' in wx.PlatformInfo:
            self.MoveXY(32767, 32767)
            self.Show()

        wx.EVT_MOTION(self, self.OnMotion)
        wx.EVT_PAINT(self, self.OnPaint)

    def OnMotion(self, evt):
        self.Hide()

    def SetText(self, text):
        width = 0
        height = 0
        self.lines = []

        dc = wx.ClientDC(self)
        dc.SetFont(wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT))

        for line in text.split('\n'):
            s = line.rstrip('\r')
            self.lines.append(s)
            w, h = dc.GetTextExtent(s)
            width = max(width, w)
            height += h + 1

        width += 6
        height += 6

        self.SetSize(wx.Size(width, height))

    def OnPaint(self, evt):
        dc = wx.PaintDC(self)
        dc.BeginDrawing()
        try:
            dc.SetFont(wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT))
            w, h = self.GetClientSizeTuple()

            brush = wx.Brush(wx.Colour(0xff, 0xff, 0xe1))
            dc.SetBrush(brush)
            dc.SetPen(wx.BLACK_PEN)
            dc.DrawRectangle(0, 0, w, h)

            x = 3
            y = 3

            for line in self.lines:
                dc.DrawText(line, x, y)
                w, h = dc.GetTextExtent(line)
                y += h + 1
        finally:
            dc.EndDrawing()
