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