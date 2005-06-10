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
            return parent
        else:
            return None

    def append(self, task):
        self.extend([task])
        
    def _tasksAndAllChildren(self, tasks):
        tasksAndAllChildren = sets.Set(tasks) 
        for task in tasks:
            tasksAndAllChildren |= sets.Set(task.allChildren())
        return list(tasksAndAllChildren)
        
    def extend(self, tasks):
        if not tasks:
            return
        tasksAndAllChildren = self._tasksAndAllChildren(tasks) 
        self.stopNotifying()
        super(TaskList, self).extend(tasksAndAllChildren)
        parents = []
        for task in tasks:
            parent = self._addTaskToParent(task)
            if parent:
                parents.append(parent)
        self.startNotifying()
        self.notifyObservers(patterns.observer.Notification(self, 
            itemsAdded=tasksAndAllChildren, itemsChanged=parents))

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
        return parent

    def remove(self, task):
        if task in self:
            self.removeItems([task])
            
    def removeItems(self, tasks):
        if not tasks:
            return
        self.stopNotifying()
        self._removeTasksFromTaskList(tasks)
        parents = []
        for task in tasks:
            parent = self._removeTaskFromParent(task)
            if parent and parent in self:
                parents.append(parent)
        self.startNotifying()
        self.notifyObservers(patterns.observer.Notification(self,
            itemsRemoved=self._tasksAndAllChildren(tasks), itemsChanged=parents))
            
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
    
    def nrBeingTracked(self):
        return self._nrInterestingTasks(task.Task.isBeingTracked)

    def allCompleted(self):
        nrCompleted = self.nrCompleted()
        return nrCompleted > 0 and nrCompleted == len(self)

    def rootTasks(self):
        return [task for task in self if task.parent() is None or task.parent() not in self]
            
    def efforts(self):
        result = []
        for task in self:
            result.extend(task.efforts())
        return result

    def categories(self):
        result = sets.Set()
        for task in self:
            result |= task.categories()
        return result