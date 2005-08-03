import patterns, task

class Sorter(patterns.ObservableListObserver):
    defaultSortKey = 'dueDate'
    
    def __init__(self, *args, **kwargs):
        self.__sortKey = self.defaultSortKey
        self.__sortKeyInitialized = False
        self.__ascending = True
        self.__sortByStatusFirst = True
        super(Sorter, self).__init__(*args, **kwargs)
     
    def _statusSortKey(self, task):
        if self.__sortByStatusFirst:
            if self.__ascending:
                return [task.completed(), task.inactive()]
            else:
                return [not task.completed(), not task.inactive()]
        else:
            return []

    def __generateSortKey(self, sortKeyName):
        def sortKey(task, sortKeyName=sortKeyName):
            args = []
            if sortKeyName.startswith('total'):
                args.append(True)
                sortKeyName = sortKeyName[len('total'):]
            return self._statusSortKey(task) + [getattr(task, sortKeyName)(*args)]
        return sortKey

    def postProcessChanges(self, notification):
        oldSelf = self[:]
        self.sort(key=self.__generateSortKey(self.__sortKey), reverse=not self.__ascending)
        if self != oldSelf:
            notification['orderChanged'] = True
        return notification
        
    def setSortKey(self, sortKey):
        if sortKey == self.getSortKey() and self.__sortKeyInitialized:
            self.setAscending(not self.isAscending())
        else:
            self.__sortKey = sortKey
        self.__sortKeyInitialized = True
        self.reset()
        
    def getSortKey(self):
        return self.__sortKey
        
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
        return notification
        
    def postProcessChanges(self, notification):
        oldSelf = self[:]
        self[:] = self.sortDepthFirst(self.original().rootTasks())
        if self != oldSelf:
            notification['orderChanged'] = True
        return notification
         
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
        
