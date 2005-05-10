import test, datetime, date

class PyDateTimeTest(test.TestCase):
    def testReplaceCannotBeEasilyUsedToFindTheLastDayofTheMonth(self):
        date = datetime.date(2004, 4, 1) # April 1st, 2004
        try:
            lastDayOfApril = date.replace(day=31)
            self.fail('Surprise! datetime.date.replace works as we want!')
            self.assertEqual(datetime.date(2004, 4, 30), lastDayOfApril)
        except ValueError:
            pass

class DateTimeTest(test.TestCase):
    def testWeekNumber(self):
        self.assertEqual(53, date.DateTime(2005,1,1).weeknumber())
        self.assertEqual(1, date.DateTime(2005,1,3).weeknumber())
        
        
    def testStartOfDay(self):
        startOfDay = date.DateTime(2005,1,1,0,0,0,0)
        noonish = date.DateTime(2005,1,1,12,30,15,400)
        self.assertEqual(startOfDay, noonish.startOfDay())
        
    def testEndOfDay(self):
        endOfDay = date.DateTime(2005,1,1,23,59,59,999999)
        noonish = date.DateTime(2005,1,1,12,30,15,400)
        self.assertEqual(endOfDay, noonish.endOfDay())
        
    def testStartOfWeek(self):
        startOfWeek = date.DateTime(2005,3,28,0,0,0,0)
        midweek = date.DateTime(2005,3,31,12,30,15,400)
        self.assertEqual(startOfWeek, midweek.startOfWeek())

    def testEndOfWeek(self):
        endOfWeek = date.DateTime(2005,4,3,23,59,59,999999)
        midweek = date.DateTime(2005,3,31,12,30,15,400)
        self.assertEqual(endOfWeek, midweek.endOfWeek())      
        
    def testStartOfMonth(self):
        startOfMonth = date.DateTime(2005,4,1)
        midMonth = date.DateTime(2005,4,15,12,45,1,999999)
        self.assertEqual(startOfMonth, midMonth.startOfMonth())
        
    def testEndOfMonth(self):
        endOfMonth = date.DateTime(2005,4,30).endOfDay()
        midMonth = date.DateTime(2005,4,15,12,45,1,999999)
        self.assertEqual(endOfMonth, midMonth.endOfMonth())
        
class TimeTest(test.TestCase):
    def testNow(self):
        now = date.Time.now()
