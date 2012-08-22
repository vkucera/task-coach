'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2012 Task Coach developers <developers@taskcoach.org>
Copyright (C) 2008 Rob McMullen <rob.mcmullen@gmail.com>

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

from taskcoachlib import operating_system, render
from taskcoachlib.thirdparty.dateutil import parser as dparser
from taskcoachlib.domain import date
import wx


class _BetterDatePickerCtrl(wx.DatePickerCtrl):
    ''' The default DatePickerControl on Mac OS X and Linux doesn't disable
        the calendar drop down button. This class fixes that and keyboard
        navigation. '''

    def __init__(self, *args, **kwargs):
        super(_BetterDatePickerCtrl, self).__init__(*args, **kwargs)
        if operating_system.isGTK():
            comboCtrl = self.GetChildren()[0]
            comboCtrl.Bind(wx.EVT_KEY_DOWN, self.onKey)

    def onKey(self, event):
        keyCode = event.GetKeyCode()
        if keyCode == wx.WXK_RETURN:
            # Move to the next field so that the contents of the text control,
            # that might be edited by the user, are updated by the datepicker:
            self.GetParent().Navigate() 
            # Next, click the default button of the dialog:
            button = self.getTopLevelWindow().GetDefaultItem()  # pylint: disable=E1103
            click = wx.CommandEvent()
            click.SetEventType(wx.EVT_BUTTON.typeId)
            wx.PostEvent(button, click)
        elif keyCode == wx.WXK_TAB:
            self.GetParent().Navigate(not event.ShiftDown())
        else:
            event.Skip()

    def getTopLevelWindow(self):
        window = self
        while not window.IsTopLevel():
            window = window.GetParent()
        return window

    def Disable(self):  # pylint: disable=W0221
        super(_BetterDatePickerCtrl, self).Disable()
        for child in self.Children:
            child.Disable()
            
    def Enable(self, enable=True):  # pylint: disable=W0221
        super(_BetterDatePickerCtrl, self).Enable(enable)
        for child in self.Children:
            child.Enable(enable)
            

class _DatePickerCtrlThatFixesAllowNoneStyle(wx.Panel):
    def __init__(self, parent, *args, **kwargs):
        self.__args = args
        self.__kwargs = kwargs
        super(_DatePickerCtrlThatFixesAllowNoneStyle, self).__init__(parent)
        self._createControls()
        self._layout()
        if operating_system.isGTK():
            # Many EVT_CHILD_FOCUS are sent on wxGTK, see 
            # http://trac.wxwidgets.org/ticket/11305. Ignore these events
            self.Bind(wx.EVT_CHILD_FOCUS, lambda event: None)
            
    def _createControls(self):
        # pylint: disable=W0201
        self.__check = wx.CheckBox(self)
        self.__check.Bind(wx.EVT_CHECKBOX, self.onCheck)
        self.__datePicker = _BetterDatePickerCtrl(self, *self.__args, 
                                                  **self.__kwargs)
        self.__datePicker.Disable()

    def _layout(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        for control in (self.__check, self.__datePicker):
            sizer.Add(control, flag=wx.ALIGN_CENTER_VERTICAL)
        self.SetSizerAndFit(sizer)

    def onCheck(self, event):
        self.__datePicker.Enable(event.IsChecked())
        event.Skip()

    def GetValue(self):
        dp = self.__datePicker
        return dp.GetValue() if dp.IsEnabled() else wx.DateTime()

    def SetValue(self, value):
        if value.IsValid():
            self.__datePicker.Enable()
            self.__check.SetValue(True)
            self.__datePicker.SetValue(value)
        else:
            self.__datePicker.Disable()
            self.__check.SetValue(False)

    def IsEnabled(self):  # pylint: disable=W0221
        return self.__datePicker.IsEnabled()

    def __getattr__(self, attr):
        return getattr(self.__datePicker, attr)


def styleDP_ALLOWNONEIsBroken():
    # DP_ALLOWNONE is not supported on Mac OS and Linux
    return not operating_system.isWindows()


def DatePickerCtrl(*args, **kwargs):
    ''' Factory function that returns _DatePickerCtrlThatFixesAllowNoneStyle 
        when necessary and wx.DatePickerCtrl otherwise. '''

    def styleIncludesDP_ALLOWNONE(style):
        return (style & wx.DP_ALLOWNONE) == wx.DP_ALLOWNONE 

    style = kwargs.get('style', wx.DP_DEFAULT)
    if styleIncludesDP_ALLOWNONE(style) and styleDP_ALLOWNONEIsBroken():
        kwargs['style'] = kwargs['style'] & ~wx.DP_ALLOWNONE
        datePickerCtrlClass = _DatePickerCtrlThatFixesAllowNoneStyle
    else:
        datePickerCtrlClass = wx.DatePickerCtrl
    return datePickerCtrlClass(*args, **kwargs)


def date2wxDateTime(value):
    wxDateTime = wx.DateTime()
    try:  # prepare for a value that is not a Python datetime instance
        if value < date.Date():
            wxDateTime.Set(value.day, value.month - 1, value.year)
    except (TypeError, AttributeError):
        pass
    return wxDateTime
    

def wxDateTime2Date(wxDateTime):
    if wxDateTime.IsValid():
        return date.Date(wxDateTime.GetYear(), wxDateTime.GetMonth() + 1,
            wxDateTime.GetDay())
    else:
        return date.Date()


class DateTimeCtrl(wx.Panel):
    def __init__(self, parent, callback=None, noneAllowed=True,
                 starthour=8, endhour=18, interval=15, showSeconds=False,
                 *args, **kwargs):
        self.__noneAllowed = noneAllowed
        self._starthour = starthour
        self._endhour = endhour
        self._interval = interval
        self.__showSeconds = showSeconds
        self._callback = callback or self.__nullCallback
        super(DateTimeCtrl, self).__init__(parent, *args, **kwargs)
        self._createControls()
        self._layout()
        if operating_system.isGTK():
            # Many EVT_CHILD_FOCUS are sent on wxGTK, see 
            # http://trac.wxwidgets.org/ticket/11305. Ignore these events
            self.Bind(wx.EVT_CHILD_FOCUS, lambda event: None)

    def _createControls(self): 
        # pylint: disable=W0201
        self._dateCtrl = DatePickerCtrl(self, **self._datePickerOptions())  # pylint: disable=W0142
        self._dateCtrl.Bind(wx.EVT_DATE_CHANGED, self._dateCtrlCallback)
        self._dateCtrl.Bind(wx.EVT_CHECKBOX, self.onEnableDatePicker)
        self._timeCtrl = wx.ComboBox(self, choices=self._timeChoices(),
                                     size=self._timeSize())
        self._timeCtrl.Bind(wx.EVT_TEXT, self._timeCtrlCallback)
        self._timeCtrl.Bind(wx.EVT_COMBOBOX, self._timeCtrlCallback)
    
    def _datePickerOptions(self):
        options = dict(style=wx.DP_DROPDOWN, dt=wx.DateTime_Today())
        if self.__noneAllowed:
            options['style'] |= wx.DP_ALLOWNONE
        if operating_system.isWindows():
            options['size'] = (self.__adjustForDPI(100), -1) 
        elif operating_system.isGTK():
            options['size'] = (115, -1)
        return options
    
    def _timeChoices(self):
        choices = []
        for hour in range(self._starthour, self._endhour):
            for minute in range(0, 60, self._interval):
                choices.append(self.__formatTime(date.Time(hour, minute)))
        if self._endhour < 24:
            choices.append(self.__formatTime(date.Time(self._endhour, 0)))
        return choices
    
    def _timeSize(self):
        if operating_system.isWindows():
            return (self.__adjustForDPI(100 if self.__showSeconds else 80), -1)
        elif operating_system.isGTK():
            return (125 if self.__showSeconds else 105, -1)
        else:
            return (125 if self.__showSeconds else 100, 
                    self._dateCtrl.GetSize()[1])
    
    @staticmethod
    def __adjustForDPI(size):
        return round(size * wx.ScreenDC().GetPPI()[0] / 96.)

    def __formatTime(self, time):
        return render.time(time, self.__showSeconds)
                    
    def _layout(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        for control in (self._dateCtrl, self._timeCtrl):
            sizer.Add(control, flag=wx.ALIGN_CENTER_VERTICAL)
        self.SetSizerAndFit(sizer)        
        
    def __nullCallback(self, *args, **kwargs):
        pass
        
    def onEnableDatePicker(self, event):
        self._timeCtrl.Enable(event.IsChecked())
        self._callback(event)

    def _timeCtrlCallback(self, *args, **kwargs):
        self._callback(*args, **kwargs)
        
    def _dateCtrlCallback(self, event, *args, **kwargs):
        # If user disables dateCtrl, disable timeCtrl too and vice versa:
        self._timeCtrl.Enable(self._isDateCtrlEnabled())
        # The datepicker sends an event with the new value before its own
        # value is changed. Silly. Fix that:
        if event.GetDate() != self._dateCtrl.GetValue():
            self._dateCtrl.SetValue(event.GetDate())
        self._callback(event, *args, **kwargs)

    def _isDateCtrlEnabled(self):
        return self._dateCtrl.GetValue().IsValid()
        
    def SetValue(self, dateTime):
        if dateTime is None or dateTime == date.DateTime():
            datePart = timePart = None
        else:
            datePart = dateTime.date()
            timePart = dateTime.time()
        wxDate = date2wxDateTime(datePart)
        if wxDate.IsValid() or self.__noneAllowed:
            self._dateCtrl.SetValue(wxDate)
        self._timeCtrl.SetValue(self.__formatTime(date.Now().time() if timePart is None else timePart))
        self._timeCtrl.Enable(self._isDateCtrlEnabled())
        
    def SetNone(self):
        ''' Set the date and time to none. allowNone should be True. '''
        assert self.__noneAllowed
        self._dateCtrl.SetValue(date2wxDateTime(None))
        self._timeCtrl.Disable()
        
    def GetValue(self):
        dateValue = wxDateTime2Date(self._dateCtrl.GetValue())
        if dateValue == date.Date():
            return date.DateTime()
        else:
            timeText = self._timeCtrl.GetValue().strip().lower()
            try:
                dateTime = dparser.parse(timeText, ignoretz=True, fuzzy=True)
                timeValue = date.Time(hour=dateTime.hour, 
                                      minute=dateTime.minute,
                                      second=dateTime.second)
            except ValueError:
                print 'ValueError'
                timeValue = date.Time()
            return date.DateTime.combine(dateValue, timeValue)

    def setCallback(self, callback):
        self._callback = callback
