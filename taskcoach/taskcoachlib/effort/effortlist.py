import patterns, date                    
        
class EffortList(patterns.ObservableListObserver):
    def notifyChange(self, tasks):
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
        efforts = []
        for task in tasks:
            efforts.extend(task.efforts())
        self._extend(efforts)
            
    def notifyRemove(self, tasks):
        efforts = []
        for task in tasks:
            efforts.extend(task.efforts())
        self._removeItems(efforts)
                     
        
class SingleTaskEffortList(patterns.ObservableObservablesList):
    ''' SingleTaskEffortList filters an EffortList so it contains the efforts for 
        one task (including its children). '''
        
    def __init__(self, task, *args, **kwargs):
        super(SingleTaskEffortList, self).__init__(*args, **kwargs)
        task.registerObserver(self.notify)
        
    def notify(self, task):
        for effort in self:
            if effort.task() == task and effort not in task.efforts():
                self.remove(effort)
        for effort in task.efforts():
            if effort not in self:
                self.append(effort)
