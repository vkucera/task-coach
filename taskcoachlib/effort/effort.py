import patterns, date

class EffortBase(object):
    def __init__(self, task, start, stop, *args, **kwargs):
        self._task = task
        self._start = start
        self._stop = stop
        super(EffortBase, self).__init__(*args, **kwargs)
      
    def task(self):
        return self._task

    def getStart(self):
        return self._start

    def getStop(self):
        return self._stop

    def __lt__(self, other):
        return self.getStart() > other.getStart() or \
            (self.getStart() == other.getStart() and \
            self.task().subject() < other.task().subject())

    def __eq__(self, other):
        return self._task == other._task and self._start == other._start and \
            self._stop == other._stop
                  

class Effort(EffortBase, patterns.Observable, date.ClockObserver):
    def __init__(self, task, start=None, stop=None, description='', *args, **kwargs):
        self._description = description
        super(Effort, self).__init__(task, start or date.DateTime.now(), stop, *args, **kwargs)
        if self._stop == None:
            self.startClock()

    def setTask(self, task):
        if self in self._task.efforts():
            self._task.removeEffort(self)
        self._task = task
        self._task.addEffort(self)

    def __str__(self):
        return 'Effort(%s, %s, %s)'%(self._task, self._start, self._stop)
        
    def __getstate__(self):
        return {'_task' : self._task, '_start' : self._start, '_stop' : self._stop }
        
    def __setstate__(self, state):
        self.__dict__.update(state)
        self.notifyObservers(patterns.Notification(self, changeNeedsSave=True))
    
    def __copy__(self):
        return Effort(self._task, self._start, self._stop)            
       
    def duration(self, now=date.DateTime.now):
        if self._stop:
            stop = self._stop
        else:
            stop = now()
        return stop - self._start
        
    def setStart(self, startDatetime):
        self._start = startDatetime
        self.notifyObservers(patterns.Notification(self, changeNeedsSave=True))       
       
    def setStop(self, stopDatetime=None):
        if stopDatetime is None:
            self._stop = date.DateTime.now()
        elif stopDatetime == date.DateTime.max:
            self._stop = None
        else:
            self._stop = stopDatetime
        if self._stop == None and not self.isClockStarted():
            self.startClock()
        elif self._stop != None and self.isClockStarted():
            self.stopClock()
        self.notifyObservers(patterns.Notification(self, changeNeedsSave=True))        
        
    def setDescription(self, description):
        self._description = description
        self.notifyObservers(patterns.Notification(self, changeNeedsSave=True))
        
    def getDescription(self):
        return self._description

    def onEverySecond(self, *args, **kwargs):
        self.notifyObservers(patterns.Notification(self))
        
        
class CompositeEffort(EffortBase, list):
    ''' CompositeEffort is a list of efforts for one task (and maybe its children)
        and within a certain time period. '''
    
    def __init__(self, task, start, stop, efforts=None):
        super(CompositeEffort, self).__init__(task, start, stop, efforts or [])
        
    def duration(self, recursive=False):
        if recursive:
            efforts = self
        else:
            efforts = [effort for effort in self if effort.task() == self._task]
        return sum([effort.duration() for effort in efforts], date.TimeDelta())
                              
