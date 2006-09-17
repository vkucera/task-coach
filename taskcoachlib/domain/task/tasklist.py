import patterns
from i18n import _
import domain.date as date
import task

            
class TaskList(patterns.ObservableSet):
    def __init__(self, initList=None, *args, **kwargs):
        super(TaskList, self).__init__(*args, **kwargs)
        self.extend(initList or [])
        
    def append(self, task):
        self.extend([task])
        
    def extend(self, tasks):
        if not tasks:
            return
        tasksAndAllChildren = self._tasksAndAllChildren(tasks) 
        self.stopNotifying()
        super(TaskList, self).extend(tasksAndAllChildren)
        parentsWithChildrenAdded = self._addTasksToParent(tasks)
        self.startNotifying()
        self.notifyObserversOfItemsAdded(*tasksAndAllChildren)
        for parent, children in parentsWithChildrenAdded.items():
            self.notifyObservers(patterns.Event(parent,
                'task.child.add', *children))

    def _tasksAndAllChildren(self, tasks):
        tasksAndAllChildren = set(tasks) 
        for task in tasks:
            tasksAndAllChildren |= set(task.children(recursive=True))
        return list(tasksAndAllChildren)

    def _splitTasksInParentsAndChildren(self, tasks):
        parents, children = [], []
        for task in tasks:
            for ancestor in task.ancestors():
                if ancestor in tasks:
                    children.append(task)
                    break
            else:
                parents.append(task)
        return parents, children
    
    def _addTasksToParent(self, tasks):
        parents = {}
        for task in tasks:
            parent = task.parent()
            if parent and parent in self:
                parent.addChild(task)
                if parent not in tasks:
                    parents.setdefault(parent, []).append(task)
        return parents

    def remove(self, task):
        if task in self:
            self.removeItems([task])
            
    def removeItems(self, tasks):
        if not tasks:
            return
        parents, children = self._splitTasksInParentsAndChildren(tasks)
        tasksAndAllChildren = self._tasksAndAllChildren(parents)
        self.stopNotifying()
        self._removeTasksFromTaskList(parents)
        parentsWithChildrenRemoved = self._removeTasksFromParent(tasks)
        self.startNotifying()
        self.notifyObserversOfItemsRemoved(*tasksAndAllChildren)
        for parent, children in parentsWithChildrenRemoved.items():
            if parent in self:
                self.notifyObservers(patterns.Event(parent,
                    'task.child.remove', *children))

    def _removeTaskFromTaskList(self, task):
        self._removeTasksFromTaskList(task.children())
        super(TaskList, self).remove(task)
        
    def _removeTasksFromTaskList(self, tasks):
        for task in tasks:
            if task in self:
                self._removeTaskFromTaskList(task)
            
    def _removeTasksFromParent(self, tasks):
        parents = {}
        for task in tasks:
            parent = task.parent()
            if parent:
                parent.removeChild(task)
                if parent not in tasks:
                    parents.setdefault(parent, []).append(task)
        return parents

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

    def rootItems(self):
        return [task for task in self if task.parent() is None or \
                task.parent() not in self]
            
    def efforts(self):
        result = []
        for task in self:
            result.extend(task.efforts())
        return result

    def categories(self):
        result = set()
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

        
class SingleTaskList(TaskList):
    pass