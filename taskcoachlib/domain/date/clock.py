import patterns, wx, time
import dateandtime

class Clock(patterns.Observable):
    __metaclass__ = patterns.Singleton
    
    def __init__(self, *args, **kwargs):
        now = kwargs.pop('now', time.time)
        super(Clock, self).__init__(*args, **kwargs)
        self._timer = wx.PyTimer(self.startTheClock)
        millisecondsToNextWholeSecond = 1000-(now()%1)*1000
        if millisecondsToNextWholeSecond < 1:
            millisecondsToNextWholeSecond += 1000
        self._timer.Start(milliseconds=millisecondsToNextWholeSecond, oneShot=True)
        
    def startTheClock(self, *args, **kwargs):
        self.notify()
        self._clock = wx.PyTimer(self.notify)
        self._clock.Start(milliseconds=1000, oneShot=False)
        
    def notify(self, now=None, *args, **kwargs):
        self.notifyObservers(patterns.Event(self, 'clock.second'))
        now = now or dateandtime.DateTime.now()
        now = now.replace(microsecond=0)
        self.notifyObservers(patterns.Event(self, now))
   
    def registerObserver(self, callback, time):
        if time != 'clock.second':
            time = time.replace(microsecond=0)
        super(Clock, self).registerObserver(callback, time)
        
        
class ClockObserver(object):    
    def startClock(self):
        Clock().registerObserver(self.onEverySecond, 'clock.second')
        
    def stopClock(self):
        Clock().removeObserver(self.onEverySecond)

    def isClockStarted(self):
        return self.onEverySecond in Clock().observers('clock.second')
        
    def XonEverySecond(self, *args, **kwargs):
        raise NotImplementedError
