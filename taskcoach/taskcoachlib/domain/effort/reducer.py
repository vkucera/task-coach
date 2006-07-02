import patterns, effort


class EffortAggregator(patterns.ListDecorator):
    ''' This class observes an TaskList and aggregates the individual effort
        records to CompositeEfforts, e.g. per day or per week. This class is 
        abstract. Subclasses should implement timePeriod(effort).'''

    def __init__(self, *args, **kwargs):
        self.__taskAndTimeToCompositesMap = {}
        self.__effortToCompositeMap = {}
        super(EffortAggregator, self).__init__(*args, **kwargs)

    def extendSelf(self, tasks):
        ''' extendSelf is called when an item is added to the observed
            list. The default behavior of extendSelf is to add the item
            to the observing list (i.e. this list) unchanged. We override 
            the default behavior to first get the efforts from the task
            and then group the efforts by time period. '''
        newComposites = []
        for newTask in tasks:
            newTask.registerObserver(self.onEffortAddedToTask, 
                'task.effort.add')
            newTask.registerObserver(self.onEffortRemovedFromTask, 
                'task.effort.remove')
            newTask.registerObserver(self.onChildAddedToTask,
                'task.child.add')
            newTask.registerObserver(self.onChildRemovedFromTask,
                'task.child.remove')
            newComposites.extend(self._addEfforts(newTask.efforts()))
        super(EffortAggregator, self).extendSelf(newComposites)

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
                                 self.onChildAddedToTask,
                                 self.onChildRemovedFromTask)
            compositesToRemove.extend(self._removeEfforts(task.efforts()))
        super(EffortAggregator, self).removeItemsFromSelf(compositesToRemove)

    def onEffortChanged(self, event):
        ''' onEffortChanged is called when the start datetime or the
            task of an effort record has changed. '''
        effortChanged = event.source()
        compositesToRemove = self._removeEfforts([effortChanged])
        super(EffortAggregator, self).removeItemsFromSelf(compositesToRemove)
        newComposites = self._addEfforts([effortChanged])
        super(EffortAggregator, self).extendSelf(newComposites)

    def onEffortAddedToTask(self, event):
        newComposites = self._addEfforts(event.values())
        super(EffortAggregator, self).extendSelf(newComposites)

    def onEffortRemovedFromTask(self, event):
        compositesToRemove = self._removeEfforts(event.values())
        super(EffortAggregator, self).removeItemsFromSelf(compositesToRemove)

    def onChildAddedToTask(self, event):
        newComposites = []
        parent = event.source()
        child = event.value()
        for effort in child.efforts(recursive=True):
            newComposites.extend(self._addEffortToCompositeForTask(effort,
                parent))
        super(EffortAggregator, self).extendSelf(newComposites)

    def onChildRemovedFromTask(self, event):
        compositesToRemove = []
        parent = event.source()
        child = event.value()
        for effort in child.efforts(recursive=True):
            compositesToRemove.extend( \
                self._removeEffortFromCompositeForTask(effort, parent))
        super(EffortAggregator, self).removeItemsFromSelf(compositesToRemove)

    def _addEfforts(self, efforts):
        newComposites = []
        for newEffort in efforts:
            newEffort.registerObserver(self.onEffortChanged, 'effort.start', 
                'effort.task')
            for task in [newEffort.task()] + newEffort.task().ancestors():
                newComposites.extend( \
                    self._addEffortToCompositeForTask(newEffort, task))
        return newComposites

    def _addEffortToCompositeForTask(self, newEffort, task):
        newComposites = []
        timePeriod = self.timePeriod(newEffort)
        key = (task.id(), timePeriod)
        composite = self.__taskAndTimeToCompositesMap.setdefault(key,
            effort.CompositeEffort(task, *timePeriod))
        if len(composite) == 0:
            newComposites.append(composite)
        composite.append(newEffort)
        self.__effortToCompositeMap.setdefault(newEffort, []).append(composite)
        return newComposites

    def _removeEfforts(self, efforts):
        compositesToRemove = []
        for effort in efforts:
            effort.removeObserver(self.onEffortChanged)
            for task in [effort.task()] + effort.task().ancestors():
                compositesToRemove.extend( \
                    self._removeEffortFromCompositeForTask(effort, task))
            del self.__effortToCompositeMap[effort]
        return compositesToRemove

    def _removeEffortFromCompositeForTask(self, effort, task):
        compositesToRemove = []
        composites = self.__effortToCompositeMap[effort]
        for composite in composites:
            if composite.task() == task:
                composite.remove(effort)
                if len(composite) == 0:
                    compositesToRemove.append(composite)
        return compositesToRemove

    def timePeriod(self, effort):
        raise NotImplementedError

    def originalLength(self):
        ''' Do not delegate originalLength to the observed TaskList because 
            that would return a number of tasks, and not the number of 
            effort records.'''
        return len(self)



"""
class _EffortAggregator(patterns.ListDecorator):
    ''' This class observes an EffortList and aggregates the individual effort
        records to CompositeEfforts, e.g. per day or per week. This class is 
        abstract. Subclasses should implement timePeriod(effort).'''
    
    def __init__(self, *args, **kwargs):
        self.__taskAndTimeToCompositesMap = {}
        self.__effortToCompositeMap = {}
        super(EffortAggregator, self).__init__(*args, **kwargs)
        
    def extendSelf(self, efforts):
        ''' extendSelf is called when an item is added to the observed
            list. The default behavior of extendSelf is to add the item
            to the observing list (i.e. this list) unchanged. We override 
            the default behavior to first group the effort by time period
            and then add the CompositeEffort(s) to this list. '''
        newComposites = []
        for newEffort in efforts:
            newEffort.registerObserver(self.onEffortChanged, 'effort.start',
                'effort.task')
            for task in [newEffort.task()] + newEffort.task().ancestors():
                timePeriod = self.timePeriod(newEffort)
                key = (task.id(), timePeriod)
                composite = self.__taskAndTimeToCompositesMap.setdefault(key,
                    effort.CompositeEffort(task, *timePeriod))
                if len(composite) == 0:
                    newComposites.append(composite)
                composite.append(newEffort)
                self.__effortToCompositeMap.setdefault(newEffort, 
                    []).append(composite)
        super(EffortAggregator, self).extendSelf(newComposites)

    def removeItemsFromSelf(self, efforts):
        ''' removeItemsFromSelf is called when an item is removed from the 
            observed list. The default behavior of removeItemsFromSelf is to 
            remove the item from the observing list (i.e. this list)
            unchanged. We override the default behavior to remove the 
            effort from the CompositeEffort is it part of. '''
        compositesToRemove = []
        for effort in efforts:
            effort.removeObserver(self.onEffortChanged)
            composites = self.__effortToCompositeMap.pop(effort)
            for composite in composites:
                composite.remove(effort)
                if len(composite) == 0:
                    compositesToRemove.append(composite)
        super(EffortAggregator, self).removeItemsFromSelf(compositesToRemove)

    def onEffortChanged(self, event):
        effortChanged = event.source()
        self.removeItemsFromSelf([effortChanged])
        self.extendSelf([effortChanged])

    def timePeriod(self, effort):
        raise NotImplementedError

    def originalLength(self):
        ''' Do not delegate originalLength to the observed TaskList because 
            that would return a number of tasks, and not the number of 
            effort records.'''
        return len(self)
"""

class EffortPerDay(EffortAggregator):        
    def timePeriod(self, effort):
        return effort.getStart().startOfDay(), effort.getStart().endOfDay()


class EffortPerWeek(EffortAggregator): 
    def timePeriod(self, effort):
        return effort.getStart().startOfWeek(), effort.getStart().endOfWeek()


class EffortPerMonth(EffortAggregator):
    def timePeriod(self, effort):
        return effort.getStart().startOfMonth(), effort.getStart().endOfMonth()
        
