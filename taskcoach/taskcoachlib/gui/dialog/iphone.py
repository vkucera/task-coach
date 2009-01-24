'''
Task Coach - Your friendly task manager
Copyright (C) 2007 Jerome Laheurte <fraca7@free.fr>

Task Coach is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Task Coach is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import wx
from taskcoachlib.i18n import _

class IPhoneSyncTypeDialog(wx.Dialog):
    def __init__(self, *args, **kwargs):
        super(IPhoneSyncTypeDialog, self).__init__(*args, **kwargs)

        vsz = wx.BoxSizer(wx.VERTICAL)
        vsz.Add(wx.StaticText(self, wx.ID_ANY,
                              _('''An iPhone or iPod Touch device is trying
to synchronize with this task file for
the first time. What kind of synchronization
would you like to use ?''')), 1, wx.EXPAND|wx.ALL, 5)

        hsz = wx.BoxSizer(wx.HORIZONTAL)
        btn = wx.Button(self, wx.ID_ANY, _('Refresh from desktop'))
        hsz.Add(btn, 0, wx.ALL, 3)
        wx.EVT_BUTTON(btn, wx.ID_ANY, self.OnType1)
        btn = wx.Button(self, wx.ID_ANY, _('Refresh from device'))
        hsz.Add(btn, 0, wx.ALL, 3)
        wx.EVT_BUTTON(btn, wx.ID_ANY, self.OnType2)
        btn = wx.Button(self, wx.ID_ANY, _('Cancel'))
        hsz.Add(btn, 0, wx.ALL, 3)
        wx.EVT_BUTTON(btn, wx.ID_ANY, self.OnCancel)
        vsz.Add(hsz, 0, wx.ALIGN_RIGHT)

        self.SetSizer(vsz)
        self.Fit()

        self.value = 3 # cancel

    def OnType1(self, evt):
        self.value = 1
        self.EndModal(wx.ID_OK)

    def OnType2(self, evt):
        self.value = 2
        self.EndModal(wx.ID_OK)

    def OnCancel(self, evt):
        self.EndModal(wx.ID_CANCEL)
