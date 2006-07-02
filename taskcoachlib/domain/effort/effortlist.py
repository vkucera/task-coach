import patterns                    

class MaxDateTimeMixin:
    def maxDateTime(self):
        stopTimes = [effort.getStop() for effort in self if effort.getStop() is not None]
        if stopTimes:
            return max(stopTimes)
        else:
            return None
    
                        
class EffortList(patterns.ListDecorator, MaxDateTimeMixin):
    ''' EffortList observes a TaskList and contains all effort records of
        all tasks in the underlying TaskList. '''

    def extendSelf(self, tasks):
        ''' This method is called when a task is added to the observed list.
            It overrides ObservableListObserver.extendSelf whose default 
            behaviour is to add the item that is added to the observed 
            list to the observing list (this list) unchanged. But we want to 
            add the efforts of the tasks, rather than the tasks themselves. '''
        effortsToAdd = []
        for task in tasks:
            effortsToAdd.extend(task.efforts())
            task.registerObserver(self.onAddEffortToTask, 'task.effort.add')
            task.registerObserver(self.onRemoveEffortFromTask,
                'task.effort.remove')
        super(EffortList, self).extendSelf(effortsToAdd)
        
    def removeItemsFromSelf(self, tasks):
        ''' This method is called when a task is removed from the observed 
            list. It overrides ObservableListObserver.removeItemsFromSelf 
            whose default behaviour is to remove the item that was removed
            from the observed list from the observing list (this list) 
            unchanged. But we want to remove the efforts of the tasks, rather 
            than the tasks themselves. '''
        effortsToRemove = []
        for task in tasks:
            effortsToRemove.extend(task.efforts())
            task.removeObservers(self.onAddEffortToTask, 
                self.onRemoveEffortFromTask)
        super(EffortList, self).removeItemsFromSelf(effortsToRemove)

    def onAddEffortToTask(self, event):
        effortsToAdd = event.values()
        super(EffortList, self).extendSelf(effortsToAdd)
        
    def onRemoveEffortFromTask(self, event):
        effortsToRemove = event.values()
        super(EffortList, self).removeItemsFromSelf(effortsToRemove)

    def originalLength(self):
        ''' Do not delegate originalLength to the underlying TaskList because
            that would return a number of tasks, and not the number of effort 
            records.'''
        return len(self)
        
    def removeItems(self, efforts):
        ''' We override ObservableListObserver.removeItems because the default
            implementation is to remove the arguments from the original list,
            which in this case would mean removing efforts from a task list.
            Since that wouldn't work we remove the efforts from the tasks by
            hand. '''
        for effort in efforts:
            effort.task().removeEffort(effort)

    def extend(self, efforts):
        ''' We override ObservableListObserver.extend because the default
            implementation is to add the arguments to the original list,
            which in this case would mean adding efforts to a task list.
            Since that wouldn't work we add the efforts to the tasks by
            hand. '''
        for effort in efforts:
            effort.task().addEffort(effort)


class SingleTaskEffortList(patterns.ObservableList, MaxDateTimeMixin):
    ''' SingleTaskEffortList filters an EffortList so it contains the efforts 
        for one task (including its children). '''
    
    def __init__(self, task, *args, **kwargs):
        super(SingleTaskEffortList, self).__init__(*args, **kwargs)
        self.addTask(task)

    def onAddEffortToTask(self, event):
        effortsToAdd = event.values()
        self.extendSelf(effortsToAdd)
        
    def onRemoveEffortFromTask(self, event):
        effortsToRemove = event.values()
        self.removeItemsFromSelf(effortsToRemove)

    def onAddChild(self, event):
        self.addTask(event.value())

    def onRemoveChild(self, event):
        childRemoved = event.value()
        for child in [childAdded] + childAdded.allChildren():
            child.removeObservers(self.onAddEffortToTask, 
                self.onRemoveEffortFromTask, self.onAddChild, 
                self.onRemoveChild)
        self.removeItemsFromSelf(child.efforts(recursive=True))

    def addTask(self, task):
        for child in [task] + task.allChildren():
            child.registerObserver(self.onAddEffortToTask, 'task.effort.add')
            child.registerObserver(self.onRemoveEffortFromTask, 
                'task.effort.remove')
            child.registerObserver(self.onAddChild, 'task.child.add')
            child.registerObserver(self.onRemoveChild, 'task.child.remove')
        self.extendSelf(task.efforts(recursive=True))

    def extendSelf(self, efforts):
        super(SingleTaskEffortList, self).extend(efforts)

    def removeItemsFromSelf(self, efforts):
        super(SingleTaskEffortList, self).removeItems(efforts)
 
    def extend(self, efforts):
        for effort in efforts:
            effort.task().addEffort(effort)

    def removeItems(self, efforts):
        for effort in efforts:
            effort.task().removeEffort(effort)
