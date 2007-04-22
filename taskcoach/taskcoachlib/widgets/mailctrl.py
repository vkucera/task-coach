
import wx
from i18n import _
import draganddrop

class MailCtrl(wx.StaticBitmap):
    def __init__(self, parent, *args, **kwargs):
        self.callback = kwargs.pop('callback')
        bmp = wx.ArtProvider_GetBitmap('email', wx.ART_TOOLBAR, (22, 22))
        wx.StaticBitmap.__init__(self, parent, wx.ID_ANY, bmp, *args, **kwargs)

        self.target = draganddrop.MailDropTarget(self.callback)
        self.SetDropTarget(self.target)
