import patterns
from domain import base


class Category(base.CompositeObject):
    def __init__(self, subject, tasks=None, children=None, filtered=False, 
                 parent=None, description=''):
        super(Category, self).__init__(subject=subject, children=children or [], 
                                       parent=parent, description=description)
        self.__tasks = tasks or []
        self.__filtered = filtered
            
    @classmethod
    def filterChangedEventType(class_):
        return 'category.filter'
    
    @classmethod
    def taskAddedEventType(class_):
        return 'category.task.added'
    
    @classmethod
    def taskRemovedEventType(class_):
        return 'category.task.removed'
            
    def __getstate__(self):
        state = super(Category, self).__getstate__()
        state.update(dict(tasks=self.__tasks[:], 
                          filtered=self.__filtered))
        return state
        
    def __setstate__(self, state):
        super(Category, self).__setstate__(state)
        self.__tasks = state['tasks']
        self.__filtered = state['filtered']
        
    def copy(self):
        return self.__class__(self.subject(), self.tasks(), 
                              [child.copy() for child in self.children()],
                              self.isFiltered(), self.parent(), 
                              self.description())
        
    def setSubject(self, *args, **kwargs):
        if super(Category, self).setSubject(*args, **kwargs):
            for task in self.tasks(recursive=True):
                task.notifyObserversOfCategorySubjectChange(self)
    
    def tasks(self, recursive=False):
        result = []
        if recursive:
            for child in self.children():
                result.extend(child.tasks(recursive))
        result.extend(self.__tasks)
        return result
    
    def addTask(self, task):
        if task not in self.__tasks: # FIXME: use set
            self.__tasks.append(task)
            self.notifyObservers(patterns.Event(self, 
                self.taskAddedEventType(), task))
            
    def removeTask(self, task):
        if task in self.__tasks:
            self.__tasks.remove(task)
            self.notifyObservers(patterns.Event(self, 
                self.taskRemovedEventType(), task))
        
    def isFiltered(self):
        return self.__filtered
    
    def setFiltered(self, filtered=True):
        if filtered != self.__filtered:
            self.__filtered = filtered
            self.notifyObservers(patterns.Event(self, 
                self.filterChangedEventType(), filtered))
        
    def contains(self, task, treeMode=False):
        containedTasks = self.tasks(recursive=True)
        if treeMode:
            tasksToInvestigate = task.family()
        else:
            tasksToInvestigate = [task] + task.ancestors()
        for task in tasksToInvestigate:
            if task in containedTasks:
                return True
        return False