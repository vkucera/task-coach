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


class EditTextCtrl(hypertreelist.EditTextCtrl):
    pass


class MultilineEditTextCtrl(EditTextCtrl):
    def __init__(self, *args, **kwargs):
        kwargs['style'] = kwargs.get('style', 0) | wx.TE_MULTILINE
        super(MultilineEditTextCtrl, self).__init__(*args, **kwargs)
        
        
class EditSpinCtrl(hypertreelist.EditCtrl, widgets.SpinCtrl):
    def __init__(self, *args, **kwargs):
        super(EditSpinCtrl, self).__init__(*args, **kwargs)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        
    def OnKeyDown(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.StopEditing()
        else:
            event.Skip()
