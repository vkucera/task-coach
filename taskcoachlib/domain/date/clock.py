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

import wx, time
from taskcoachlib import patterns
import dateandtime, date


class Clock(object):
    __metaclass__ = patterns.Singleton
    
    def __init__(self, *args, **kwargs):
        now = kwargs.pop('now', time.time)
        super(Clock, self).__init__(*args, **kwargs)
        self._lastMidnightNotified = date.Today()
        self._timer = wx.PyTimer(self.startTheClock)
        millisecondsToNextWholeSecond = 1000-(now()%1)*1000
        if millisecondsToNextWholeSecond < 1:
            millisecondsToNextWholeSecond += 1000
        self._timer.Start(milliseconds=millisecondsToNextWholeSecond, 
                          oneShot=True)
        
    def startTheClock(self, *args, **kwargs):
        self.notify()
        self._clock = wx.PyTimer(self.notify)
        self._clock.Start(milliseconds=1000, oneShot=False)
        
    def notify(self, now=None, *args, **kwargs):
        now = now or dateandtime.DateTime.now()
        self.notifyEverySecondObservers(now)
        self.notifySpecificTimeObservers(now)
        self.notifyMidnightObservers(now)
    
    def notifyEverySecondObservers(self, now):
        patterns.Publisher().notifyObservers(patterns.Event(self,
            'clock.second', now))

    def notifySpecificTimeObservers(self, now):
        patterns.Publisher().notifyObservers(patterns.Event(self,
            Clock.eventType(now), now))

    def notifyMidnightObservers(self, now):
        today = date.Date(now.year, now.month, now.day)
        if today != self._lastMidnightNotified:
            self._lastMidnightNotified = today
            patterns.Publisher().notifyObservers(patterns.Event(self,
                'clock.midnight', now))        
        
    @staticmethod    
    def eventType(dateTime):
        return 'clock.%s'%dateTime.strftime('%Y%m%d-%H%M%S')


class ClockObserver(object):    
    def startClock(self):
        self.__clock = Clock() # make sure the clock is instantiated at least once
        patterns.Publisher().registerObserver(self.onEverySecond,
                                              eventType='clock.second')
        
    def stopClock(self):
        patterns.Publisher().removeObserver(self.onEverySecond,
                                            eventType='clock.second')

    def isClockStarted(self):
        return self.onEverySecond in \
            patterns.Publisher().observers(eventType='clock.second')
        
    def onEverySecond(self, *args, **kwargs):
        raise NotImplementedError
