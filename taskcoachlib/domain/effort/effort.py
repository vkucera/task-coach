'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>
Copyright (C) 2008 Thomas Sonne Olesen <tpo@sonnet.dk>

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

from taskcoachlib import patterns
from taskcoachlib.domain import date, base


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

    def subject(self, *args, **kwargs):
        return self._task.subject(*args, **kwargs)

    def categories(self, recursive=False):
        return self._task.categories(recursive)

    @classmethod
    def trackStartEventType(class_):
        return 'effort.track.start' 
        # We don't use '%s.effort...'%class_ because we need Effort and 
        # CompositeEffort to use the same event types. This is needed to make
        # UpdatePerSecondViewer work regardless whether EffortViewer is in
        # aggregate mode or not.
    
    @classmethod
    def trackStopEventType(class_):
        return 'effort.track.stop'
    

class Effort(EffortBase, base.Object):
    def __init__(self, task=None, start=None, stop=None, *args, **kwargs):
        super(Effort, self).__init__(task, start or date.DateTime.now(), stop, 
            *args, **kwargs)

    def setTask(self, task):
        if self._task is None: 
            # We haven't been fully initialised yet, so allow setting of the
            # task, without notifying observers. Also, don't call addEffort()
            # on the new task, because we assume setTask was invoked by the
            # new task itself.
            self._task = task
            return
        if task in (self._task, None): 
            # command.PasteCommand may try to set the parent to None
            return
        self._task.removeEffort(self)
        self._task = task
        self._task.addEffort(self)
        patterns.Publisher().notifyObservers(patterns.Event(self, 
            'effort.task', task))

    setParent = setTask # FIXME: I should really create a common superclass for Effort and Task
    
    def __str__(self):
        return 'Effort(%s, %s, %s)'%(self._task, self._start, self._stop)
    
    __repr__ = __str__
        
    def __getstate__(self):
        state = super(Effort, self).__getstate__()
        state.update(dict(task=self._task, start=self._start,
            stop=self._stop))
        return state

    def __setstate__(self, state):
        super(Effort, self).__setstate__(state)
        self.setTask(state['task'])
        self.setStart(state['start'])
        self.setStop(state['stop'])

    def __getcopystate__(self):
        state = super(Effort, self).__getcopystate__()
        state.update(dict(task=self._task, start=self._start,
            stop=self._stop))
        return state
   
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
        self.task().notifyObserversOfTimeSpentChange(self)
        patterns.Publisher().notifyObservers(patterns.Event(self,
            'effort.start', self._start))
        patterns.Publisher().notifyObservers(patterns.Event(self,
            'effort.duration', self.duration()))
            
    def setStop(self, newStop=None):
        if newStop is None:
            newStop = date.DateTime.now()
        elif newStop == date.DateTime.max:
            newStop = None
        if newStop != self._stop:
            previousStop = self._stop
            self._stop = newStop
            self.notifyStopOrStartTracking(previousStop, newStop)
            self.task().notifyObserversOfTimeSpentChange(self)
            patterns.Publisher().notifyObservers(patterns.Event(self, 
                'effort.stop', newStop))
            patterns.Publisher().notifyObservers(patterns.Event(self,
                'effort.duration', self.duration()))
            if self.task().hourlyFee():
                self.notifyObserversOfRevenueChange()
                    
    def notifyStopOrStartTracking(self, previousStop, newStop):
        eventType = ''
        if newStop == None:
            eventType = self.trackStartEventType()
            self.task().notifyObserversOfStartTracking(self)
        elif previousStop == None:
            eventType = self.trackStopEventType()
            self.task().notifyObserversOfStopTracking(self)
        if eventType:
            patterns.Publisher().notifyObservers(patterns.Event(self, 
                eventType))

    def isBeingTracked(self, recursive=False):
        return self._stop is None

    def revenue(self):
        task = self.task()
        variableRevenue = self.duration().hours() * task.hourlyFee()
        if task.timeSpent().hours() > 0:
            fixedRevenue = self.duration().hours() / \
                task.timeSpent().hours() * task.fixedFee()
        else:
            fixedRevenue = 0
        return variableRevenue + fixedRevenue
    
    def notifyObserversOfRevenueChange(self):
        self.notifyObservers(patterns.Event(self, 'effort.revenue', 
            self.revenue()))
    

class CompositeEffort(EffortBase):
    ''' CompositeEffort is a lazy list (but cached) of efforts for one task
        (and its children) and within a certain time period. The task, start 
        of time period and end of time period need to be provided when
        initializing the CompositeEffort and cannot be changed
        afterwards. '''
    
    def __init__(self, task, start, stop):
        super(CompositeEffort, self).__init__(task, start, stop)
        self.__effortCache = {} # {True: [efforts recursively], False: [efforts]}
        self.__invalidateCache()
        patterns.Publisher().registerObserver(self.onTimeSpentChanged,
            eventType=task.totalTimeSpentChangedEventType(), eventSource=task)
        patterns.Publisher().registerObserver(self.onStartTracking,
            eventType=task.trackStartEventType(), eventSource=task)
        patterns.Publisher().registerObserver(self.onStopTracking,
            eventType=task.trackStopEventType(), eventSource=task)
        patterns.Publisher().registerObserver(self.onHourlyFeeChanged,
            eventType=task.hourlyFeeChangedEventType(), eventSource=task)
        patterns.Publisher().registerObserver(self.onChildHourlyFeeChanged,
            eventType=task.totalHourlyFeeChangedEventType(), eventSource=task)
        patterns.Publisher().registerObserver(self.onColorChanged,
            eventType=task.colorChangedEventType(), eventSource=task)

    def __hash__(self):
        return hash((self.task(), self.getStart()))

    def __contains__(self, effort):
        return effort in self.__getEfforts(recursive=True)

    def __getitem__(self, index):
        return self.__getEfforts(recursive=True)[index]

    def __len__(self):
        return len(self.__getEfforts(recursive=True))

    def __repr__(self):
        return 'CompositeEffort(task=%s, start=%s, stop=%s, efforts=%s)'%\
            (self.task(), self.getStart(), self.getStop(),
            str([e for e in self.__getEfforts(recursive=True)]))

    def duration(self, recursive=False):
        return sum([effort.duration() for effort in \
                    self.__getEfforts(recursive)], date.TimeDelta())

    def durationDay(self, dayOffset, recursive=False):
        ''' Return the duration of this composite effort on a specific day. '''
    	startOfDay = self.getStart() + date.TimeDelta(days=dayOffset)
    	endOfDay = self.getStart() + date.TimeDelta(days=dayOffset+1)
        return sum([effort.duration() for effort in \
                    self.__getEfforts(recursive) \
                    if startOfDay <= effort.getStart() <= endOfDay], 
                   date.TimeDelta())
                              
    def revenue(self, recursive=False):
        return sum(effort.revenue() for effort in self.__getEfforts(recursive))
    
    def __invalidateCache(self):
        for recursive in False, True:
            self.__effortCache[recursive] = \
                [effort for effort in self.task().efforts(recursive=recursive) \
                 if self.__inPeriod(effort)]
                
    def __inCache(self, effort):
        return effort in self.__effortCache[True]

    def __getEfforts(self, recursive):
        return self.__effortCache[recursive]
        
    def isBeingTracked(self, recursive=False):
        return self.nrBeingTracked() > 0

    def nrBeingTracked(self):
        return len([effort for effort in self.__getEfforts(recursive=True) \
            if effort.isBeingTracked()])
        
    def mayContain(self, effort):
        ''' Return whether effort would be contained in this composite effort 
            if it existed. '''
        return effort.task() == self.task() and self.__inPeriod(effort)

    def __inPeriod(self, effort):
        return self.getStart() <= effort.getStart() <= self.getStop()

    def onTimeSpentChanged(self, event):
        changedEffort = event.value()
        if changedEffort is None or self.__inPeriod(changedEffort) or \
                                    self.__inCache(changedEffort):
            self.__invalidateCache()
            duration = self.duration(recursive=True)
            patterns.Publisher().notifyObservers(patterns.Event(self,
                'effort.duration', duration))
            if not self.__getEfforts(recursive=True):
                patterns.Publisher().notifyObservers(patterns.Event(self, 
                    'effort.composite.empty'))

    def onStartTracking(self, event):
        startedEffort = event.value()
        if self.__inPeriod(startedEffort):
            self.__invalidateCache()
            patterns.Publisher().notifyObservers(patterns.Event(self,
                self.trackStartEventType(), startedEffort))

    def onStopTracking(self, event):
        stoppedEffort = event.value()
        if self.__inPeriod(stoppedEffort):
            self.__invalidateCache()
            patterns.Publisher().notifyObservers(patterns.Event(self,
                self.trackStopEventType(), stoppedEffort))

    def onHourlyFeeChanged(self, event):
        patterns.Publisher().notifyObservers(patterns.Event(self,
                'effort.revenue', self.revenue()))

    def onChildHourlyFeeChanged(self, event):
        patterns.Publisher().notifyObservers(patterns.Event(self,
                'effort.totalRevenue', self.revenue(recursive=True)))
                
    def description(self):
        effortDescriptions = [effort.description() for effort in \
                              self.__getEfforts(False) if effort.description()]
        return '\n'.join(effortDescriptions)
    
    def onColorChanged(self, event):
        patterns.Publisher().notifyObservers(patterns.Event(self,
            Effort.colorChangedEventType(), event.value()))