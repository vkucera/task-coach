'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>

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
import effort, effortlist


class EffortAggregator(patterns.SetDecorator, 
                       effortlist.EffortUICommandNamesMixin):
    ''' This class observes an TaskList and aggregates the individual effort
        records to CompositeEfforts, e.g. per day or per week. '''
    def __init__(self, *args, **kwargs):
        self.__composites = {}
        aggregation = kwargs.pop('aggregation')
        assert aggregation in ('day', 'week', 'month')
        aggregation = aggregation.capitalize()
        self.startOfPeriod = getattr(date.DateTime, 'startOf%s'%aggregation)
        self.endOfPeriod = getattr(date.DateTime, 'endOf%s'%aggregation)
        super(EffortAggregator, self).__init__(*args, **kwargs)
        patterns.Publisher().registerObserver(self.onCompositeEmpty,
            eventType='effort.composite.empty')
        patterns.Publisher().registerObserver(self.onEffortAddedToTask, 
            eventType='task.effort.add')
        patterns.Publisher().registerObserver(self.onChildAddedToTask,
            eventType=task.Task.addChildEventType())
        patterns.Publisher().registerObserver(self.onEffortStartChanged, 
            eventType='effort.start')
        
    def extend(self, efforts):
        for effort in efforts:
            effort.task().addEffort(effort)
            
    def removeItems(self, efforts):
        for effort in efforts:
            effort.task().removeEffort(effort)
            
    def extendSelf(self, tasks):
        ''' extendSelf is called when an item is added to the observed
            list. The default behavior of extendSelf is to add the item
            to the observing list (i.e. this list) unchanged. We override 
            the default behavior to first get the efforts from the task
            and then group the efforts by time period. '''
        newComposites = []
        for task in tasks:
            newComposites.extend(self.createComposites(task, task.efforts()))
        super(EffortAggregator, self).extendSelf(newComposites)

    def removeItemsFromSelf(self, tasks):
        ''' removeItemsFromSelf is called when an item is removed from the 
            observed list. The default behavior of removeItemsFromSelf is to 
            remove the item from the observing list (i.e. this list)
            unchanged. We override the default behavior to remove the 
            tasks' efforts from the CompositeEfforts they are part of. '''
        for task in tasks:
            self.removeComposites(task, task.efforts())

    def onEffortAddedToTask(self, event):
        task, effort = event.source(), event.value()
        if task in self.observable():
            newComposites = self.createComposites(task, [effort])
            super(EffortAggregator, self).extendSelf(newComposites)
        
    def onChildAddedToTask(self, event):
        task, child = event.source(), event.value()
        if task in self.observable():
            newComposites = self.createComposites(task,
                child.efforts(recursive=True))
            super(EffortAggregator, self).extendSelf(newComposites)

    def onCompositeEmpty(self, event):
        composite = event.source()
        if composite not in self:
            return
        key = self.keyForComposite(composite)
        if key not in self.__composites:
            # A composite may already have been removed, e.g. when a
            # parent and child task have effort in the same period
            return
        del self.__composites[key]
        super(EffortAggregator, self).removeItemsFromSelf([composite])
        
    def onEffortStartChanged(self, event):
        effort = event.source()
        key = self.keyForEffort(effort)
        task = effort.task()
        if (task in self.observable()) and (key not in self.__composites):
            newComposites = self.createComposites(task, [effort])
            super(EffortAggregator, self).extendSelf(newComposites)
            
    def createComposites(self, task, efforts):
        newComposites = []
        taskAndAncestors = [task] + task.ancestors()
        for effort in efforts:
            for task in taskAndAncestors:
                newComposites.extend(self.createComposite(effort, task))
        return newComposites

    def createComposite(self, anEffort, task):
        key = self.keyForEffort(anEffort, task)
        if key in self.__composites:
            return []
        newComposite = effort.CompositeEffort(*key)
        self.__composites[key] = newComposite
        return [newComposite]

    def removeComposites(self, task, efforts):
        taskAndAncestors = [task] + task.ancestors()
        for effort in efforts:
            for task in taskAndAncestors:
                self.removeComposite(effort, task)

    def removeComposite(self, anEffort, task):
        key = self.keyForEffort(anEffort, task)
        if key not in self.__composites:
            # A composite may already have been removed, e.g. when a
            # parent and child task have effort in the same period
            return
        compositeToRemove = self.__composites.pop(key)
        super(EffortAggregator, self).removeItemsFromSelf([compositeToRemove])

    def maxDateTime(self):
        stopTimes = [effort.getStop() for composite in self for effort
            in composite if effort.getStop() is not None]
        if stopTimes:
            return max(stopTimes)
        else:
            return None

    @staticmethod
    def keyForComposite(composite):
        return (composite.task(), composite.getStart(), composite.getStop())
    
    def keyForEffort(self, effort, task=None):
        task = task or effort.task()
        effortStart = effort.getStart()
        return (task, self.startOfPeriod(effortStart), 
            self.endOfPeriod(effortStart))
    
    @classmethod
    def sortEventType(class_):
        return 'this event type is not used' 

