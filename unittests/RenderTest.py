import test, task, date
from gui import render

class RenderSubjectTest(test.TestCase):
    def setUp(self):
        self.parent = task.Task(subject='Parent')
        self.child = task.Task(subject='Child')
        self.parent.addChild(self.child)
        
    def testSubject(self):
        self.assertEqual('Parent', render.subject(self.parent))

    def testSubjectWithChild(self):
        self.assertEqual('Parent+Child', 
            render.subject(self.child, recursively=True, sep='+'))

    def testSubjectRecursively(self):
        self.assertEqual('Child',
            render.subject(self.child, recursively=False, sep='+'))


class RenderTimeLeftTest(test.TestCase):
    def testOneDayLeft(self):
        self.assertEqual('1', render.timeLeft(date.TimeDelta(days=1)))

    def testOneDayLate(self):
        self.assertEqual('-1', render.timeLeft(date.TimeDelta(days=-1)))

    def testInfiniteTimeLeft(self):
        self.assertEqual('Infinite', render.timeLeft(date.TimeDelta.max))


class RenderTimeSpentTest(test.TestCase):
    def testZeroTime(self):
        self.assertEqual('0:00:00', render.timeSpent(date.TimeDelta()))
        
    def testOneSecond(self):
        self.assertEqual('0:00:01', 
            render.timeSpent(date.TimeDelta(seconds=1)))
            
    def testTenHours(self):
        self.assertEqual('10:00:00', 
            render.timeSpent(date.TimeDelta(hours=10)))
        

class RenderWeekNumberTest(test.TestCase):
    def testWeek1(self):
        self.assertEqual('2005-1', render.weekNumber(date.DateTime(2005,1,3)))
        
    def testWeek53(self):
        self.assertEqual('2004-53', render.weekNumber(date.DateTime(2004,12,31)))