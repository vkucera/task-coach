
import wx
from i18n import _

class DirectoryChooser(wx.Panel):
    def __init__(self, *args, **kwargs):
        super(DirectoryChooser, self).__init__(*args, **kwargs)

        self.chooser = wx.DirPickerCtrl(self, wx.ID_ANY, u'')
        self.checkbx = wx.CheckBox(self, wx.ID_ANY, _('None'))

        sz = wx.BoxSizer(wx.VERTICAL)
        sz.Add(self.chooser, 1, wx.EXPAND)
        sz.Add(self.checkbx, 1)

        self.SetSizer(sz)
        self.Fit()

        wx.EVT_CHECKBOX(self.checkbx, wx.ID_ANY, self.OnCheck)

    def SetPath(self, pth):
        if pth:
            self.checkbx.SetValue(False)
            self.chooser.Enable(True)
            self.chooser.SetPath(pth)
        else:
            self.checkbx.SetValue(True)
            self.chooser.SetPath(u'')
            self.chooser.Enable(False)

    def GetPath(self):
        if not self.checkbx.GetValue():
            return self.chooser.GetPath()
        return u''

    def OnCheck(self, evt):
        self.chooser.Enable(not evt.IsChecked())
        self.chooser.SetPath('/') # Workaround for a wx bug
