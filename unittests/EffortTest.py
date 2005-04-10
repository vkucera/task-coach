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
        self.assertEqual('', self.effort.getDescription())
        
    def testStr(self):
        self.assertEqual('Effort(%s, %s, %s)'%(self.effort.task(), 
            self.effort.getStart(), self.effort.getStop()), str(self.effort))
        
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
        currentTime = date.DateTime.now()
        now = lambda: currentTime
        self.assertEqual(now()-effortPeriod.getStart(), effortPeriod.duration(now=now))
     
    def testState(self):
        state = self.effort.__getstate__()
        newEffort = effort.Effort(task.Task())
        newEffort.__setstate__(state)
        self.assertEqual(newEffort, self.effort)
        self.assertEqual(newEffort.getDescription(), self.effort.getDescription())
        
    def testCompare(self):
        newEffort = effort.Effort(self.task, start=date.DateTime(2005,1,1),
            stop=date.DateTime(2005,1,2))
        self.failUnless(self.effort > newEffort)
        
    def testCopy(self):
        import copy
        copyEffort = copy.copy(self.effort)
        self.assertEqual(copyEffort, self.effort)
        self.assertEqual(copyEffort.getDescription(), self.effort.getDescription())
        
    def testDescription(self):
        self.effort.setDescription('description')
        self.assertEqual('description', self.effort.getDescription())
        
    def testDescription_Constructor(self):
        newEffort = effort.Effort(self.task, description='description')
        self.assertEqual('description', newEffort.getDescription())
        
    def testSetDescriptionDoesNotTriggerNotification(self):
        self.effort.setDescription('description')
        self.assertEqual(0, self.notifications)
        
    def testSetStop_None(self):
        self.effort.setStop()
        self.assertEqual(date.Today(), self.effort.getStop().date())
        
    def testSetStop_Infinite(self):
        self.effort.setStop(date.DateTime.max)
        self.assertEqual(None, self.effort.getStop())
        
    def testSetStop_SpecificDateTime(self):
        self.effort.setStop(date.DateTime(2005,1,1))
        self.assertEqual(date.DateTime(2005,1,1), self.effort.getStop())