import patterns
import domain.date as date

class EffortBase(patterns.Observable):
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


class Effort(EffortBase):
    def __init__(self, task, start=None, stop=None, description='', 
            *args, **kwargs):
        self._description = description
        super(Effort, self).__init__(task, start or date.DateTime.now(), stop, 
            *args, **kwargs)

    def setTask(self, task):
        if task in [self._task, None]: 
            # command.PasteCommand may try to set the parent to None
            return
        self._task.removeEffort(self)
        self._task = task
        self._task.addEffort(self)
        self.notifyObservers(patterns.Event(self, 'effort.task', task))

    setParent = setTask # FIXME: I should really create a common superclass for Effort and Task
    
    def __str__(self):
        return 'Effort(%s, %s, %s)'%(self._task, self._start, self._stop)
    
    __repr__ = __str__
        
    def __getstate__(self):
        return dict(task=self._task, start=self._start,
            stop=self._stop, description=self._description)
        
    def __setstate__(self, state):
        self.setTask(state['task'])
        self.setStart(state['start'])
        self.setStop(state['stop'])
        self.setDescription(state['description'])
   
    def copy(self):
        return Effort(self._task, self._start, self._stop, self._description) 

    def duration(self, now=date.DateTime.now):
        if self._stop:
            stop = self._stop
        else:
            stop = now()
        return stop - self._start
        
    def setStart(self, startDatetime):
        if startDatetime == self._start:
            return
        self._start = startDatetime
        self.notifyObservers(patterns.Event(self, 'effort.start', self._start))

    def setStop(self, newStop=None):
        if newStop is None:
            newStop = date.DateTime.now()
        elif newStop == date.DateTime.max:
            newStop = None
        if newStop != self._stop:
            previousStop = self._stop
            self._stop = newStop
            self.notifyObservers(patterns.Event(self, 'effort.stop', newStop))
            self.notifyStopOrStartTracking(previousStop, newStop)

    def notifyStopOrStartTracking(self, previousStop, newStop):
        eventType = ''
        if newStop == None:
            eventType = 'effort.track.start'
        elif previousStop == None:
            eventType = 'effort.track.stop'
        if eventType:
            self.notifyObservers(patterns.Event(self, eventType))

    def setDescription(self, description):
        self._description = description
        self.notifyObservers(patterns.Event(self, 'effort.description',
            description))
        
    def getDescription(self):
        return self._description

    def revenue(self):
        variableRevenue = self.duration().hours() * self.task().hourlyFee()
        if self.task().timeSpent().hours() > 0:
            fixedRevenue = self.duration().hours() / self.task().timeSpent().hours() * self.task().fixedFee()
        else:
            fixedRevenue = 0
        return variableRevenue + fixedRevenue
        
        
class CompositeEffort(EffortBase, patterns.List):
    ''' CompositeEffort is a list of efforts for one task (and maybe its 
        children) and within a certain time period. '''
    
    def __init__(self, task, start, stop, efforts=None):
        super(CompositeEffort, self).__init__(task, start, stop, efforts or [])
        
    def duration(self, recursive=False):
        return sum([effort.duration() for effort in self.__getEfforts(recursive)], 
                   date.TimeDelta())
                              
    def revenue(self, recursive=False):
        return sum(effort.revenue() for effort in self.__getEfforts(recursive))
    
    def __getEfforts(self, recursive):
        if recursive:
            return self
        else:
            return [effort for effort in self if effort.task() == self._task]
        
    def __eq__(self, other):
        return self is other
