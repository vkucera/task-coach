import test, effort, task, date

__coverage__ = [effort.Effort]

class EffortTest(test.TestCase):
    def setUp(self):
        self.task = task.Task()
        self.effort = effort.Effort(self.task, start=date.DateTime(2004, 1, 1),
            stop=date.DateTime(2004,1,2))
        self.notifications = 0
        self.effort.registerObserver(self.notify)
        
    def notify(self, *args):
        self.notifications += 1
        
    def testCreate(self):
        self.assertEqual(self.task, self.effort.task())
        
    def testDuration(self):
        self.assertEqual(date.TimeDelta(days=1), self.effort.duration())

    def testNotificationForSetStart(self):
        self.effort.setStart(date.DateTime.now())
        self.assertEqual(1, self.notifications)
        
    def testNotificationForSetStop(self):
        self.effort.setStop(date.DateTime.now())
        self.assertEqual(1, self.notifications)
        
    def testDefaultStartAndStop(self):
        effortPeriod = effort.Effort(self.task)
        now = lambda: date.DateTime.now()
        self.assertEqual(now()-effortPeriod.getStart(), effortPeriod.duration(now=now))
     
    def testState(self):
        state = self.effort.__getstate__()
        newEffort = effort.Effort(task.Task())
        newEffort.__setstate__(state)
        self.assertEqual(newEffort, self.effort)
        
    def testCompare(self):
        newEffort = effort.Effort(self.task, start=date.DateTime(2005,1,1),
            stop=date.DateTime(2005,1,2))
        self.failUnless(self.effort < newEffort)
        
    def testCopy(self):
        import copy
        copyEffort = copy.copy(self.effort)
        self.assertEqual(copyEffort, self.effort)