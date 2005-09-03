import test, date, wx
        
        
class ClockTest(test.wxTestCase):    
    def tearDown(self):
        date.Clock.deleteInstance()
        
    def onNotify(self, *args, **kwargs):
        self.notifications += 1
                
    def testNotification(self):
        self.notifications = 0
        self.clock = date.Clock()
        self.clock.registerObserver(self.onNotify)
        self.clock.notify()
        self.assertEqual(1, self.notifications)
        
    def testSingleton(self):
        self.clock = date.Clock()
        clock2 = date.Clock()
        self.failUnless(self.clock is clock2)
        
    def testSyncWithSeconds_TimerTimeoutNeedsToBeMoreThanZero(self):
        # This makes the initial timeout zero, be prepared
        self.clock = date.Clock(now=lambda: 0.999999999999999)
            