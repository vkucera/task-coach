'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>

Task Coach is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Task Coach is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

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
