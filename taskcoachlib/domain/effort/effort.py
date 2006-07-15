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
        return self.getStart() < other.getStart() or \
            (self.getStart() == other.getStart() and \
            self.task().subject() < other.task().subject())

    def __gt__(self, other):
        return other < self


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
        self.notifyObservers(patterns.Event(self, 'effort.duration',
            self.duration()))

    def setStop(self, newStop=None):
        if newStop is None:
            newStop = date.DateTime.now()
        elif newStop == date.DateTime.max:
            newStop = None
        if newStop != self._stop:
            previousStop = self._stop
            self._stop = newStop
            self.notifyObservers(patterns.Event(self, 'effort.stop', newStop))
            self.notifyObservers(patterns.Event(self, 'effort.duration', 
                self.duration()))
            self.notifyStopOrStartTracking(previousStop, newStop)

    def notifyStopOrStartTracking(self, previousStop, newStop):
        eventType = ''
        if newStop == None:
            eventType = 'effort.track.start'
        elif previousStop == None:
            eventType = 'effort.track.stop'
        if eventType:
            self.notifyObservers(patterns.Event(self, eventType))

    def isBeingTracked(self):
        return self._stop is None

    def setDescription(self, description):
        self._description = description
        self.notifyObservers(patterns.Event(self, 'effort.description',
            description))
        
    def getDescription(self):
        return self._description

    def revenue(self):
        task = self.task()
        variableRevenue = self.duration().hours() * task.hourlyFee()
        if task.timeSpent().hours() > 0:
            fixedRevenue = self.duration().hours() / \
                task.timeSpent().hours() * task.fixedFee()
        else:
            fixedRevenue = 0
        return variableRevenue + fixedRevenue
        
        
class CompositeEffort(EffortBase, patterns.List):
    ''' CompositeEffort is a list of efforts for one task (and its 
        children) and within a certain time period. The task, start of
        time period and end of time period need to be provided when
        initializing the CompositeEffort and cannot be changed
        afterwards. '''
    
    def __init__(self, task, start, stop):
        super(CompositeEffort, self).__init__(task, start, stop)
        self.addTask(task)

    def __hash__(self):
        return hash((self.task(), self.getStart()))

    def __repr__(self):
        return 'CompositeEffort(%s, %s)'%(self.task(), str([e for e in self]))

    def duration(self, recursive=False):
        return sum([effort.duration() for effort in \
                    self.__getEfforts(recursive)], date.TimeDelta())
                              
    def revenue(self, recursive=False):
        return sum(effort.revenue() for effort in self.__getEfforts(recursive))
    
    def __getEfforts(self, recursive):
        if recursive:
            return self
        else:
            return [effort for effort in self if effort.task() == self._task]
        
    def __eq__(self, other):
        return self is other

    def isBeingTracked(self):
        return True in [effort.isBeingTracked() for effort in self]

    # event handlers:
    
    def onAddChild(self, event):
        self.addTask(event.value())

    def onRemoveChild(self, event):
        self.removeTask(event.value())

    def onAddEffort(self, event):
        self.addNewEffortIfInPeriod(event.value())

    def onRemoveEffort(self, event):
        self.removeDeletedEffortIfInPeriod(event.value())
    
    def onStartTracking(self, event):
        self.notifyObservers(patterns.Event(self, 'effort.track.start'))

    def onStopTracking(self, event):
        self.notifyObservers(patterns.Event(self, 'effort.track.stop'))

    def onChangeStart(self, event):
        effort = event.source()
        inPeriod = self.inPeriod(effort)
        if inPeriod and effort not in self:
            self.addEffort(effort)
        elif not inPeriod and effort in self:
            self.removeEffort(effort)
        
    def onChangeDuration(self, event):
        self.notifyObservers(patterns.Event(self, 'effort.duration',
            self.duration()))

    # process changes:

    def inPeriod(self, effort):
        return self.getStart() <= effort.getStart() <= self.getStop()

    def addNewEffortIfInPeriod(self, effort):
        if self.inPeriod(effort):
            self.addEffort(effort)
        effort.registerObserver(self.onChangeStart, 'effort.start')

    def removeDeletedEffortIfInPeriod(self, effort):
        if effort in self:
            self.removeEffort(effort)
        effort.removeObserver(self.onChangeStart)

    def addEffort(self, effort):
        wasTracking = self.isBeingTracked()
        self.append(effort) 
        effort.registerObserver(self.onStartTracking, 'effort.track.start') 
        effort.registerObserver(self.onStopTracking, 'effort.track.stop') 
        effort.registerObserver(self.onChangeDuration, 'effort.duration') 
        self.notifyObservers(patterns.Event(self, 'effort.duration', 
            self.duration()))
        if effort.isBeingTracked() and not wasTracking:
            self.notifyObservers(patterns.Event(self, 'effort.track.start'))

    def removeEffort(self, effort):
        wasTracking = self.isBeingTracked()
        self.remove(effort)
        effort.removeObservers(self.onStartTracking, self.onStopTracking, 
            self.onChangeDuration) 
        self.notifyObservers(patterns.Event(self, 'effort.duration', 
            self.duration()))
        if wasTracking and not self.isBeingTracked():
            self.notifyObservers(patterns.Event(self, 'effort.track.stop'))
        if len(self) == 0:
            self.notifyObservers(patterns.Event(self, 'list.empty'))

    def addTask(self, task):
        for child in [task] + task.children(recursive=True):
            child.registerObserver(self.onAddChild, 'task.child.add')
            child.registerObserver(self.onRemoveChild, 'task.child.remove')
            child.registerObserver(self.onAddEffort, 'task.effort.add')
            child.registerObserver(self.onRemoveEffort, 'task.effort.remove')
        for effort in task.efforts(recursive=True):
            self.addNewEffortIfInPeriod(effort)

    def removeTask(self, task):
        for child in [task] + task.children(recursive=True):
            child.removeObservers(self.onAddChild, self.onRemoveChild, 
                self.onAddEffort, self.onRemoveEffort)
        for effort in task.efforts(recursive=True):
            self.removeDeletedEffortIfInPeriod(effort)
