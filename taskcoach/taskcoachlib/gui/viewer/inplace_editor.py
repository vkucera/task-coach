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
''' # pylint: disable-msg=W0105

import wx
from taskcoachlib.thirdparty import hypertreelist
from taskcoachlib import widgets
from taskcoachlib.domain import date


class SubjectCtrl(hypertreelist.EditTextCtrl):
    ''' Single line inline control for editing item subjects. '''
    pass


class DescriptionCtrl(hypertreelist.EditTextCtrl):
    ''' Multiline inline text control for editing item descriptions. '''
    def __init__(self, *args, **kwargs):
        kwargs['style'] = kwargs.get('style', 0) | wx.TE_MULTILINE
        super(DescriptionCtrl, self).__init__(*args, **kwargs)


class EscapeKeyMixin(object):
    ''' Mixin class for text(like) controls to properly handle the Escape key. 
        The inheriting class needs to bind to the event handler. For example:
        self._spinCtrl.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown) '''
    def OnKeyDown(self, event):
        keyCode = event.GetKeyCode()
        if keyCode == wx.WXK_ESCAPE:
            self.StopEditing()
        elif keyCode in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER) and not event.ShiftDown():
            # Notify the owner about the changes
            self.AcceptChanges()
            # Even if vetoed, close the control (consistent with MSW)
            wx.CallAfter(self.Finish)
        else:
            event.Skip()
      

class _SpinCtrl(EscapeKeyMixin, hypertreelist.EditCtrl, widgets.SpinCtrl):
    ''' Base spin control class. '''
    def __init__(self, parent, wxId, item, column, owner, value, *args, **kwargs):
        super(_SpinCtrl, self).__init__(parent, wxId, item, column, owner, str(value), *args, **kwargs)
        self._textCtrl.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

        
class PriorityCtrl(_SpinCtrl):
    ''' Spin control for priority. Since priorities can be any negative or
        positive integer we don't need to set an allowed range. '''
    pass

            
class PercentageCtrl(_SpinCtrl):
    ''' Spin control for percentages. '''
    def __init__(self, *args, **kwargs):
        super(PercentageCtrl, self).__init__(min=0, max=100, *args, **kwargs)
        

class Panel(wx.Panel):
    ''' Panel class for inline controls that need to be put into a panel. '''
    def __init__(self, parent, wxId, value, *args, **kwargs): # pylint: disable-msg=W0613
        # Don't pass the value argument to the wx.Panel since it doesn't take 
        # a value argument
        super(Panel, self).__init__(parent, wxId, *args, **kwargs)      
        
    def makeSizer(self, control):  
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(control, flag=wx.EXPAND)
        self.SetSizerAndFit(sizer)


class BudgetCtrl(hypertreelist.EditCtrl, Panel):
    ''' Masked inline text control for editing budgets: 
        <hours>:<minutes>:<seconds>. '''
    def __init__(self, parent, wxId, item, column, owner, value):
        super(BudgetCtrl, self).__init__(parent, wxId, item, column, owner)
        hours, minutes, seconds = value.hoursMinutesSeconds()
        # Can't inherit from TimeDeltaCtrl because we need to override GetValue,
        # so we use composition instead
        self.__timeDeltaCtrl = widgets.masked.TimeDeltaCtrl(self, hours, minutes, seconds)
        self.makeSizer(self.__timeDeltaCtrl)
        
    def GetValue(self):
        return date.parseTimeDelta(self.__timeDeltaCtrl.GetValue())


class AmountCtrl(EscapeKeyMixin, hypertreelist.EditCtrl, Panel):
    ''' Masked inline text control for editing amounts (floats >= 0). '''
    def __init__(self, parent, wxId, item, column, owner, value):
        super(AmountCtrl, self).__init__(parent, wxId, item, column, owner)
        self.__floatCtrl = widgets.masked.AmountCtrl(self, value)
        self.__floatCtrl.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.makeSizer(self.__floatCtrl)
        
    def GetValue(self):
        return self.__floatCtrl.GetValue()
 
    
class DateTimeCtrl(hypertreelist.EditCtrl, Panel):
    ''' Inline date and time picker control. '''
    def __init__(self, parent, wxId, item, column, owner, value):
        super(DateTimeCtrl, self).__init__(parent, wxId, item, column, owner)
        #starthour = settings.getint('view', 'efforthourstart')
        #endhour = settings.getint('view', 'efforthourend')
        #interval = settings.getint('view', 'effortminuteinterval')
        self.__dateTimeCtrl = widgets.DateTimeCtrl(self)
        self.__dateTimeCtrl.SetValue(value)
        self.makeSizer(self.__dateTimeCtrl)
                
    def GetValue(self):
        return self.__dateTimeCtrl.GetValue()
