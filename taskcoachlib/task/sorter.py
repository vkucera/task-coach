import patterns, task

class Sorter(patterns.ObservableListObserver):
    defaultSortKey = 'dueDate'
    def __init__(self, *args, **kwargs):
        self.__sortKey = getattr(self, '_%sSortKey'%self.defaultSortKey)
        self.__ascending = True
        self.__sortByStatusFirst = True
        super(Sorter, self).__init__(*args, **kwargs)

    def _dueDateSortKey(self, task):
        result = []
        if self.__sortByStatusFirst:
            result.extend([task.completed(), task.inactive()])
        result.extend([task.dueDate(), task.startDate(), task.subject()])
        return tuple(result)
        
    def _subjectSortKey(self, task):
        result = []
        if self.__sortByStatusFirst:
            result.extend([task.completed(), task.inactive()])
        result.append(task.subject())
        return tuple(result)

    def _budgetSortKey(self, task):
        result = []
        if self.__sortByStatusFirst:
            result.extend([task.completed(), task.inactive()])
        result.append(task.budget())
        return tuple(result)

    def postProcessChanges(self):
        self.sort(key=self.__sortKey, reverse=not self.__ascending)
  
    def setSortKey(self, sortKey):
        self.__sortKey = getattr(self, '_%sSortKey'%sortKey)
        self.reset()
        
    def getSortKey(self):
        return self.__sortKey.__name__[1:-len('SortKey')]
        
    def setAscending(self, ascending=True):
        self.__ascending = ascending
        self.reset()
        
    def isAscending(self):
        return self.__ascending
        
    def setSortByStatusFirst(self, sortByStatusFirst=True):
        self.__sortByStatusFirst = sortByStatusFirst
        self.reset()

    def rootTasks(self):
        return [task for task in self if task.parent() is None]


class DepthFirstSorter(patterns.ObservableListObserver):
    ''' DepthFirstSorter assumes the tasks in the original list are sorted, and
        just need to be put in tree-like order, i.e. put children after their 
        parents, in depth-first fashion. ''' 

    def processChanges(self, notification):
        return self.original(), self[:], []
        
    def postProcessChanges(self):
        self[:] = self.sortDepthFirst(self.original().rootTasks())
        
    def sortDepthFirst(self, tasks):
        result = []
        for task in tasks:
            result.append(task)
            if task.children():
                sortedChildren = [child for child in self.original() \
                    if child.parent() and child.parent() == task]
                result.extend(self.sortDepthFirst(sortedChildren))
        return result

    def rootTasks(self):
        return [task for task in self if task.parent() is None]
        