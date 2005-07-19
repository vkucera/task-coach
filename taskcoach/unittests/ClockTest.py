import test, date, wx
        
        
class ClockTest(test.wxTestCase):
    def testNotification(self):
        self.notifications = 0
        clock = date.Clock()
        clock.registerObserver(self.onNotify)
        clock.notify()
        self.assertEqual(1, self.notifications)
        
    def onNotify(self, *args, **kwargs):
        self.notifications += 1
        
    def testSingleton(self):
        clock1 = date.Clock()
        clock2 = date.Clock()
        self.failUnless(clock1 is clock2)