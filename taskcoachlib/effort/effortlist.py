import patterns, date

class Cache(dict):
    def __init__(self, computeValue, *args, **kwargs):
        super(Cache, self).__init__(*args, **kwargs)
        self._computeValue = computeValue
        
    def clean(self, tasks):
        for task in tasks:
            for key in self.keys():
                if task in key:
                    del self[key]        
                        
    def __getitem__(self, tasks):
        key = tuple(tasks)
        if not key in self:
            self[key] = self._computeValue(tasks)
        return super(Cache, self).__getitem__(key)
                    
        
class EffortList(patterns.ObservableListObserver):
    def __init__(self, *args, **kwargs):
        self._timeSpentCache = Cache(self._computeTimeSpentForTasks)
        super(EffortList, self).__init__(*args, **kwargs)
                    
    def notifyChange(self, tasks):
        self._timeSpentCache.clean(tasks)
        efforts = []
        for task in tasks:
            efforts.extend(task.efforts())
        effortsToBeRemoved = [effort for effort in self if effort.task() in tasks and effort not in efforts]
        effortsToBeAdded = [effort for effort in efforts if effort not in self]
        self._removeItems(effortsToBeRemoved)
        self._extend(effortsToBeAdded)
        if not effortsToBeRemoved and not effortsToBeAdded:
            # no new efforts and no removed efforts: so there must be changed efforts
            self._notifyObserversOfChange(efforts)
            
    def notifyAdd(self, tasks):
        self._timeSpentCache.clean(tasks)
        efforts = []
        for task in tasks:
            efforts.extend(task.efforts())
        self._extend(efforts)
            
    def notifyRemove(self, tasks):
        self._timeSpentCache.clean(tasks)
        efforts = []
        for task in tasks:
            efforts.extend(task.efforts())
        self._removeItems(efforts)
                
    def stopTracking(self):
        [effort.setStop() for effort in self if effort.getStop() is None]
                
    def getEffortForTask(self, task):
        return self.getEffortForTasks([task])
    
    def getEffortForTasks(self, tasks, recursive=False):
        if recursive:
            allChildren = []
            for task in tasks:
                allChildren.extend(task.allChildren())
            tasks.extend(allChildren)    
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
            
    def getActiveTasks(self):
        return [effort.task() for effort in self if effort.getStop() is None]
        
                     
        
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