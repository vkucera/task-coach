import test, effort, task, date

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
        self.assertEqual(date.TimeDelta(), effortPeriod.duration())
        