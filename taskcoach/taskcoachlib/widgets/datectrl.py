import wx
import domain.date as date


class Panel(wx.Panel):
    def __init__(self, parent, callback=None, *args, **kwargs):
        super(Panel, self).__init__(parent, *args, **kwargs)
        self._controls = self._createControls(callback)
        self._layout()
        
    def _createControls(self, callback):
        raise NotImplementedError
                
    def _layout(self):
        self._sizer = wx.BoxSizer(wx.HORIZONTAL)
        for control in self._controls:
            self._sizer.Add(control, flag=wx.ALIGN_CENTER_VERTICAL)
        self.SetSizerAndFit(self._sizer)


class _DatePickerCtrlThatFixesAllowNoneStyle(Panel):
    def __init__(self, parent, *args, **kwargs):
        self.__args = args
        self.__kwargs = kwargs
        super(_DatePickerCtrlThatFixesAllowNoneStyle, self).__init__(parent)
        
    def _createControls(self, callback):
        self.__check = wx.CheckBox(self)
        self.__check.Bind(wx.EVT_CHECKBOX, self.onCheck)
        self.__datePicker = wx.DatePickerCtrl(self, *self.__args,
            **self.__kwargs)
        self.__datePicker.Disable()
        return [self.__check, self.__datePicker]

    def onCheck(self, event):
        self.__datePicker.Enable(event.IsChecked())
        event.Skip()

    def GetValue(self):
        if self.__datePicker.IsEnabled():
            return self.__datePicker.GetValue()
        else:
            return wx.DateTime()

    def SetValue(self, value):
        if value.IsValid():
            self.__datePicker.Enable()
            self.__check.SetValue(True)
            self.__datePicker.SetValue(value)
        else:
            self.__datePicker.Disable()
            self.__check.SetValue(False)

    def IsEnabled(self):
        return self.__datePicker.IsEnabled()


def DatePickerCtrl(*args, **kwargs):
    ''' Factory function that returns _DatePickerCtrlThatFixesAllowNoneStyle 
        when necessary and wx.DatePickerCtrl otherwise. '''

    def styleIncludesDP_ALLOWNONE(style):
        return (style & wx.DP_ALLOWNONE) == wx.DP_ALLOWNONE 

    def styleDP_ALLOWNONEIsBroken():
        return not ('__WXMSW__' in wx.PlatformInfo)

    style = kwargs.get('style', wx.DP_DEFAULT)
    if styleIncludesDP_ALLOWNONE(style) and styleDP_ALLOWNONEIsBroken():
        kwargs['style'] = kwargs['style'] & ~wx.DP_ALLOWNONE
        DatePickerCtrlClass = _DatePickerCtrlThatFixesAllowNoneStyle
    else:
        DatePickerCtrlClass = wx.DatePickerCtrl
    return DatePickerCtrlClass(*args, **kwargs)


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
    def __init__(self, parent, callback=None, noneAllowed=True, *args, 
                 **kwargs):
        self._noneAllowed = noneAllowed
        super(DateCtrl, self).__init__(parent, callback, *args, **kwargs)
        self._callback = callback
        self.Bind(wx.EVT_DATE_CHANGED, self._callback)
        
    def _createControls(self, callback):
        style = wx.DP_DROPDOWN
        if self._noneAllowed:
            style |= wx.DP_ALLOWNONE
        return [DatePickerCtrl(self, style=style)]

    def SetValue(self, value):
        self._controls[0].SetValue(date2wxDateTime(value))

    def GetValue(self):
        return wxDateTime2Date(self._controls[0].GetValue())
        

class TimeCtrl(Panel):
    def __init__(self, parent, callback=None, *args, **kwargs):
        super(TimeCtrl, self).__init__(parent, callback, *args, **kwargs)
        
    def SetValue(self, time):
        self._controls[0].SetValue('%02d:%02d'%(time.hour, time.minute))
    
    def _createControls(self, callback):
        # TODO: use wx.lib.masked.ComboBox or wx.lib.masked.TimeCtrl?
        control = wx.ComboBox(self, value='00:00', choices=self._choices())
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
    def __init__(self, parent, dateTime, callback=None, noneAllowed=True, 
                 *args, **kwargs):
        self._noneAllowed = noneAllowed
        super(DateTimeCtrl, self).__init__(parent, callback, *args, **kwargs)
        self._callback = callback or self.__nullCallback
        self.SetValue(dateTime)
        
    def __nullCallback(self, *args, **kwargs):
        pass
        
    def _createControls(self, callback):
        self._dateCtrl = DateCtrl(self, self._dateCtrlCallback, 
            self._noneAllowed)
        self._dateCtrl.Bind(wx.EVT_CHECKBOX, self.onEnableDatePicker)
        self._timeCtrl = TimeCtrl(self, self._timeCtrlCallback)
        return [self._dateCtrl, self._timeCtrl]
        
    def onEnableDatePicker(self, event):
        self._timeCtrl.Enable(event.IsChecked())
        self._callback(event)

    def _timeCtrlCallback(self, *args, **kwargs):
        print '_timeCtrlCallback'
        self._callback(*args, **kwargs)
        
    def _dateCtrlCallback(self, *args, **kwargs):
        print '_dateCtrlCallback'
        if not self._isDateCtrlEnabled(): 
            self._timeCtrl.SetValue(date.Time())
        elif self._timeCtrl.GetValue() == date.Time():
            self._timeCtrl.SetValue(date.Time.now())
        # If user disables dateCtrl, disable timeCtrl too and vice versa:
        self._timeCtrl.Enable(self._isDateCtrlEnabled())
        self._callback(*args, **kwargs)

    def _isDateCtrlEnabled(self):
        return self._dateCtrl.GetValue() != date.Date()
        
    def SetValue(self, dateTime):
        if dateTime is None:
            datePart = None
            timePart = date.Time()
        else:
            datePart = dateTime.date()
            timePart = dateTime.time()
        self._dateCtrl.SetValue(datePart)
        self._timeCtrl.SetValue(timePart)
        self._timeCtrl.Enable(self._isDateCtrlEnabled())
        
    def GetValue(self):
        dateValue = self._dateCtrl.GetValue()
        if dateValue == date.Date():
            return date.DateTime.max
        else:
            return date.DateTime.combine(dateValue, self._timeCtrl.GetValue())

