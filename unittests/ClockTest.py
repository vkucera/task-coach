import test, date, wx
        
        
class ClockTest(test.wxTestCase):
    def setUp(self):
        date.Clock.instance = None
        
    def tearDown(self):
        date.Clock.instance = None
                
    def testNotification(self):
        self.notifications = 0
        self.clock = date.Clock()
        self.clock.registerObserver(self.onNotify)
        self.clock.notify()
        self.assertEqual(1, self.notifications)
        
    def onNotify(self, *args, **kwargs):
        self.notifications += 1
        
    def testSingleton(self):
        self.clock = date.Clock()
        clock2 = date.Clock()
        self.failUnless(self.clock is clock2)
        
    def testSyncWithSeconds_TimerTimeoutNeedsToBeMoreThanZero(self):
        # This makes the initial time out zero, be prepared
        self.clock = date.Clock(now=lambda: 0.999999999999999)
        