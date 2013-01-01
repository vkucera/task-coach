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

import taskcoachlib.i18n
from taskcoachlib.thirdparty import smartdatetimectrl as sdtc
from taskcoachlib.domain import date
from taskcoachlib import render

import wx, datetime


class _SmartDateTimeCtrl(sdtc.SmartDateTimeCtrl):
    def __init__(self, *args, **kwargs):
        self.__interval = (kwargs.get('startHour', 8), kwargs.get('endHour', 18))
        super(_SmartDateTimeCtrl, self).__init__(*args, **kwargs)

    def HandleKey(self, event):
        if not super(_SmartDateTimeCtrl, self).HandleKey(event) and self.GetDateTime() is not None:
            startHour, endHour = self.__interval
            if event.GetUnicodeKey() in [ord('s'), ord('S')]:
                hour = datetime.time(startHour, 0, 0, 0) if event.ShiftDown() else datetime.time(0, 0, 0, 0)
                self.SetDateTime(datetime.datetime.combine(self.GetDateTime().date(), hour), notify=True)
                return True
            elif event.GetUnicodeKey() in [ord('e'), ord('E')]:
                hour = datetime.time(endHour, 0, 0, 0) if event.ShiftDown() else datetime.time(23, 59, 0, 0)
                self.SetDateTime(datetime.datetime.combine(self.GetDateTime().date(), hour), notify=True)
                return True
        return False


class DateTimeCtrl(wx.Panel):
    def __init__(self, parent, callback=None, noneAllowed=True,
                 starthour=8, endhour=18, interval=15, showSeconds=False,
                 showRelative=False, units=None, **kwargs):
        super(DateTimeCtrl, self).__init__(parent, **kwargs)

        self.__callback = callback
        self.__ctrl = _SmartDateTimeCtrl(self, enableNone=noneAllowed,
                                         dateFormat=render.date,
                                         timeFormat=lambda x: render.time(x, seconds=showSeconds),
                                         startHour=starthour, endHour=endhour,
                                         minuteDelta=interval, secondDelta=interval, showRelative=showRelative,
                                         units=units)
        self.__ctrl.EnableChoices()

        # When the widget fires its event, its value has not changed yet (because it can be vetoed).
        # We need to store the new value so that GetValue() returns the right thing when called from event processing.
        self.__value = self.__ctrl.GetDateTime()

        sizer = wx.BoxSizer()
        sizer.Add(self.__ctrl, 1, wx.EXPAND)
        self.SetSizer(sizer)

        sdtc.EVT_DATETIME_CHANGE(self.__ctrl, self.__OnChange)

    def __OnChange(self, event):
        self.__value = event.GetValue()
        if self.__callback is not None:
            self.__callback()

    def EnableChoices(self, enabled=True):
        self.__ctrl.EnableChoices(enabled=enabled)

    def SetRelativeChoicesStart(self, start=None):
        self.__ctrl.SetRelativeChoicesStart(start=start)

    def HideRelativeButton(self):
        self.__ctrl.HideRelativeButton()

    def LoadChoices(self, choices):
        self.__ctrl.LoadChoices(choices)

    def GetValue(self):
        return date.DateTime() if self.__value is None else date.DateTime.fromDateTime(self.__value)

    def SetValue(self, dateTime):
        if dateTime == date.DateTime():
            dateTime = None
        self.__ctrl.SetDateTime(dateTime)
        self.__value = self.__ctrl.GetDateTime()

    def SetNone(self):
        self.__value = None
        self.__ctrl.SetDateTime(None)

    def setCallback(self, callback):
        self.__callback = callback

    def Cleanup(self):
        self.__ctrl.Cleanup()
