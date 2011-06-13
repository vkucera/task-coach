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

import test
from taskcoachlib import widgets
from taskcoachlib.domain import date


class CommonTestsMixin(object):
    def testGetValue(self):
        oneHour = date.DateTime(2000,1,1,hour=1)
        self.dateTimeCtrl.SetValue(oneHour)
        self.assertEqual(oneHour, self.dateTimeCtrl.GetValue())

    def testChoicesStartTime(self):
        self.assertEqual('08:00:00' if self.showSeconds else '08:00', 
                         self.dateTimeCtrl._timeCtrl._choices()[0])
        
    def testChoicesEndTime(self):
        self.assertEqual('18:00:00' if self.showSeconds else '18:00', 
                         self.dateTimeCtrl._timeCtrl._choices()[-1])
        
    def testChoicesEndTime24(self):
        dateTimeCtrl = widgets.datectrl.DateTimeCtrl(self.frame, endhour=24, 
                                                     showSeconds=self.showSeconds)
        self.assertEqual('23:45:00' if self.showSeconds else '23:45', 
                         dateTimeCtrl._timeCtrl._choices()[-1])

    def testChoicesStartTime0(self):
        dateTimeCtrl = widgets.datectrl.DateTimeCtrl(self.frame, starthour=0, 
                                                     showSeconds=self.showSeconds)
        self.assertEqual('00:00:00' if self.showSeconds else '00:00', 
                         dateTimeCtrl._timeCtrl._choices()[0])

        
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
