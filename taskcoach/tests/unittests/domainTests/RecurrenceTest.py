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
from taskcoachlib.domain import date


class DailyRecurrenceTest(test.TestCase):        
    def testNextDate(self):
        self.assertEqual(date.Tomorrow(), date.next(date.Today(), 'daily'))
        
    def testNextDateTwice(self):
        today = date.next(date.Yesterday(), 'daily')
        self.assertEqual(date.Tomorrow(), date.next(today, 'daily'))
        
    def testNextDateWithInfiniteDate(self):
        self.assertEqual(date.Date(), date.next(date.Date(), 'daily'))
        
        
class WeeklyRecurrenceTest(test.TestCase):
    def setUp(self):
        self.January1 = date.Date(2000,1,1)
        self.January8 = date.Date(2000,1,8)
        self.January15 = date.Date(2000,1,15)
        
    def testNextDate(self):
        self.assertEqual(self.January8, 
                         date.next(self.January1, 'weekly'))
        
    def testNextDateTwice(self):
        January8 = date.next(self.January1, 'weekly')
        self.assertEqual(self.January15, date.next(January8, 'weekly'))

    def testNextDateWithInfiniteDate(self):
        self.assertEqual(date.Date(), date.next(date.Date(), 'weekly'))
    

class MonthlyRecurrenceTest(test.TestCase):
    def testFirstDayOf31DayMonth(self):
        self.assertEqual(date.Date(2000,2,1), 
                         date.next(date.Date(2000,1,1), 'monthly'))
        
    def testFirstDayOf30DayMonth(self):
        self.assertEqual(date.Date(2000,5,1),
                         date.next(date.Date(2000,4,1), 'monthly'))
        
    def testFirstDayOfDecember(self):
        self.assertEqual(date.Date(2001,1,1),
                         date.next(date.Date(2000,12,1), 'monthly'))
        
    def testLastDayOf31DayMonth(self):
        self.assertEqual(date.Date(2000,4,30), 
                         date.next(date.Date(2000,3,31), 'monthly'))
        
    def testLastDayOf30DayMonth(self):
        self.assertEqual(date.Date(2000,5,30), 
                         date.next(date.Date(2000,4,30), 'monthly'))
        
    def testNextDateWithInfiniteDate(self):
        self.assertEqual(date.Date(), date.next(date.Date(), 'monthly'))


class YearlyRecurrenceTest(test.TestCase):
    def testJanuary1(self):
        self.assertEqual(date.Date(2002,1,1), 
                         date.next(date.Date(2001,1,1), 'yearly'))
        
    def testJanuary1_LeapYear(self):
        self.assertEqual(date.Date(2001,1,1), 
                         date.next(date.Date(2000,1,1), 'yearly'))

    def testMarch1_LeapYear(self):
        self.assertEqual(date.Date(2001,3,1), 
                         date.next(date.Date(2000,3,1), 'yearly'))
        
    def testMarch1_YearBeforeLeapYear(self):
        self.assertEqual(date.Date(2004,3,1), 
                         date.next(date.Date(2003,3,1), 'yearly'))

    def testFebruary1_YearBeforeLeapYear(self):
        self.assertEqual(date.Date(2004,2,1), 
                         date.next(date.Date(2003,2,1), 'yearly'))

    def testFebruary28(self):
        self.assertEqual(date.Date(2003,2,28), 
                         date.next(date.Date(2002,2,28), 'yearly'))

    def testFebruary28_LeapYear(self):
        self.assertEqual(date.Date(2005,2,28), 
                         date.next(date.Date(2004,2,28), 'yearly'))

    def testFebruary28_YearBeforeLeapYear(self):
        self.assertEqual(date.Date(2004,2,28), 
                         date.next(date.Date(2003,2,28), 'yearly'))

    def testFebruary29(self):
        self.assertEqual(date.Date(2005,2,28), 
                         date.next(date.Date(2004,2,29), 'yearly'))
        
    def testNextDateWithInfiniteDate(self):
        self.assertEqual(date.Date(), date.next(date.Date(), 'yearly'))
