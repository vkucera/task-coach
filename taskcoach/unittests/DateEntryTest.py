import test, date
from gui import editor 

class DateEntryTest(test.wxTestCase):
    def setUp(self):
        self.dateEntry = editor.DateEntry(self.frame)

    def testCreate(self):
        self.assertEqual(date.Date(), self.dateEntry.get())

    def testSet(self):
        self.dateEntry.set(date.Today())
        self.assertEqual(date.Today(), self.dateEntry.get())

    def testReset(self):
        self.dateEntry.set()
        self.assertEqual(date.Date(), self.dateEntry.get())

    def testValidDate(self):
        self.dateEntry.set('2004-1-1')
        self.assertEqual(date.Date(2004, 1, 1), self.dateEntry.get())

    def testValidDateWithDefaultDate(self):
        self.dateEntry.set('2004-1-1')
        self.assertEqual(date.Date(2004, 1, 1), 
            self.dateEntry.get(date.Today()))

    def testInvalidDate(self):
        self.dateEntry.set('bla')
        self.assertEqual(date.Date(), self.dateEntry.get())

    def testInvalidDateWithDefaultDate(self):
        self.dateEntry.set('bla')
        self.assertEqual(date.Tomorrow(), self.dateEntry.get(date.Tomorrow()))


class DateEntryConstructorTest(test.wxTestCase):
    def testCreateWithDate(self):
        dateEntry = editor.DateEntry(self.frame, date.Tomorrow())
        self.assertEqual(date.Tomorrow(), dateEntry.get())

