# -*- coding: utf-8 -*-

import test
from gui import render
from domain import task, date


class RenderDaysLeftTest(test.TestCase):
    def testOneDayLeft(self):
        self.assertEqual('1', render.daysLeft(date.TimeDelta(days=1), False))
        
    def testDueToday(self):
        self.assertEqual('0', render.daysLeft(date.TimeDelta(days=0), False))

    def testOneDayLate(self):
        self.assertEqual('-1', render.daysLeft(date.TimeDelta(days=-1), False))

    def testInfiniteTimeLeft(self):
        self.assertEqual(u'∞', render.daysLeft(date.TimeDelta.max, False))

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