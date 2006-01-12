import test, wx
import domain.date as date
        
class ClockTest(test.wxTestCase):
    def setUp(self):
        self.notifications = 0
        self.clock = date.Clock()
         
    def tearDown(self):
        date.Clock.deleteInstance()
        
    def onNotify(self, *args, **kwargs):
        self.notifications += 1
                
    def testNotification(self):
        self.clock.registerObserver(self.onNotify)
        self.clock.notify()
        self.assertEqual(1, self.notifications)
        
    def testSingleton(self):
        clock2 = date.Clock()
        self.failUnless(self.clock is clock2)
        
    def testSyncWithSeconds_TimerTimeoutNeedsToBeMoreThanZero(self):
        # This makes the initial timeout zero, be prepared
        self.clock = date.Clock(now=lambda: 0.999999999999999)
        
    def testRegisterForSpecificTime(self):
        realSoonNow = date.DateTime.now() + date.TimeDelta(seconds=1)
        self.clock.registerObserver(self.onNotify, realSoonNow)
        self.clock.notify(now=realSoonNow)
        self.assertEqual(1, self.notifications)
            