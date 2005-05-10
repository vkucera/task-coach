import wx, date, statictextctrl
from i18n import _

class Panel(wx.Panel):
    def __init__(self, parent, callback=None, *args, **kwargs):
        super(Panel, self).__init__(parent, -1, *args, **kwargs)
        self._controls = self._createControls(callback)
        self._layout()
        
    def _createControls(self, callback):
        raise NotImplementedError
                
    def _layout(self):
        self._sizer = wx.BoxSizer(wx.HORIZONTAL)
        for control in self._controls:
            self._sizer.Add(control)
        self.SetSizerAndFit(self._sizer)


def date2wxDateTime(value):
    wxDateTime = wx.DateTime()
    try: # prepare for a value that is not a Python datetime instance
        if value < date.Date():
            wxDateTime.Set(value.day, value.month-1, value.year)
    except (TypeError, AttributeError):
        pass
    return wxDateTime
    
def wxDateTime2Date(wxDateTime):
    if wxDateTime.IsValid():
        return date.Date(wxDateTime.GetYear(), wxDateTime.GetMonth()+1,
            wxDateTime.GetDay())
    else:
        return date.Date()

    
class DateCtrl(Panel):
    def __init__(self, parent, callback=None, noneAllowed=True, *args, **kwargs):
        self._noneAllowed = noneAllowed
        super(DateCtrl, self).__init__(parent, callback, *args, **kwargs)
        self._callback = callback
        self.Bind(wx.EVT_DATE_CHANGED, self._callback)
        
    def _createControls(self, callback):
        style = wx.DP_DROPDOWN
        if self._noneAllowed:
            style |= wx.DP_ALLOWNONE
        return [wx.DatePickerCtrl(self, -1, style=style)]

    def SetValue(self, value):
        self._controls[0].SetValue(date2wxDateTime(value))

    def GetValue(self):
        return wxDateTime2Date(self._controls[0].GetValue())
        

class StaticDateCtrl(DateCtrl):
    def _createControls(self, callback):
        return [statictextctrl.StaticTextCtrl(self)]
        
    def SetValue(self, value):
        self._value = value
        # Use wx.DateTime to get locale dependent formatting
        value = date2wxDateTime(value)
        if value.IsValid():
            value = value.FormatDate() 
        else:
            value = _('None')
        self._controls[0].SetValue(value)
        
    def GetValue(self):
        return self._value


class TimeCtrl(Panel):
    def __init__(self, parent, callback=None, *args, **kwargs):
        super(TimeCtrl, self).__init__(parent, callback, *args, **kwargs)
        
    def SetValue(self, time):
        self._controls[0].SetValue('%02d:%02d'%(time.hour, time.minute))
    
    def _createControls(self, callback):
        # TODO: use wx.lib.masked.ComboBox or wx.lib.masked.TimeCtrl?
        control = wx.ComboBox(self, -1, '00:00', choices=self._choices())
        control.Bind(wx.EVT_TEXT, callback)
        control.Bind(wx.EVT_COMBOBOX, callback)
        return [control]
        
    def _choices(self):
        choices = []
        for hour in range(8, 18):
            for minute in range(0, 60, 15):
                choices.append('%02d:%02d'%(hour, minute))
        return choices
        
    def GetValue(self):
        value = self._controls[0].GetValue()
        try:
            hour, minute = value.split(':')
            time = date.Time(int(hour), int(minute))
        except:
            time = date.Time()
        return time


class DateTimeCtrl(Panel):
    def __init__(self, parent, dateTime, callback=None, noneAllowed=True, *args, **kwargs):
        self._noneAllowed = noneAllowed
        super(DateTimeCtrl, self).__init__(parent, callback, *args, **kwargs)
        self._callback = callback
        self.SetValue(dateTime)
        
    def _createControls(self, callback):
        self._dateCtrl = DateCtrl(self, self._dateCtrlCallback, self._noneAllowed)
        self._timeCtrl = TimeCtrl(self, self._timeCtrlCallback)
        return self._dateCtrl, self._timeCtrl
        
    def _timeCtrlCallback(self, *args, **kwargs):
        # if user sets time and date == None, then set date to today
        if self._dateCtrl.GetValue() == date.Date():
            self._dateCtrl.SetValue(date.Today())
        self._callback(*args, **kwargs)
        
    def _dateCtrlCallback(self, *args, **kwargs):
        # if users sets date and time == '00:00', then set time to now
        if self._dateCtrl.GetValue() == date.Date():
            self._timeCtrl.SetValue(date.Time())
        elif self._timeCtrl.GetValue() == date.Time():
            self._timeCtrl.SetValue(date.Time.now())
        self._callback(*args, **kwargs)
        
    def SetValue(self, dateTime):
        if dateTime is None:
            datePart = 'None'
            timePart = date.Time()
        else:
            datePart = dateTime.date()
            timePart = dateTime.time()
        self._dateCtrl.SetValue(datePart)
        self._timeCtrl.SetValue(timePart)
        
    def GetValue(self):
        return date.DateTime.combine(self._dateCtrl.GetValue(), 
            self._timeCtrl.GetValue())