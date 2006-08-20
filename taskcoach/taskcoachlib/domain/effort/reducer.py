import patterns, effort
from domain import date


class EffortAggregator(patterns.SetDecorator):
    ''' This class observes an TaskList and aggregates the individual effort
        records to CompositeEfforts, e.g. per day or per week. This class is 
        abstract. Subclasses should implement startOfPeriod(dateTime)
        and endOfPeriod(dateTime). '''
    def __init__(self, *args, **kwargs):
        self.__composites = {}
        super(EffortAggregator, self).__init__(*args, **kwargs)
        patterns.Publisher().registerObserver(self.onCompositeEmpty,
            eventType='effort.composite.empty')
        patterns.Publisher().registerObserver(self.onEffortAddedToTask, 
            eventType='task.effort.add')
        patterns.Publisher().registerObserver(self.onChildAddedToTask,
            eventType='task.child.add')
        patterns.Publisher().registerObserver(self.onEffortStartChanged, 
            eventType='effort.start')

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
        key = (composite.task(), composite.getStart())
        if key not in self.__composites:
            # A composite may already have been removed, e.g. when a
            # parent and child task have effort in the same period
            return
        del self.__composites[(composite.task(), composite.getStart())]
        super(EffortAggregator, self).removeItemsFromSelf([composite])
        
    def onEffortStartChanged(self, event):
        effort, start = event.source(), event.value()
        task = effort.task()
        if (task in self.observable()) and \
           ((task, self.startOfPeriod(start)) not in self.__composites):
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
        startOfEffort = anEffort.getStart()
        startOfPeriod = self.startOfPeriod(startOfEffort)
        key = (task, startOfPeriod) 
        if key in self.__composites:
            return []
        newComposite = effort.CompositeEffort(task, startOfPeriod, 
                self.endOfPeriod(startOfEffort))
        self.__composites[key] = newComposite
        return [newComposite]

    def removeComposites(self, task, efforts):
        taskAndAncestors = [task] + task.ancestors()
        for effort in efforts:
            for task in taskAndAncestors:
                self.removeComposite(effort, task)

    def removeComposite(self, anEffort, task):
        startOfEffort = anEffort.getStart()
        startOfPeriod = self.startOfPeriod(startOfEffort)
        key = (task, startOfPeriod) 
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


class EffortPerDay(EffortAggregator):        
    startOfPeriod = date.DateTime.startOfDay
    endOfPeriod = date.DateTime.endOfDay
    

class EffortPerWeek(EffortAggregator): 
    startOfPeriod = date.DateTime.startOfWeek
    endOfPeriod = date.DateTime.endOfWeek


class EffortPerMonth(EffortAggregator):
    startOfPeriod = date.DateTime.startOfMonth
    endOfPeriod = date.DateTime.endOfMonth
    