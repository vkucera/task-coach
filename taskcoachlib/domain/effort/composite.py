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
from taskcoachlib.domain import date, task
from taskcoachlib.i18n import _
from taskcoachlib.gui import render
import base, effort


class BaseCompositeEffort(base.BaseEffort):
    def _inPeriod(self, effort):
        return self.getStart() <= effort.getStart() <= self.getStop()

    def __contains__(self, effort):
        return effort in self._getEfforts()

    def __getitem__(self, index):
        return self._getEfforts()[index]

    def __len__(self):
        return len(self._getEfforts())

    def durationDay(self, dayOffset):
        ''' Return the duration of this composite effort on a specific day. '''
        startOfDay = self.getStart() + date.TimeDelta(days=dayOffset)
        endOfDay = self.getStart() + date.TimeDelta(days=dayOffset+1)
        return sum([effort.duration() for effort in \
                    self._getEfforts(recursive=False) \
                    if startOfDay <= effort.getStart() <= endOfDay], 
                   date.TimeDelta())
                              
    def notifyObserversOfDurationOrEmpty(self):
        if self._getEfforts():
            duration = self.duration(recursive=True)
            patterns.Publisher().notifyObservers(patterns.Event(self,
                'effort.duration', duration))
        else:
            patterns.Publisher().notifyObservers(patterns.Event(self, 
                'effort.composite.empty'))                

    @classmethod
    def modificationEventTypes(class_):
        return [] # A composite effort cannot be 'dirty' since its contents
        # are determined by the contained efforts.


class CompositeEffort(BaseCompositeEffort):
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
        patterns.Publisher().registerObserver(self.onRevenueChanged,
            eventType='task.revenue', eventSource=task)
        patterns.Publisher().registerObserver(self.onTotalRevenueChanged,
            eventType='task.totalRevenue', eventSource=task)
        patterns.Publisher().registerObserver(self.onColorChanged,
            eventType=task.colorChangedEventType(), eventSource=task)

    def __hash__(self):
        return hash((self.task(), self.getStart()))

    def __repr__(self):
        return 'CompositeEffort(task=%s, start=%s, stop=%s, efforts=%s)'%\
            (self.task(), self.getStart(), self.getStop(),
            str([e for e in self._getEfforts()]))

    def duration(self, recursive=False):
        return sum([effort.duration() for effort in \
                    self._getEfforts(recursive)], date.TimeDelta())

    def revenue(self, recursive=False):
        return sum(effort.revenue() for effort in self._getEfforts(recursive))
    
    def __invalidateCache(self):
        for recursive in False, True:
            self.__effortCache[recursive] = \
                [effort for effort in self.task().efforts(recursive=recursive) \
                 if self._inPeriod(effort)]
                
    def __inCache(self, effort):
        return effort in self.__effortCache[True]

    def _getEfforts(self, recursive=True):
        return self.__effortCache[recursive]
        
    def isBeingTracked(self, recursive=False):
        return self.nrBeingTracked() > 0

    def nrBeingTracked(self):
        return len([effort for effort in self._getEfforts() \
            if effort.isBeingTracked()])
        
    def mayContain(self, effort):
        ''' Return whether effort would be contained in this composite effort 
            if it existed. '''
        return effort.task() == self.task() and self._inPeriod(effort)

    def onTimeSpentChanged(self, event):
        changedEffort = event.value()
        if changedEffort is None or self._inPeriod(changedEffort) or \
                                    self.__inCache(changedEffort):
            self.__invalidateCache()
            self.notifyObserversOfDurationOrEmpty()

    def onStartTracking(self, event):
        startedEffort = event.value()
        if self._inPeriod(startedEffort):
            self.__invalidateCache()
            patterns.Publisher().notifyObservers(patterns.Event(self,
                self.trackStartEventType(), startedEffort))

    def onStopTracking(self, event):
        stoppedEffort = event.value()
        if self._inPeriod(stoppedEffort):
            self.__invalidateCache()
            patterns.Publisher().notifyObservers(patterns.Event(self,
                self.trackStopEventType(), stoppedEffort))

    def onRevenueChanged(self, event):
        patterns.Publisher().notifyObservers(patterns.Event(self,
                'effort.revenue', self.revenue()))

    def onTotalRevenueChanged(self, event):
        patterns.Publisher().notifyObservers(patterns.Event(self,
                'effort.totalRevenue', self.revenue(recursive=True)))
        
    def description(self):
        effortDescriptions = [effort.description() for effort in \
                              self._getEfforts(False) if effort.description()]
        return '\n'.join(effortDescriptions)
    
    def onColorChanged(self, event):
        return # FIXME: CompositeEffort does not derive from base.Object
        patterns.Publisher().notifyObservers(patterns.Event(self,
            self.colorChangedEventType(), event.value()))
        

class CompositeEffortPerPeriod(BaseCompositeEffort):
    def __init__(self, start, stop, taskList):
        self.taskList = taskList
        super(CompositeEffortPerPeriod, self).__init__(None, start, stop)
        self.__invalidateCache()
        patterns.Publisher().registerObserver(self.onTimeSpentChanged,
            eventType=task.Task.totalTimeSpentChangedEventType())
        for eventType in self.taskList.modificationEventTypes():
            patterns.Publisher().registerObserver(self.onTaskAddedOrRemoved, eventType,
                                                  eventSource=self.taskList)

    def onTimeSpentChanged(self, event):
        changedEffort = event.value()
        if changedEffort is None or self._inPeriod(changedEffort) or \
                                    self.__inCache(changedEffort):
            self.__invalidateCache()
            self.notifyObserversOfDurationOrEmpty()

    def onTaskAddedOrRemoved(self, event):
        if any(task.efforts() for task in event.values()):
            self.__invalidateCache()
            self.notifyObserversOfDurationOrEmpty()
            
    def task(self):
        class Total(object):
            def subject(self, *args, **kwargs):
                return _('Total')
            def color(self, *args, **kwargs):
                return None
        return Total()

    def description(self, *args, **kwargs):
        return _('Total for %s')%render.dateTimePeriod(self.getStart(), self.getStop())

    def duration(self, recursive=False):
        return sum((effort.duration() for effort in self._getEfforts(recursive)),
                   date.TimeDelta())

    def revenue(self, recursive=False):
        return sum(effort.revenue() for effort in self._getEfforts())
    
    def categories(self, recursive=False):
        return [] 
        
    def isBeingTracked(self, recursive=False):
        for effort in self._getEfforts():
            if effort.isBeingTracked():
                return True
        return False

    def __repr__(self):
        return 'CompositeEffortPerPeriod(start=%s, stop=%s, efforts=%s)'%\
            (self.getStart(), self.getStop(),
            str([e for e in self._getEfforts()]))

    # Cache handling:

    def _getEfforts(self, recursive=False): # recursive argument is ignored
        return self.__effortCache
    
    def __invalidateCache(self):
        self.__effortCache = []
        for task in self.taskList:
            self.__effortCache.extend([effort for effort in task.efforts() \
                                       if self._inPeriod(effort)])
                
    def __inCache(self, effort):
        return effort in self.__effortCache
