import patterns, task

class Sorter(patterns.ObservableListObserver):
    def __init__(self, *args, **kwargs):
        self.__sortOnSubject = False
        super(Sorter, self).__init__(*args, **kwargs)

    def postProcessChanges(self):
        if self.__sortOnSubject:
            self.sort(key=task.Task.subject)
        else:
            self.sort()

    def setSortOnSubject(self, sortOnSubject=True):
        self.__sortOnSubject = sortOnSubject
        self.reset()

    def getSortOnSubject(self):
        return self.__sortOnSubject

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
        