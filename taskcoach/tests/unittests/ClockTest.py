import test, wx, patterns
from domain import date


class ClockTest(test.wxTestCase):
    def setUp(self):
        self.events = []
        self.clock = date.Clock()
         
    def tearDown(self):
        super(ClockTest, self).tearDown()
        date.Clock.deleteInstance()
        
    def onEvent(self, event):
        self.events.append(event)
                
    def testNotification(self):
        patterns.Publisher().registerObserver(self.onEvent, 
            eventType='clock.second')
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
        patterns.Publisher().registerObserver(self.onEvent, 
            eventType=date.Clock.eventType(realSoonNow))
        self.clock.notify(now=realSoonNow)
        self.assertEqual(1, len(self.events))

    def testRegisterForDateChange_Midnight(self):
        patterns.Publisher().registerObserver(self.onEvent,
            eventType='clock.midnight')
        self.clock.notify(now=date.DateTime(2000,1,1,0,0,0))
        self.assertEqual(1, len(self.events))
        
    def testRegisterForDateChange_BeforeMidnight(self):
        patterns.Publisher().registerObserver(self.onEvent,
            eventType='clock.midnight')
        self.clock.notify(now=date.DateTime(2000,1,1,23,59,59))
        self.failIf(self.events)