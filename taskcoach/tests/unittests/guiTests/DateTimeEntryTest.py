'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2010 Frank Niessink <frank@niessink.com>

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
from taskcoachlib.gui.dialog import entry 
from taskcoachlib.domain import date


class DateTimeEntryTest(test.wxTestCase):
    def setUp(self):
        super(DateTimeEntryTest, self).setUp()
        self.dateTimeEntry = entry.DateTimeEntry(self.frame)
        self.dateTime = date.DateTime(2004, 1, 1)

    def testCreate(self):
        self.assertEqual(date.DateTime(), self.dateTimeEntry.get())

    def testSet(self):
        now = date.Now()
        self.dateTimeEntry.set(now)
        self.assertAlmostEqual(now.toordinal(), 
                               self.dateTimeEntry.get().toordinal(), places=2)

    def testReset(self):
        self.dateTimeEntry.set()
        self.assertEqual(date.DateTime(), self.dateTimeEntry.get())

    def testValidDateTime(self):
        self.dateTimeEntry.set(self.dateTime)
        self.assertEqual(self.dateTime, self.dateTimeEntry.get())

    def testValidDateTimeWithDefaultDateTime(self):
        self.dateTimeEntry.set(self.dateTime)
        self.assertEqual(self.dateTime, self.dateTimeEntry.get(date.Now()))


class DateEntryConstructorTest(test.wxTestCase):
    def testCreateWithDate(self):
        tomorrow = date.Now() + date.oneDay
        dateTimeEntry = entry.DateTimeEntry(self.frame, tomorrow)
        self.assertAlmostEqual(tomorrow.toordinal(), 
                               dateTimeEntry.get().toordinal(),
                               places=2)
