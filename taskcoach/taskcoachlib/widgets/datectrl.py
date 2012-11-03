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

from taskcoachlib.thirdparty import smartdatetimectrl as sdtc
from taskcoachlib.domain import date
from taskcoachlib import render
import wx


class DateTimeCtrl(wx.Panel):
    def __init__(self, parent, callback=None, noneAllowed=True,
                 starthour=8, endhour=18, interval=15, showSeconds=False,
                 *args, **kwargs):
        super(DateTimeCtrl, self).__init__(parent, *args, **kwargs)

        self.__callback = callback
        self.__ctrl = sdtc.SmartDateTimeCtrl(self, enableNone=noneAllowed,
                                             dateFormat=render.date,
                                             timeFormat=lambda x: render.time(x, seconds=showSeconds),
                                             startHour=starthour, endHour=endhour)

        # When the widget fires its event, its value has not changed yet (because it can be vetoed).
        # We need to store the new value so that GetValue() returns the right thing when called from event processing.
        self.__value = self.__ctrl.GetDateTime()

        sizer = wx.BoxSizer()
        sizer.Add(self.__ctrl, 1, wx.EXPAND)
        self.SetSizer(sizer)

        sdtc.EVT_DATETIME_CHANGE(self.__ctrl, self.__OnChange)

    def __OnChange(self, event):
        self.__value = event.GetValue()
        self.__callback()

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
