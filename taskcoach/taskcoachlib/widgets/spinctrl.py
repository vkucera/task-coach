'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2011 Task Coach developers <developers@taskcoach.org>
Copyright (C) 2008 Rob McMullen <rob.mcmullen@gmail.com>
Copyright (C) 2008 Carl Zmola <zmola@acm.org>

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
from taskcoachlib import platform


if platform.isWindows() or platform.isMac():
    # The native SpinCtrl on Windows has no TextCtrl API which means we cannot make
    # the Delete key work (see uicommand.py::Delete). Our own SpinCtrl below doesn't 
    # have this disadvantage.
    
    class SpinCtrl(wx.Panel):
        maxRange = 2147483647 # 2^31
        
        def __init__(self, parent, wxId=wx.ID_ANY, value=0, pos=wx.DefaultPosition, size=wx.DefaultSize, 
                     style=0, name='wx.SpinCtrl', **kwargs):
            super(SpinCtrl, self).__init__(parent, wxId, pos=pos, size=size)
            minValue = kwargs['min'] if 'min' in kwargs else -self.maxRange
            maxValue = kwargs['max'] if 'max' in kwargs else self.maxRange
            value = min(maxValue, max(int(value), minValue))
            self._textCtrl = wx.TextCtrl(self, value=str(value))
            self._spinButton = wx.SpinButton(self, size=(-1, self._textCtrl.GetSize()[1]), 
                                             style=wx.SP_VERTICAL|wx.SP_ARROW_KEYS)
            self._spinButton.SetRange(minValue, maxValue)
            self._spinButton.SetValue(value)
            self._textCtrl.SetMinSize((size[0]-self._spinButton.GetSize()[0], -1))
            sizer = wx.BoxSizer(wx.HORIZONTAL)
            sizer.AddMany([self._textCtrl, self._spinButton])
            self.SetSizerAndFit(sizer)
            self._textCtrl.Bind(wx.EVT_TEXT, self.onText)
            self._spinButton.Bind(wx.EVT_SPIN, self.onSpin)
            
        def onText(self, event):
            try:
                self._spinButton.SetValue(int(self._textCtrl.GetValue()))
            except ValueError:
                self._textCtrl.SetValue(str(self._spinButton.GetValue()))
            event.Skip()
    
        def onSpin(self, event): # pylint: disable-msg=W0613
            self._textCtrl.SetValue(str(self._spinButton.GetValue()))

        def GetValue(self):
            return self._spinButton.GetValue()
        
        def SetValue(self, value):
            self._textCtrl.SetValue(str(value))
            self._spinButton.SetValue(value)
        
        Value = property(GetValue, SetValue)
        
        def GetMax(self):
            return self._spinButton.GetMax()
        
        def GetMin(self):
            return self._spinButton.GetMin()
    
else:
    
    class SpinCtrl(wx.SpinCtrl):
        # Can't use sys.maxint for the range because Python and wxPython disagree 
        # on what the maximum integer is on Suse 10.0 x86_64. Using sys.maxint 
        # will cause an Overflow exception, so we use a constant:
        maxRange = 2147483647
        
        def __init__(self, *args, **kwargs):
            kwargs['style'] = kwargs.get('style', 0) | wx.SP_ARROW_KEYS
            if 'min' not in kwargs:
                kwargs['min'] = -self.maxRange
            if 'max' not in kwargs:
                kwargs['max'] = self.maxRange
            kwargs['value'] = str(kwargs.get('value', 0))
            super(SpinCtrl, self).__init__(*args, **kwargs)
            if '__WXGTK__' != wx.Platform:
                # on wxGtk, entering text is not possible anyway, so no need to deal
                # with it.
                self.Bind(wx.EVT_SPINCTRL, self.onValueChanged)
    
        def onValueChanged(self, event):
            ''' wx.SpinCtrl resets invalid values (e.g. text or an empty string)
                to wx.SpinCtrl.GetMin(). The minimum priority value is a large
                (negative) number by default. It makes more sense to reset the 
                SpinCtrl to 0 in case of invalid input. '''
            if self.GetValue() == -self.maxRange:
                wx.CallAfter(self.SetValue, 0)
            event.Skip()
    
