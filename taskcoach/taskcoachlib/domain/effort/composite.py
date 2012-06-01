'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2012 Task Coach developers <developers@taskcoach.org>
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

from taskcoachlib import render
from taskcoachlib.domain import date
from taskcoachlib.i18n import _
from taskcoachlib.thirdparty.pubsub import pub
import base


class BaseCompositeEffort(base.BaseEffort):  # pylint: disable-msg=W0223        
    def parent(self):
        # Composite efforts don't have a parent.
        return None
        
    def _inPeriod(self, effort):
        return self.getStart() <= effort.getStart() <= self.getStop()

    def __contains__(self, effort):
        return effort in self._getEfforts()

    def __getitem__(self, index):
        return self._getEfforts()[index]

    def __len__(self):
        return len(self._getEfforts())
    
    def _getEfforts(self):
        raise NotImplementedError

    def markDirty(self):
        pass  # CompositeEfforts cannot be dirty
    
    def duration(self, recursive=False):
        return sum((effort.duration() for effort in \
                    self._getEfforts(recursive)), date.TimeDelta())

    def isBeingTracked(self, recursive=False):  # pylint: disable-msg=W0613
        return any(effort.isBeingTracked() for effort in self._getEfforts())

    def durationDay(self, dayOffset):
        ''' Return the duration of this composite effort on a specific day. '''
        startOfDay = self.getStart() + date.TimeDelta(days=dayOffset)
        endOfDay = self.getStart() + date.TimeDelta(days=dayOffset + 1)
        return sum((effort.duration() for effort in \
                    self._getEfforts(recursive=False) \
                    if startOfDay <= effort.getStart() <= endOfDay), 
                   date.TimeDelta())
                              
    def notifyObserversOfDurationOrEmpty(self):
        if self._getEfforts():
            self.sendDurationChangedMessage()
        else:
            pub.sendMessage(self.compositeEmptyEventType(), sender=self)
        
    @classmethod
    def compositeEmptyEventType(class_):
        return 'pubsub.effort.composite.empty'
        
    @classmethod
    def modificationEventTypes(class_):
        return []  # A composite effort cannot be 'dirty' since its contents
        # are determined by the contained efforts.

    def onTimeSpentChanged(self, newValue, sender):  # pylint: disable-msg=W0613
        self._invalidateCache()
        self.notifyObserversOfDurationOrEmpty()

    def onRevenueChanged(self, newValue, sender):  # pylint: disable-msg=W0613
        self.sendRevenueChangedMessage()
           
    def revenue(self, recursive=False):
        raise NotImplementedError  # pragma: no cover
    
    def _invalidateCache(self):
        raise NotImplementedError  # pragma: no cover
    

class CompositeEffort(BaseCompositeEffort):
    ''' CompositeEffort is a lazy list (but cached) of efforts for one task
        (and its children) and within a certain time period. The task, start 
        of time period and end of time period need to be provided when
        initializing the CompositeEffort and cannot be changed
        afterwards. '''
    
    def __init__(self, task, start, stop):  # pylint: disable-msg=W0621
        super(CompositeEffort, self).__init__(task, start, stop)
        self.__hash_value = hash((task, start))
        # Effort cache: {True: [efforts recursively], False: [efforts]}
        self.__effortCache = dict()  
        self._invalidateCache()
        '''
        FIMXE! CompositeEffort does not derive from base.Object
        patterns.Publisher().registerObserver(self.onAppearanceChanged,
            eventType=task.appearanceChangedEventType(), eventSource=task)
        '''

    def __hash__(self):
        return self.__hash_value

    def __repr__(self):
        return 'CompositeEffort(task=%s, start=%s, stop=%s, efforts=%s)' % \
            (self.task(), self.getStart(), self.getStop(),
            str([e for e in self._getEfforts()]))

    def addEffort(self, anEffort):
        assert self._inPeriod(anEffort)
        self.__effortCache.setdefault(True, []).append(anEffort)
        if anEffort.task() == self.task():
            self.__effortCache.setdefault(False, []).append(anEffort)
            
    def revenue(self, recursive=False):
        return sum(effort.revenue() for effort in self._getEfforts(recursive))
    
    def _invalidateCache(self):
        self.__effortCache = dict()
                
    def _getEfforts(self, recursive=True):  # pylint: disable-msg=W0221
        try:
            return self.__effortCache[recursive]
        except KeyError:
            result = self.__effortCache[recursive] = \
                [effort for effort in self.task().efforts(recursive=recursive) \
                 if self._inPeriod(effort)]
            return result
        
    def mayContain(self, effort):
        ''' Return whether effort would be contained in this composite effort 
            if it existed. '''
        return effort.task() == self.task() and self._inPeriod(effort)
            
    def description(self):
        effortDescriptions = [effort.description() for effort in \
                              self._getEfforts(False) if effort.description()]
        return '\n'.join(effortDescriptions)
    
    def onAppearanceChanged(self, event):    
        return  # FIXME: CompositeEffort does not derive from base.Object
        #patterns.Event(self.appearanceChangedEventType(), self, event.value()).send()


class CompositeEffortPerPeriod(BaseCompositeEffort):
    def __init__(self, start, stop, taskList, initialEffort=None):
        self.taskList = taskList
        super(CompositeEffortPerPeriod, self).__init__(None, start, stop)
        if initialEffort:
            assert self._inPeriod(initialEffort)
            self.__effortCache = [initialEffort]
        else:
            self._invalidateCache()
            
    def addEffort(self, anEffort):
        assert self._inPeriod(anEffort)
        if anEffort not in self.__effortCache:
            self.__effortCache.append(anEffort)

    def task(self):
        class Total(object):
            # pylint: disable-msg=W0613
            def subject(self, *args, **kwargs): 
                return _('Total')
            
            def foregroundColor(self, *args, **kwargs):
                return None
            
            def backgroundColor(self, *args, **kwargs):
                return None
            
            def font(self, *args, **kwargs):
                return None
        
        return Total()

    def isTotal(self):
        return True

    def description(self, *args, **kwargs):  # pylint: disable-msg=W0613
        return _('Total for %s') % render.dateTimePeriod(self.getStart(), 
                                                         self.getStop())

    def revenue(self, recursive=False):  # pylint: disable-msg=W0613
        return sum(effort.revenue() for effort in self._getEfforts())

    def categories(self, *args, **kwargs):
        return [] 
        
    def __repr__(self):
        return 'CompositeEffortPerPeriod(start=%s, stop=%s, efforts=%s)' % \
            (self.getStart(), self.getStop(),
            str([e for e in self._getEfforts()]))

    # Cache handling:

    def _getEfforts(self, recursive=False):  # pylint: disable-msg=W0613,W0221
        if self.__effortCache is None:
            self.__effortCache = []
            for eachTask in self.taskList:
                self.__effortCache.extend([effort for effort in eachTask.efforts() \
                                           if self._inPeriod(effort)])
        return self.__effortCache
    
    def _invalidateCache(self):
        self.__effortCache = None
