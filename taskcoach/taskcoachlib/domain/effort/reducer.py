import patterns, effort
from domain import date


class EffortAggregator(patterns.ListDecorator):
    ''' This class observes an TaskList and aggregates the individual effort
        records to CompositeEfforts, e.g. per day or per week. This class is 
        abstract. Subclasses should implement startOfPeriod(dateTime)
        and endOfPeriod(dateTime). '''

    def __init__(self, *args, **kwargs):
        self.__taskAndTimeToCompositesMap = {}
        self.__taskToCompositesMap = {}
        super(EffortAggregator, self).__init__(*args, **kwargs)

    def extendSelf(self, tasks):
        ''' extendSelf is called when an item is added to the observed
            list. The default behavior of extendSelf is to add the item
            to the observing list (i.e. this list) unchanged. We override 
            the default behavior to first get the efforts from the task
            and then group the efforts by time period. '''
        newEfforts = []
        for newTask in tasks:
            newTask.registerObserver(self.onEffortAddedToTask, 
                'task.effort.add')
            newTask.registerObserver(self.onEffortRemovedFromTask, 
                'task.effort.remove')
            newTask.registerObserver(self.onChildAddedToTask, 
                'task.child.add')
            newEfforts.extend(newTask.efforts())
        self.addComposites(self.addEfforts(newEfforts))

    def removeItemsFromSelf(self, tasks):
        ''' removeItemsFromSelf is called when an item is removed from the 
            observed list. The default behavior of removeItemsFromSelf is to 
            remove the item from the observing list (i.e. this list)
            unchanged. We override the default behavior to remove the 
            tasks' efforts from the CompositeEfforts they are part of. '''
        compositesToRemove = []
        for task in tasks:
            task.removeObservers(self.onEffortAddedToTask,
                                 self.onEffortRemovedFromTask,
                                 self.onChildAddedToTask)
            for effort in task.efforts():
                effort.removeObserver(self.onEffortChanged)
            compositesToRemove.extend(self.__taskToCompositesMap.get(task, []))
        self.removeComposites(compositesToRemove)

    def onChildAddedToTask(self, event):
        child = event.value() 
        self.addComposites(self.addEfforts(child.efforts(recursive=True)))

    def onEffortAddedToTask(self, event):
        self.addComposites(self.addEfforts(event.values()))

    def onEffortRemovedFromTask(self, event):
        event.value().removeObserver(self.onEffortChanged)

    def onEffortChanged(self, event):
        ''' onEffortChanged is called when the start datetime or the
            task of an effort record has changed. '''
        effortChanged = event.source()
        self.addComposites(self.addEfforts([effortChanged]))

    def onCompositeEmpty(self, event):
        self.removeComposites([event.source()])

    def addComposites(self, composites):
        for composite in composites:
            composite.registerObserver(self.onCompositeEmpty, 'list.empty')
        super(EffortAggregator, self).extendSelf(composites)

    def removeComposites(self, composites):
        for composite in composites:
            composite.removeObserver(self.onCompositeEmpty)
            task = composite.task()
            self.__taskToCompositesMap[task].remove(composite)
            key = (task.id(), composite.getStart())
            del self.__taskAndTimeToCompositesMap[key]
        super(EffortAggregator, self).removeItemsFromSelf(composites)
        
    def addEfforts(self, efforts):
        newComposites = set()
        for effort in efforts:
            effort.registerObserver(self.onEffortChanged, 'effort.start')
            newComposites |= self.addEffort(effort)
        newComposites.discard(None)
        return newComposites

    def addEffort(self, newEffort):
        newComposites = set()
        for task in [newEffort.task()] + newEffort.task().ancestors():
            newComposites.add(self.addEffortForTask(newEffort, task))
        return newComposites

    def addEffortForTask(self, newEffort, task):
        startOfEffort = newEffort.getStart()
        startOfPeriod = self.startOfPeriod(startOfEffort)
        key = (task.id(), startOfPeriod)
        if key in self.__taskAndTimeToCompositesMap:
            newComposite = None
        else:
            newComposite = effort.CompositeEffort(task, startOfPeriod, 
                self.endOfPeriod(startOfEffort))
            self.__taskToCompositesMap.setdefault(task, []).append(newComposite)
            self.__taskAndTimeToCompositesMap[key] = newComposite
        return newComposite

    def startOfPeriod(self, dateTime):
        ''' For a given dateTime, startOfPeriod returns the start-dateTime 
            of the period dateTime belongs to. '''
        raise NotImplementedError

    def endOfPeriod(self, dateTime):
        ''' For a given dateTime, endOfPeriod returns the end-dateTime 
            of the period dateTime belongs to. '''
        raise NotImplementedError

    def originalLength(self):
        ''' Do not delegate originalLength to the observed TaskList because 
            that would return a number of tasks, and not the number of 
            effort records.'''
        return len(self)


class EffortPerDay(EffortAggregator):        
    startOfPeriod = date.DateTime.startOfDay
    endOfPeriod = date.DateTime.endOfDay


class EffortPerWeek(EffortAggregator): 
    startOfPeriod = date.DateTime.startOfWeek
    endOfPeriod = date.DateTime.endOfWeek


class EffortPerMonth(EffortAggregator):
    startOfPeriod = date.DateTime.startOfMonth
    endOfPeriod = date.DateTime.endOfMonth
        
