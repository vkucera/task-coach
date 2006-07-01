import patterns, sets
from i18n import _
import domain.date as date
import task

            
class TaskList(patterns.ObservableList):
    def __init__(self, initList=None, *args, **kwargs):
        super(TaskList, self).__init__(*args, **kwargs)
        self.extend(initList or [])
        
    def newItem(self):
        ''' TaskList knows how to create new items so classes that
            manipulate containers (TaskList, EffortList, etc.) such
            as commands (NewCommand, DeleteCommand, etc.) can
            create new items without having to know their type. '''
        return task.Task(subject=_('New task'))

    # list interface and helpers

    def append(self, task):
        self.extend([task])
        
    def extend(self, tasks):
        if not tasks:
            return
        tasksAndAllChildren = self._tasksAndAllChildren(tasks) 
        self.stopNotifying()
        super(TaskList, self).extend(tasksAndAllChildren)
        for task in tasks:
            self._addTaskToParent(task)
        self.startNotifying()
        self.notifyObservers(patterns.Event(self, 'list.add', 
            *tasksAndAllChildren))

    def _tasksAndAllChildren(self, tasks):
        tasksAndAllChildren = sets.Set(tasks) 
        for task in tasks:
            tasksAndAllChildren |= sets.Set(task.allChildren())
        return list(tasksAndAllChildren)

    def _addTaskToParent(self, task):
        parent = task.parent()
        if parent and parent in self:
            parent.addChild(task)

    def remove(self, task):
        if task in self:
            self.removeItems([task])
            
    def removeItems(self, tasks):
        if not tasks:
            return
        tasksAndAllChildren = self._tasksAndAllChildren(tasks)
        self.stopNotifying()
        self._removeTasksFromTaskList(tasks)
        for task in tasks:
            self._removeTaskFromParent(task)
        self.startNotifying()
        self.notifyObservers(patterns.Event(self, 'list.remove', 
            *tasksAndAllChildren))

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
        return [task for task in self if task.parent() is None or \
                task.parent() not in self]
            
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
    
    def __allDates(self):        
        realDates = [aDate for task in self 
            for aDate in (task.startDate(), task.dueDate(), task.completionDate()) 
            if aDate != date.Date()]
        if realDates:
            return realDates
        else:
            return [date.Date()]
            
    def minDate(self):      
        return min(self.__allDates())
          
    def maxDate(self):
        return max(self.__allDates())
        
    def originalLength(self):
        ''' Provide a way for bypassing the __len__ method of decorators. '''
        return len(self)
