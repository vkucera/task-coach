import patterns                    
        
class EffortList(patterns.ObservableListObserver):
    def notifyChange(self, tasks, *args, **kwargs):
        efforts = self.extractEfforts(tasks)
        effortsToBeRemoved = [effort for effort in self if effort.task() in tasks and effort not in efforts]
        effortsToBeAdded = [effort for effort in efforts if effort not in self]
        self._removeItems(effortsToBeRemoved)
        self._extend(effortsToBeAdded)
        if not effortsToBeRemoved and not effortsToBeAdded:
            # no new efforts and no removed efforts: so there must be changed efforts
            self._notifyObserversOfChange(efforts)
            
    def notifyAdd(self, tasks, *args, **kwargs):
        self._extend(self.extractEfforts(tasks))
            
    def notifyRemove(self, tasks, *args, **kwargs):
        self._removeItems(self.extractEfforts(tasks))
        
    def extractEfforts(self, tasks):
        efforts = []
        for task in tasks:
            efforts.extend(task.efforts())
        return efforts             

        
class SingleTaskEffortList(patterns.ObservableObservablesList):
    ''' SingleTaskEffortList filters an EffortList so it contains the efforts for 
        one task (including its children). '''
        
    def __init__(self, task, *args, **kwargs):
        super(SingleTaskEffortList, self).__init__(*args, **kwargs)
        task.registerObserver(self.notify)
        self.notify(task, patterns.observer.Notification(task, effortsAdded=task.efforts()))
        for child in task.allChildren():
            self.notify(child, patterns.observer.Notification(child, effortsAdded=child.efforts()))
        
    def notify(self, task, notification, *args, **kwargs):
        self.extend(notification.effortsAdded)
        self.removeItems(notification.effortsRemoved)
