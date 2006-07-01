import test, wx
import domain.date as date
        
class ClockTest(test.wxTestCase):
    def setUp(self):
        self.events = []
        self.clock = date.Clock()
         
    def tearDown(self):
        date.Clock.deleteInstance()
        
    def onEvent(self, event):
        self.events.append(event)
                
    def testNotification(self):
        self.clock.registerObserver(self.onEvent, 'clock.second')
        self.clock.notify()
        self.assertEqual(1, len(self.events))
        
    def testSingleton(self):
        clock2 = date.Clock()
        self.failUnless(self.clock is clock2)
        
    def testSyncWithSeconds_TimerTimeoutNeedsToBeMoreThanZero(self):
        # This makes the initial timeout zero, be prepared
        self.clock = date.Clock(now=lambda: 0.999999999999999)
        
    def testRegisterForSpecificTime(self):
        realSoonNow = date.DateTime.now() + date.TimeDelta(seconds=1)
        self.clock.registerObserver(self.onEvent, realSoonNow)
        self.clock.notify(now=realSoonNow)
        self.assertEqual(1, len(self.events))
            
