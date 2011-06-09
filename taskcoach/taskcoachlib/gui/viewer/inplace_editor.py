'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2011 Task Coach developers <developers@taskcoach.org>

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

'''
In place editors for viewers.
'''

import wx
from taskcoachlib.thirdparty import hypertreelist
from taskcoachlib import widgets
from taskcoachlib.domain import date


class SubjectCtrl(hypertreelist.EditTextCtrl):
    pass


class DescriptionCtrl(hypertreelist.EditTextCtrl):
    def __init__(self, *args, **kwargs):
        kwargs['style'] = kwargs.get('style', 0) | wx.TE_MULTILINE
        super(DescriptionCtrl, self).__init__(*args, **kwargs)
        
        
class PriorityCtrl(hypertreelist.EditCtrl, widgets.SpinCtrl):
    def __init__(self, parent, id, item, column, owner, value):
        super(PriorityCtrl, self).__init__(parent, id, item, column, owner, str(value))
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        
    def OnKeyDown(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.StopEditing()
        else:
            event.Skip()


class Panel(wx.Panel):
    def __init__(self, parent, id, value, *args, **kwargs):
        # Don't pass the value argument to the wx.Panel since it doesn't take 
        # a value argument
        super(Panel, self).__init__(parent, id, *args, **kwargs)        


class BudgetCtrl(hypertreelist.EditCtrl, Panel):
    def __init__(self, parent, id, item, column, owner, value):
        super(BudgetCtrl, self).__init__(parent, id, item, column, owner)
        hours, minutes, seconds = value.hoursMinutesSeconds()
        # Can't inherit from TimeDeltaCtrl because we need to override GetValue,
        # so we use composition instead
        self.__timeDeltaCtrl = widgets.masked.TimeDeltaCtrl(self, hours, minutes, seconds)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.__timeDeltaCtrl, flag=wx.EXPAND)
        self.SetSizerAndFit(sizer)
        
    def GetValue(self):
        return date.parseTimeDelta(self.__timeDeltaCtrl.GetValue())
    
