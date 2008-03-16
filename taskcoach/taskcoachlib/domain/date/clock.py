import patterns, wx, time, dateandtime

class Clock(object):
    __metaclass__ = patterns.Singleton
    
    def __init__(self, *args, **kwargs):
        now = kwargs.pop('now', time.time)
        super(Clock, self).__init__(*args, **kwargs)
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
        for eventType in 'clock.second', Clock.eventType(now):
            patterns.Publisher().notifyObservers(patterns.Event(self,
                eventType, now))
        if now.hour == now.minute == now.second == 0:
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
