import patterns, date

class Cache(dict):
    def __init__(self, computeValue, *args, **kwargs):
        super(Cache, self).__init__(*args, **kwargs)
        self._computeValue = computeValue
        
    def clean(self, efforts):
        for effort in efforts:
            task = effort.task()
            for key in self.keys():
                if task in key:
                    del self[key]        
                    
    def __getitem__(self, tasks):
        key = tuple(tasks)
        if not key in self:
            self[key] = self._computeValue(tasks)
        return super(Cache, self).__getitem__(key)
                    
        
class EffortList(patterns.ObservableObservablesList):
    def __init__(self, *args, **kwargs):
        super(EffortList, self).__init__(self, *args, **kwargs)
        self._activeTasks = []
        self._start = date.DateTime.now()
        self._timeSpentCache = Cache(self._computeTimeSpentForTasks)
                    
    def notifyChange(self, effort):
        self._timeSpentCache.clean([effort])
        super(EffortList, self).notifyChange(effort)

    def _notifyObserversOfNewItems(self, efforts):
        self._timeSpentCache.clean(efforts)
        super(EffortList, self)._notifyObserversOfNewItems(efforts)
            
    def _notifyObserversOfRemovedItems(self, efforts):
        self._timeSpentCache.clean(efforts)
        super(EffortList, self)._notifyObserversOfRemovedItems(efforts)        
                
    def getEffortForTask(self, task):
        return self.getEffortForTasks([task])
    
    def getEffortForTasks(self, tasks):
        return [effort for effort in self if effort.task() in tasks]
    
    def getTimeSpentForTasks(self, tasks): 
        return self._timeSpentCache[tasks]
        
    def _computeTimeSpentForTasks(self, tasks):
        return sum([effort.duration() for effort in self.getEffortForTasks(tasks)],
            date.TimeDelta())
            
    def getTimeSpentForTask(self, task):
        return self.getTimeSpentForTasks([task])
        
    def getTotalTimeSpentForTask(self, task):
        return self.getTimeSpentForTasks([task]+task.allChildren())
        
    def setActiveTasks(self, newActiveTasks, adjacent=False):
        if adjacent:
            self._start = self.maxDateTime() or date.DateTime.now()
        else:
            self._start = date.DateTime.now()
        previousActiveTasks = self._activeTasks
        self._activeTasks = newActiveTasks
        self.notifyTaskObservers(previousActiveTasks + newActiveTasks)
    
    def notifyTaskObservers(self, tasks):
        for task in tasks:
            task._notifyObserversOfChange()
        
    def getActiveTasks(self):
        return self._activeTasks
        
    def start(self):
        return self._start

    def maxDateTime(self):
        if self:
            return max([effort.getStop() for effort in self])
        else:
            return None
                     
        
class SingleTaskEffortList(patterns.ObservableListObserver):
    ''' SingleTaskEffortList filters an EffortList so it contains the efforts for 
        one task (including its children). '''
        
    def __init__(self, task, effortList, *args, **kwargs):
        self._task = task
        super(SingleTaskEffortList, self).__init__(effortList, *args, **kwargs)
        
    def _filterMyEfforts(self, efforts):
        return [effort for effort in efforts \
            if self._task in [effort.task()] + effort.task().ancestors()]
        
    def notifyAdd(self, newEfforts):
        newEffortsForMyTask = self._filterMyEfforts(newEfforts)
        self._extend(newEffortsForMyTask)
        
    def notifyChange(self, changedEfforts):
        changedEffortsForMyTask = self._filterMyEfforts(changedEfforts)
        super(SingleTaskEffortList, self).notifyChange(changedEffortsForMyTask)

    def notifyRemove(self, removedEfforts):
        removedEffortsForMyTask = self._filterMyEfforts(removedEfforts)
        self._removeItems(removedEffortsForMyTask)