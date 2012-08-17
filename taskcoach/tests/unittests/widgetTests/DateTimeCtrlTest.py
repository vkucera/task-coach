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

import test
from taskcoachlib import widgets
from taskcoachlib.domain import date


class CommonTestsMixin(object):
    def testGetValue(self):
        oneHour = date.DateTime(2000, 1, 1, hour=1)
        self.dateTimeCtrl.SetValue(oneHour)
        self.assertEqual(oneHour, self.dateTimeCtrl.GetValue())

    def testChoicesStartTime(self):
        self.assertEqual('08:00:00 AM' if self.showSeconds else '08:00 AM', 
                         self.dateTimeCtrl._timeChoices()[0])
        
    def testChoicesEndTime(self):
        self.assertEqual('06:00:00 PM' if self.showSeconds else '06:00 PM', 
                         self.dateTimeCtrl._timeChoices()[-1])
        
    def testChoicesEndTime24(self):
        dateTimeCtrl = widgets.datectrl.DateTimeCtrl(self.frame, endhour=24, 
                                                     showSeconds=self.showSeconds)
        self.assertEqual('11:45:00 PM' if self.showSeconds else '11:45 PM', 
                         dateTimeCtrl._timeChoices()[-1])

    def testChoicesStartTime0(self):
        dateTimeCtrl = widgets.datectrl.DateTimeCtrl(self.frame, starthour=0, 
                                                     showSeconds=self.showSeconds)
        self.assertEqual('12:00:00 AM' if self.showSeconds else '12:00 AM', 
                         dateTimeCtrl._timeChoices()[0])

        
class DateTimeCtrlTestCase(test.wxTestCase):
    def setUp(self):
        super(DateTimeCtrlTestCase, self).setUp()
        self.dateTimeCtrl = widgets.datectrl.DateTimeCtrl(self.frame, 
                                                          showSeconds=self.showSeconds)
        

class DateTimeCtrlTest_Seconds(CommonTestsMixin, DateTimeCtrlTestCase):
    showSeconds = True
        
    def testGetValue_SecondPrecision(self):
        oneHourAndTenSeconds = date.DateTime(2000, 1, 1, hour=1, second=10)
        self.dateTimeCtrl.SetValue(oneHourAndTenSeconds)
        self.assertEqual(oneHourAndTenSeconds, self.dateTimeCtrl.GetValue())


class DateTimeCtrlTest_NoSeconds(CommonTestsMixin, DateTimeCtrlTestCase):
    showSeconds = False

    def testGetValue_SecondPrecision(self):
        oneHour = date.DateTime(2000, 1, 1, hour=1)
        oneHourAndTenSeconds = date.DateTime(2000, 1, 1, hour=1, second=10)
        self.dateTimeCtrl.SetValue(oneHourAndTenSeconds)
        self.assertEqual(oneHour, self.dateTimeCtrl.GetValue())
