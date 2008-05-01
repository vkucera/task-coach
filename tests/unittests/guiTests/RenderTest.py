# -*- coding: utf-8 -*-

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

import test
from taskcoachlib.gui import render
from taskcoachlib.domain import task, date


class RenderDaysLeftTest(test.TestCase):
    def testOneDayLeft(self):
        self.assertEqual('1', render.daysLeft(date.TimeDelta(days=1), False))
        
    def testDueToday(self):
        self.assertEqual('0', render.daysLeft(date.TimeDelta(days=0), False))

    def testOneDayLate(self):
        self.assertEqual('-1', render.daysLeft(date.TimeDelta(days=-1), False))

    def testInfiniteTimeLeft(self):
        self.assertEqual('Infinite', render.daysLeft(date.TimeDelta.max, False))

    def testCompletedTask(self):
        self.assertEqual('', render.daysLeft(date.TimeDelta.max, True))
        

class RenderTimeSpentTest(test.TestCase):
    def testZeroTime(self):
        self.assertEqual('0:00:00', render.timeSpent(date.TimeDelta()))
        
    def testOneSecond(self):
        self.assertEqual('0:00:01', 
            render.timeSpent(date.TimeDelta(seconds=1)))
            
    def testTenHours(self):
        self.assertEqual('10:00:00', 
            render.timeSpent(date.TimeDelta(hours=10)))
            
    def testNegativeHours(self):
        self.assertEqual('-1:00:00', render.timeSpent(date.TimeDelta(hours=-1)))
        
    def testNegativeSeconds(self):
        self.assertEqual('-0:00:01', render.timeSpent(date.TimeDelta(seconds=-1)))


class RenderWeekNumberTest(test.TestCase):
    def testWeek1(self):
        self.assertEqual('2005-1', render.weekNumber(date.DateTime(2005,1,3)))
        
    def testWeek53(self):
        self.assertEqual('2004-53', render.weekNumber(date.DateTime(2004,12,31)))

