'''
Task Coach - Your friendly task manager
Copyright (C) 2009 Jerome Laheurte <fraca7@free.fr>

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
import wx.lib.hyperlink as hl

from taskcoachlib.gui.threads import DeferredCallMixin, synchronized, synchronizednb
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
        self.CentreOnScreen()
        self.RequestUserAttention()

        self.value = 3 # cancel

    def OnType1(self, evt):
        self.value = 1
        self.EndModal(wx.ID_OK)

    def OnType2(self, evt):
        self.value = 2
        self.EndModal(wx.ID_OK)

    def OnCancel(self, evt):
        self.EndModal(wx.ID_CANCEL)


class IPhoneSyncDialog(DeferredCallMixin, wx.Dialog):
    def __init__(self, deviceName, *args, **kwargs):
        super(IPhoneSyncDialog, self).__init__(*args, **kwargs)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(self, wx.ID_ANY, _('Synchronizing with %s...') % deviceName),
                  0, wx.ALL, 3)

        self.gauge = wx.Gauge(self, wx.ID_ANY)
        self.gauge.SetRange(100)
        sizer.Add(self.gauge, 0, wx.EXPAND|wx.ALL, 3)

        self.SetSizer(sizer)
        self.Fit()
        self.CentreOnScreen()

    @synchronized
    def SetProgress(self, value, total):
        self.gauge.SetValue(int(100 * value / total))

    @synchronizednb
    def Started(self):
        self.ShowModal()

    @synchronized
    def Finished(self):
        self.EndModal(wx.ID_OK)


class IPhoneBonjourDialog(wx.Dialog):
    def __init__(self, *args, **kwargs):
        super(IPhoneBonjourDialog, self).__init__(*args, **kwargs)

        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(wx.StaticText(self, wx.ID_ANY,
                                 _('You have enabled the iPhone synchronization feature, which\n'
                                   'needs Bonjour. Bonjour does not seem to be installed on\n'
                                   'your system.')), 0, wx.ALL, 3)
        if '__WXMSW__' in wx.PlatformInfo:
            vsizer.Add(wx.StaticText(self, wx.ID_ANY,
                                     _('Please download and install Bonjour for Windows from\n')), 0, wx.ALL, 3)
            vsizer.Add(hl.HyperLinkCtrl(self, wx.ID_ANY,
                                        _('Apple\'s web site'),
                                        URL='http://support.apple.com/downloads/Bonjour_for_Windows'), 0, wx.ALL, 3)
        else:
            # MacOS does support Bonjour in all cases, so we're probably running Linux.
            vsizer.Add(wx.StaticText(self, wx.ID_ANY,
                                     _('Bonjour support for Linux is generally provided by\n'
                                       'Avahi.')), 0, wx.ALL, 3)
            vsizer.Add(hl.HyperLinkCtrl(self, wx.ID_ANY,
                                        _('More details on pybonjour web site'),
                                        URL='http://o2s.csail.mit.edu/o2s-wiki/pybonjour'), 0, wx.ALL, 3)

        btnOK = wx.Button(self, wx.ID_ANY, _('OK'))
        vsizer.Add(btnOK, 0, wx.ALIGN_CENTRE|wx.ALL, 3)

        self.SetSizer(vsizer)
        self.Fit()
        self.CentreOnScreen()

        wx.EVT_BUTTON(btnOK, wx.ID_ANY, self.OnDismiss)

    def OnDismiss(self, evt):
        self.EndModal(wx.ID_OK)
