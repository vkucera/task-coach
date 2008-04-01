'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>

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

import test, widgets
from domain import date


class TimeCtrlTest(test.wxTestCase):
    def setUp(self):
        self.timeCtrl = widgets.datectrl.TimeCtrl(self.frame)
        
    def testGetValue(self):
        oneHour = date.Time(hour=1)
        self.timeCtrl.SetValue(oneHour)
        self.assertEqual(oneHour, self.timeCtrl.GetValue())

    def testGetValue_SecondPrecision(self):
        oneHourAndTenSeconds = date.Time(hour=1, second=10)
        self.timeCtrl.SetValue(oneHourAndTenSeconds)
        self.assertEqual(oneHourAndTenSeconds, self.timeCtrl.GetValue())
