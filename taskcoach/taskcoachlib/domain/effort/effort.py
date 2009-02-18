'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2009 Frank Niessink <frank@niessink.com>
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
import base as baseeffort
    

class Effort(baseeffort.BaseEffort, base.Object):
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
            self.taskChangedEventType(), task))
        
    setParent = setTask # FIXME: I should really create a common superclass for Effort and Task
    
    @classmethod
    def taskChangedEventType(class_):
        return '%s.task'%class_
    
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
        
    @classmethod    
    def modificationEventTypes(class_):
        eventTypes = super(Effort, class_).modificationEventTypes()
        return eventTypes + [class_.taskChangedEventType(), 
                             'effort.start', 'effort.stop']
    
    