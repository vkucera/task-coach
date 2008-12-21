'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>
Copyright (C) 2007-2008 Jerome Laheurte <fraca7@free.fr>
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
from wx.lib import masked
from taskcoachlib import widgets
from taskcoachlib.domain import date


class DateEntry(widgets.PanelWithBoxSizer):
    defaultDate = date.Date()

    def __init__(self, parent, date=defaultDate, readonly=False, callback=None,
                 *args, **kwargs):
        super(DateEntry, self).__init__(parent, *args, **kwargs)
        self._entry = widgets.DateCtrl(self, callback)
        if readonly:
            self._entry.Disable()
        self._entry.SetValue(date)
        self.add(self._entry)
        self.fit()

    def get(self, defaultDate=None):
        result = self._entry.GetValue()
        if result == date.Date() and defaultDate:
            result = defaultDate
        return result

    def set(self, date=defaultDate):
        self._entry.SetValue(date)

    def setToday(self):
        self._entry.SetValue(date.Today())


class TimeDeltaEntry(widgets.PanelWithBoxSizer):
    defaultTimeDelta=date.TimeDelta()

    def __init__(self, parent, timeDelta=defaultTimeDelta, readonly=False,
                 *args, **kwargs):
        super(TimeDeltaEntry, self).__init__(parent, *args, **kwargs)
        if readonly:
            self._entry = wx.StaticText(self, label=render.timeSpent(timeDelta))
        else:
            self._entry = masked.TextCtrl(self, mask='#{6}:##:##',
                fields=[masked.Field(formatcodes='rRFS'),
                        masked.Field(formatcodes='RFS'),
                        masked.Field(formatcodes='RFS')])
            hours, minutes, seconds = timeDelta.hoursMinutesSeconds()
            self._entry.SetFieldParameters(0, defaultValue='%6d'%hours)
            self._entry.SetFieldParameters(1, defaultValue='%02d'%minutes)
            self._entry.SetFieldParameters(2, defaultValue='%02d'%seconds)
        self.add(self._entry, flag=wx.EXPAND|wx.ALL, proportion=1)
        self.fit()

    def get(self):
        return date.parseTimeDelta(self._entry.GetValue())


class AmountEntry(widgets.PanelWithBoxSizer):
    def __init__(self, parent, amount=0.0, readonly=False, *args, **kwargs):
        super(AmountEntry, self).__init__(parent, *args, **kwargs)
        if readonly:
            self._entry = wx.StaticText(self, label=render.amount(amount))
        else:
            self._entry = masked.NumCtrl(self, fractionWidth=2,
                                         allowNegative=False, value=amount)
        self.add(self._entry)
        self.fit()

    def get(self):
        return self._entry.GetValue()

    def set(self, value):
        self._entry.SetValue(value)
