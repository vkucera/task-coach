'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2012 Task Coach developers <developers@taskcoach.org>

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
from taskcoachlib.thirdparty.pubsub import pub
import composite
import effortlist
import effort


class EffortAggregator(patterns.SetDecorator, 
                       effortlist.EffortUICommandNamesMixin):
    ''' This class observes an TaskList and aggregates the individual effort
        records to CompositeEfforts, e.g. per day or per week. Whenever a 
        CompositeEffort becomes empty, for example because effort is deleted,
        it sends an 'empty' event so that the aggregator can remove the
        (now empty) CompositeEffort from itself. '''
        
    def __init__(self, *args, **kwargs):
        self.__composites = {}
        self.__trackedComposites = set()
        aggregation = kwargs.pop('aggregation')
        assert aggregation in ('day', 'week', 'month')
        aggregation = aggregation.capitalize()
        self.startOfPeriod = getattr(date.DateTime, 'startOf%s' % aggregation)
        self.endOfPeriod = getattr(date.DateTime, 'endOf%s' % aggregation)
        super(EffortAggregator, self).__init__(*args, **kwargs)
        pub.subscribe(self.onCompositeEmpty, 
                      composite.CompositeEffort.compositeEmptyEventType())
        pub.subscribe(self.onEffortAddedToTask, 
                      task.Task.effortsChangedEventType())
        patterns.Publisher().registerObserver(self.onChildAddedToTask,
            eventType=task.Task.addChildEventType())
        for eventType in self.observable().modificationEventTypes():
            patterns.Publisher().registerObserver(self.onTaskAddedOrRemoved, eventType,
                                                  eventSource=self.observable())
        pub.subscribe(self.onEffortStartChanged, 
                      effort.Effort.startChangedEventType())
        pub.subscribe(self.onTimeSpentChanged,
                      task.Task.timeSpentChangedEventType())
        pub.subscribe(self.onRevenueChanged,
                      task.Task.hourlyFeeChangedEventType())
    
    def extend(self, efforts):  # pylint: disable-msg=W0221
        for effort in efforts:
            effort.task().addEffort(effort)

    def removeItems(self, efforts):  # pylint: disable-msg=W0221
        for effort in efforts:
            effort.task().removeEffort(effort)
            
    @patterns.eventSource
    def extendSelf(self, tasks, event=None):
        ''' extendSelf is called when an item is added to the observed
            list. The default behavior of extendSelf is to add the item
            to the observing list (i.e. this list) unchanged. We override 
            the default behavior to first get the efforts from the task
            and then group the efforts by time period. '''
        newComposites = []
        for task in tasks:  # pylint: disable-msg=W0621
            newComposites.extend(self.createComposites(task, task.efforts()))
        self.__extendSelfWithComposites(newComposites, event=event)
        
    @patterns.eventSource
    def __extendSelfWithComposites(self, newComposites, event=None):
        ''' Add composites to the aggregator. '''
        super(EffortAggregator, self).extendSelf(newComposites, event=event)
        for newComposite in newComposites:
            if newComposite.isBeingTracked():
                self.__trackedComposites.add(newComposite)
                pub.sendMessage(effort.Effort.trackingChangedEventType(),
                                newValue=True, sender=newComposite)

    @patterns.eventSource
    def removeItemsFromSelf(self, tasks, event=None):
        ''' removeItemsFromSelf is called when an item is removed from the 
            observed list. The default behavior of removeItemsFromSelf is to 
            remove the item from the observing list (i.e. this list)
            unchanged. We override the default behavior to remove the 
            tasks' efforts from the CompositeEfforts they are part of. '''
        compositesToRemove = []
        for task in tasks:  # pylint: disable-msg=W0621
            compositesToRemove.extend(self.compositesToRemove(task))
        self.__removeCompositesFromSelf(compositesToRemove, event=event)
         
    @patterns.eventSource
    def __removeCompositesFromSelf(self, compositesToRemove, event=None):
        ''' Remove composites from the aggregator. '''
        self.__trackedComposites.difference_update(set(compositesToRemove))
        super(EffortAggregator, self).removeItemsFromSelf(compositesToRemove, 
                                                          event=event)
        
    def onTaskAddedOrRemoved(self, event):
        if any(task.efforts() for task in event.values()):
            for eachComposite in self.getCompositesForTask(None):
                eachComposite._invalidateCache()
                eachComposite.notifyObserversOfDurationOrEmpty()
            
    def onEffortAddedToTask(self, newValue, oldValue, sender):
        if sender not in self.observable():
            return
        newComposites = []
        effortsAdded = [effort for effort in newValue if effort not in oldValue]
        newComposites.extend(self.createComposites(sender, effortsAdded))
        self.__extendSelfWithComposites(newComposites)
        
    def onChildAddedToTask(self, event):
        newComposites = []
        for task in event.sources():  # pylint: disable-msg=W0621
            if task in self.observable():
                child = event.value(task)
                newComposites.extend(self.createComposites(task,
                    child.efforts(recursive=True)))
        self.__extendSelfWithComposites(newComposites)

    def onCompositeEmpty(self, sender):
        # pylint: disable-msg=W0621
        if sender not in self:
            return
        key = self.keyForComposite(sender)
        if key in self.__composites:
            # A composite may already have been removed, e.g. when a
            # parent and child task have effort in the same period
            del self.__composites[key]
        self.__removeCompositesFromSelf([sender])
        
    def onEffortStartChanged(self, newValue, sender):  # pylint: disable-msg=W0613
        newComposites = []
        key = self.keyForEffort(sender)
        task = sender.task()  # pylint: disable-msg=W0621
        if (task in self.observable()) and (key not in self.__composites):
            newComposites.extend(self.createComposites(task, [sender]))
        self.__extendSelfWithComposites(newComposites)
            
    def onTimeSpentChanged(self, newValue, sender):
        for affectedComposite in self.getCompositesForTask(sender):
            isTracked = affectedComposite.isBeingTracked()
            wasTracked = affectedComposite in self.__trackedComposites
            if isTracked and not wasTracked:
                self.__trackedComposites.add(affectedComposite)
                pub.sendMessage(effort.Effort.trackingChangedEventType(),
                                newValue=True, sender=affectedComposite)
            elif not isTracked and wasTracked:
                self.__trackedComposites.remove(affectedComposite)
                pub.sendMessage(effort.Effort.trackingChangedEventType(),
                                newValue=False, sender=affectedComposite)
            affectedComposite.onTimeSpentChanged(newValue, sender)
            
    def onRevenueChanged(self, newValue, sender):
        for affectedComposite in self.getCompositesForTask(sender):
            affectedComposite.onRevenueChanged(newValue, sender)
            
    def getCompositesForTask(self, theTask):
        return [eachComposite for eachComposite in self \
                if theTask == eachComposite.task() or \
                (eachComposite.task().__class__.__name__ == 'Total' and \
                 theTask is not None and \
                 any([effort in eachComposite for effort in theTask.efforts()]))]
        
    def createComposites(self, task, efforts):  # pylint: disable-msg=W0621
        newComposites = []
        for effort in efforts:
            newComposites.extend(self.createCompositesForTask(effort, task))
            newComposites.extend(self.createCompositeForPeriod(effort))
        return newComposites

    def createCompositesForTask(self, anEffort, task):  # pylint: disable-msg=W0621
        newComposites = []
        for eachTask in [task] + task.ancestors():
            key = self.keyForEffort(anEffort, eachTask)
            if key in self.__composites:
                self.__composites[key].addEffort(anEffort)
                continue
            newComposite = composite.CompositeEffort(*key)  # pylint: disable-msg=W0142
            newComposite.addEffort(anEffort)
            self.__composites[key] = newComposite
            newComposites.append(newComposite)
        return newComposites
    
    def createCompositeForPeriod(self, anEffort):
        key = self.keyForPeriod(anEffort)
        if key in self.__composites:
            self.__composites[key].addEffort(anEffort)
            return []
        newCompositePerPeriod = composite.CompositeEffortPerPeriod(key[0], key[1], self.observable(), anEffort)
        self.__composites[key] = newCompositePerPeriod
        return [newCompositePerPeriod]

    def compositesToRemove(self, task):  # pylint: disable-msg=W0621
        efforts = task.efforts()
        taskAndAncestors = [task] + task.ancestors()
        compositesToRemove = []
        for effort in efforts:
            for task in taskAndAncestors:
                compositesToRemove.extend(self.compositeToRemove(effort, task))
        return compositesToRemove
        
    def compositeToRemove(self, anEffort, task):  # pylint: disable-msg=W0613,W0621
        key = self.keyForEffort(anEffort, task)
        # A composite may already have been removed, e.g. when a
        # parent and child task have effort in the same period
        return [self.__composites.pop(key)] if key in self.__composites else []

    def maxDateTime(self):
        stopTimes = [effort.getStop() for compositeEffort in self for effort
                     in compositeEffort if effort.getStop() is not None]
        return max(stopTimes) if stopTimes else None

    @staticmethod
    def keyForComposite(compositeEffort):
        if compositeEffort.task().__class__.__name__ == 'Total':
            return (compositeEffort.getStart(), compositeEffort.getStop())
        else:
            return (compositeEffort.task(), compositeEffort.getStart(), 
                    compositeEffort.getStop())
    
    def keyForEffort(self, effort, task=None):  # pylint: disable-msg=W0621
        task = task or effort.task()
        effortStart = effort.getStart()
        return (task, self.startOfPeriod(effortStart), 
            self.endOfPeriod(effortStart))
        
    def keyForPeriod(self, effort):
        key = self.keyForEffort(effort)
        return key[1], key[2]
    
    @classmethod
    def sortEventType(class_):
        return 'this event type is not used'  # pragma: no cover
