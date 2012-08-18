'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2012 Task Coach developers <developers@taskcoach.org>

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

import test, locale
from taskcoachlib import widgets, render
from taskcoachlib.domain import date


class CommonTestsMixin(object):
    def setUp(self):
        super(CommonTestsMixin, self).setUp()
        locale.setlocale(locale.LC_ALL, 'en_US.utf8' if self.ampm else 'fr_FR.utf8')
        reload(render) # To execute module-level code every time

    def _format(self, hour, minute, second):
        if self.ampm:
            dpyHour = hour % 12
            if dpyHour == 0:
                dpyHour = 12
            r = '%02d:%02d' % (dpyHour, minute)
            if self.showSeconds:
                r += ':%02d' % second
            r += ' AM' if hour <= 12 else ' PM'
        else:
            r = '%02d:%02d' % (hour, minute)
            if self.showSeconds:
                r += ':%02d' % second
        return r

    def testGetValue(self):
        oneHour = date.DateTime(2000, 1, 1, hour=1)
        self.dateTimeCtrl.SetValue(oneHour)
        self.assertEqual(oneHour, self.dateTimeCtrl.GetValue())

    def testChoicesStartTime(self):
        self.assertEqual(self._format(8, 0, 0), 
                         self.dateTimeCtrl._timeChoices()[0])
        
    def testChoicesEndTime(self):
        self.assertEqual(self._format(18, 0, 0), 
                         self.dateTimeCtrl._timeChoices()[-1])
        
    def testChoicesEndTime24(self):
        dateTimeCtrl = widgets.datectrl.DateTimeCtrl(self.frame, endhour=24, 
                                                     showSeconds=self.showSeconds)
        self.assertEqual(self._format(23, 45, 0), 
                         dateTimeCtrl._timeChoices()[-1])

    def testChoicesStartTime0(self):
        dateTimeCtrl = widgets.datectrl.DateTimeCtrl(self.frame, starthour=0, 
                                                     showSeconds=self.showSeconds)
        self.assertEqual(self._format(0, 0, 0), 
                         dateTimeCtrl._timeChoices()[0])

        
class DateTimeCtrlTestCase(test.wxTestCase):
    def setUp(self):
        super(DateTimeCtrlTestCase, self).setUp()
        self.dateTimeCtrl = widgets.datectrl.DateTimeCtrl(self.frame, 
                                                          showSeconds=self.showSeconds)


class DateTimeCtrlTest_Seconds_Base(CommonTestsMixin):
    showSeconds = True

    def testGetValue_SecondPrecision(self):
        oneHourAndTenSeconds = date.DateTime(2000, 1, 1, hour=1, second=10)
        self.dateTimeCtrl.SetValue(oneHourAndTenSeconds)
        self.assertEqual(oneHourAndTenSeconds, self.dateTimeCtrl.GetValue())


class DateTimeCtrlTest_Seconds(DateTimeCtrlTest_Seconds_Base, DateTimeCtrlTestCase):
    ampm = False


class DateTimeCtrlTest_Seconds_AMPM(DateTimeCtrlTest_Seconds_Base, DateTimeCtrlTestCase):
    ampm = True


class DateTimeCtrlTest_NoSeconds_Base(CommonTestsMixin):
    showSeconds = False

    def testGetValue_SecondPrecision(self):
        oneHour = date.DateTime(2000, 1, 1, hour=1)
        oneHourAndTenSeconds = date.DateTime(2000, 1, 1, hour=1, second=10)
        self.dateTimeCtrl.SetValue(oneHourAndTenSeconds)
        self.assertEqual(oneHour, self.dateTimeCtrl.GetValue())


class DateTimeCtrlTest_NoSeconds(DateTimeCtrlTest_NoSeconds_Base, DateTimeCtrlTestCase):
    ampm = False


class DateTimeCtrlTest_NoSeconds_AMPM(DateTimeCtrlTest_NoSeconds_Base, DateTimeCtrlTestCase):
    ampm = True
