import patterns, date

class Effort(patterns.Observable):
    def __init__(self, task, start=None, stop=None, description='', *args, **kwargs):
        super(Effort, self).__init__(*args, **kwargs)
        self._task = task
        self._start = start or date.DateTime.now()
        self._stop = stop
        self._description = description
        
    def __str__(self):
        return 'Effort(%s, %s, %s)'%(self._task, self._start, self._stop)
        
    def __getstate__(self):
        return {'_task' : self._task, '_start' : self._start, '_stop' : self._stop }
        
    def __setstate__(self, state):
        self.__dict__.update(state)
        self.notifyObservers(patterns.observer.Notification(self))
    
    def __copy__(self):
        return Effort(self._task, self._start, self._stop)
            
    def task(self):
        return self._task
        
    def duration(self, now=date.DateTime.now):
        if self._stop:
            stop = self._stop
        else:
            stop = now()
        return stop - self._start
        
    def setStart(self, startDatetime):
        self._start = startDatetime
        self.notifyObservers(patterns.observer.Notification(self))
        
    def getStart(self):
        return self._start
        
    def setStop(self, stopDatetime=None):
        if stopDatetime and stopDatetime.date() == date.Date():
            self._stop = None
        else:
            self._stop = stopDatetime or date.DateTime.now()
        self.notifyObservers(patterns.observer.Notification(self))
        
    def getStop(self):
        return self._stop
        
    def setDescription(self, description):
        self._description = description
        self.notifyObservers(patterns.observer.Notification(self))
        
    def getDescription(self):
        return self._description
        
    def __eq__(self, other):
        return self._task == other._task and self._start == other._start and \
            self._stop == other._stop
        
    def __lt__(self, other):
        return self.getStart() < other.getStart()

        
class CompositeEffort(list):
    ''' CompositeEffort is a list of efforts for one task (and maybe its children)
        and within a certain time period. '''
    
    def __init__(self, task, start, stop, efforts=None):
        self._task = task
        self._start = start
        self._stop = stop
        super(CompositeEffort, self).__init__(efforts or [])
        
    def duration(self, recursive=False):
        if recursive:
            efforts = self
        else:
            efforts = [effort for effort in self if effort.task() == self._task]
        return sum([effort.duration() for effort in efforts], date.TimeDelta())
        
    def getStart(self):
        return self._start
            
    def getStop(self):
        return self._stop
            
    def task(self):
        return self._task
            
    def __lt__(self, other):
        return self.getStart() < other.getStart() or \
            (self.getStart() == other.getStart() and \
            self.task().subject() < other.task().subject())
