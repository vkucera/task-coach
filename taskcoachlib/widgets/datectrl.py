import wx, wx.calendar, date, statictextctrl

class CalendarPopup(wx.Frame):
    def __init__(self, parent, callback=None, *args, **kwargs):
        super(CalendarPopup, self).__init__(parent, -1, 
            style=wx.SIMPLE_BORDER|wx.FRAME_FLOAT_ON_PARENT|wx.FRAME_NO_TASKBAR,
            *args, **kwargs)
        self._callback = callback
        panel = wx.Panel(self, -1)
        border = 5
        self.calendar = wx.calendar.CalendarCtrl(panel, -1,
            pos=(border, border), style=wx.WANTS_CHARS)
        self.setDate()
        self.calendar.Bind(wx.calendar.EVT_CALENDAR_DAY, 
            self.onDateSelected)
        self.setupFocus()
        bestSize = self.calendar.GetBestSize()
        panel.SetSize( (bestSize.width+border*2, bestSize.height+border*2) )
        self.SetSize(panel.GetSize())
    
    def onDateSelected(self, event):
        wxDate = self.calendar.GetDate()
        newDate = date.Date(wxDate.GetYear(), wxDate.GetMonth()+1, 
                            wxDate.GetDay())
        self.GetParent().SetValue(newDate)
        if self._callback:
            self._callback(event)
        self.Destroy()
    
    def setupFocus(self):
        self.timer = None
        self.calendar.SetFocus()
        for control in self._calendarControls():
            control.Bind(wx.EVT_KILL_FOCUS, self.onKillFocus)
            control.Bind(wx.EVT_SET_FOCUS, self.onSetFocus)
                
    def onKillFocus(self, event):
        if wx.Window.FindFocus() not in self._calendarControls():
            # remove the calendar 1 second after it loses focus
            self.timer = wx.FutureCall(1000, self.Destroy)
        event.Skip()
        
    def onSetFocus(self, event):
        if self.timer:
            self.timer.Stop()
        event.Skip()    
        
    def setDate(self):
        currentDate = self.GetParent().GetValue()
        if currentDate == date.Date():
            currentDate = date.Today()
        self.calendar.SetDate(wx.DateTimeFromDMY(currentDate.day, 
            currentDate.month-1, currentDate.year))

    def _calendarControls(self):
        return [self.calendar, self.calendar.GetMonthControl(), 
            self.calendar.GetYearControl()]


class Panel(wx.Panel):
    def __init__(self, parent, callback=None, render=str, *args, **kwargs):
        super(Panel, self).__init__(parent, -1, *args, **kwargs)
        self._render = render
        self._controls = self._createControls(callback)
        self._layout()
        
    def _createControls(self, callback):
        control = wx.TextCtrl(self, -1)
        if callback:
            control.Bind(wx.EVT_KILL_FOCUS, callback)
        return [control]
 
    def SetValue(self, value):
        self._controls[0].SetValue(self._render(value))

    def GetValue(self):
        return self._controls[0].GetValue()
        
    def _layout(self):
        self._sizer = wx.BoxSizer(wx.HORIZONTAL)
        for control in self._controls:
            self._sizer.Add(control)
        self.SetSizerAndFit(self._sizer)

   
class DateCtrl(Panel):
    def __init__(self, parent, callback=None, *args, **kwargs):
        super(DateCtrl, self).__init__(parent, callback, *args, **kwargs)
        self._callback = callback
        self.Bind(wx.EVT_BUTTON, self.popupCalendar)
        
    def _createControls(self, callback):
        controls = super(DateCtrl, self)._createControls(callback) 
        dateButton = wx.BitmapButton(self, -1, 
            wx.ArtProvider_GetBitmap('date', wx.ART_BUTTON, (16,16)))
        return controls + [dateButton]
    
    def popupCalendar(self, event):
        button = event.GetEventObject()
        pos = button.ClientToScreen( (0,0) )
        size = button.GetSize()
        calendarPopup = CalendarPopup(self, self._callback,
            pos=(pos[0],pos[1]+size[1]))
        calendarPopup.Show()

    def GetValue(self):
        value = super(DateCtrl, self).GetValue()
        try:
            year, month, day = value.split('-')
            value = date.Date(int(year), int(month), int(day))
        except:
            value = date.Date()
        return value


class StaticDateCtrl(DateCtrl):
    def _createControls(self, callback):
        return [statictextctrl.StaticTextCtrl(self)]
        
        
class TimeCtrl(Panel):
    def __init__(self, parent, callback=None, *args, **kwargs):
        super(TimeCtrl, self).__init__(parent, callback, self._renderTime, *args, **kwargs)
        
    def _renderTime(self, time):
        return '%02d:%02d'%(time.hour, time.minute)
    
    def _createControls(self, callback):
        # TODO: use wx.lib.masked.ComboBox or wx.lib.masked.TimeCtrl?
        control = wx.ComboBox(self, -1, '00:00', choices=self._choices())
        control.Bind(wx.EVT_KILL_FOCUS, callback)
        return [control]
        
    def _choices(self):
        choices = []
        for hour in range(8, 18):
            for minute in range(0, 60, 15):
                choices.append('%02d:%02d'%(hour, minute))
        return choices
        
    def GetValue(self):
        value = super(TimeCtrl, self).GetValue()
        try:
            hour, minute = value.split(':')
            time = date.Time(int(hour), int(minute))
        except:
            time = date.Time()
        return time


class DateTimeCtrl(Panel):
    def __init__(self, parent, dateTime, callback=None, *args, **kwargs):
        super(DateTimeCtrl, self).__init__(parent, callback, *args, **kwargs)
        self.SetValue(dateTime)
        
    def _createControls(self, callback):
        return [DateCtrl(self, callback), TimeCtrl(self, callback)]
        
    def SetValue(self, dateTime):
        self._controls[0].SetValue(dateTime.date())
        self._controls[1].SetValue(dateTime.time())
        
    def GetValue(self):
        dateValue = self._controls[0].GetValue()
        timeValue = self._controls[1].GetValue()
        return date.DateTime.combine(dateValue, timeValue)