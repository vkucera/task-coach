import patterns, task, sets

class TaskList(patterns.ObservableObservablesList):
    def __init__(self, initList=None, *args, **kwargs):
        super(TaskList, self).__init__(*args, **kwargs)
        self.extend(initList or [])

    # list interface and helpers

    def _addTaskToParent(self, task):
        parent = task.parent()
        if parent and parent in self:
            parent.addChild(task)

    def append(self, task):
        self.extend([task])
        
    def extend(self, tasks):
        # We use a set here because tasks could contain parents and their children and
        # we want to prevent adding the children twice
        if not tasks:
            return
        tasksAndAllChildren = sets.Set(tasks) 
        for task in tasks:
            tasksAndAllChildren |= sets.Set(task.allChildren())
        self.stopNotifying()
        super(TaskList, self).extend(tasksAndAllChildren)
        for task in tasks:
            self._addTaskToParent(task)
        self.startNotifying()
        self.notifyObservers(patterns.observer.Notification(self, 
            itemsAdded=list(tasksAndAllChildren)))

    def _removeTaskFromTaskList(self, task):
        self._removeTasksFromTaskList(task.children())
        super(TaskList, self).remove(task)
        
    def _removeTasksFromTaskList(self, tasks):
        for task in tasks:
            if task in self:
                self._removeTaskFromTaskList(task)
            
    def _removeTaskFromParent(self, task):
        parent = task.parent()
        if parent:
            parent.removeChild(task)

    def remove(self, task):
        if task not in self:
            return
        self.removeItems([task])
            
    def removeItems(self, tasks):
        if not tasks:
            return
        self.stopNotifying()
        self._removeTasksFromTaskList(tasks)
        for task in tasks:
            self._removeTaskFromParent(task)
        self.startNotifying()
        tasksAndAllChildren = sets.Set(tasks) 
        for task in tasks:
            tasksAndAllChildren |= sets.Set(task.allChildren())
        self.notifyObservers(patterns.observer.Notification(self,
            itemsRemoved=list(tasksAndAllChildren)))
            
    # queries

    def _nrInterestingTasks(self, isInteresting):
        interestingTasks = [task for task in self if isInteresting(task)]
        return len(interestingTasks)

    def nrCompleted(self):
        return self._nrInterestingTasks(task.Task.completed)

    def nrOverdue(self):
        return self._nrInterestingTasks(task.Task.overdue)

    def nrInactive(self):
        return self._nrInterestingTasks(task.Task.inactive)

    def nrDueToday(self):
        return self._nrInterestingTasks(task.Task.dueToday)

    def allCompleted(self):
        nrCompleted = self.nrCompleted()
        return nrCompleted > 0 and nrCompleted == len(self)

    def rootTasks(self):
        return [task for task in self if task.parent() is None]

    def maxDateTime(self):
        stopTimes = []
        for task in self:
            stopTimes.extend([effort.getStop() for effort in task.efforts()
                if effort.getStop() is not None])
        if stopTimes:
            return max(stopTimes)
        else:
            return None
            
    def efforts(self):
        result = []
        for task in self:
            result.extend(task.efforts())
        return result
