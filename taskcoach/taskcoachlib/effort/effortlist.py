import patterns                    

class EffortListMixin:
   def _addAndRemoveEfforts(self, effortsToAdd, effortsToRemove, effortsChanged=None):
        if not (effortsToAdd or effortsToRemove or effortsChanged):
            return
        self.stopNotifying()
        self._extend(effortsToAdd)
        self._removeItems(effortsToRemove)
        self.startNotifying()
        self.notifyObservers(patterns.observer.Notification(self,
            itemsAdded=effortsToAdd, itemsRemoved=effortsToRemove,
            itemsChanged=effortsChanged or []))

                        
class EffortList(patterns.ObservableListObserver, EffortListMixin):
    def onNotify(self, notification, *args, **kwargs):
        effortsToAdd, effortsToRemove = [], []
        for task in notification.itemsAdded:
            effortsToAdd.extend(task.efforts())
            task.registerObserver(self.onNotifyTask)
        for task in notification.itemsRemoved:
            effortsToRemove.extend(task.efforts())
            task.removeObserver(self.onNotifyTask)   
        self._addAndRemoveEfforts(effortsToAdd, effortsToRemove)
                
    def onNotifyTask(self, notification, *args, **kwargs):
        self._addAndRemoveEfforts(notification.effortsAdded, 
            notification.effortsRemoved, notification.effortsChanged)


class SingleTaskEffortList(patterns.ObservableObservablesList, EffortListMixin):
    ''' SingleTaskEffortList filters an EffortList so it contains the efforts for 
        one task (including its children). '''
        
    def __init__(self, task, *args, **kwargs):
        super(SingleTaskEffortList, self).__init__(*args, **kwargs)
        task.registerObserver(self.onNotify)
        for child in task.allChildren():
            child.registerObserver(self.onNotify)
        self.extend(task.efforts(recursive=True))
        
    def onNotify(self, notification, *args, **kwargs):
        self._addAndRemoveEfforts(notification.effortsAdded,
            notification.effortsRemoved, notification.effortsChanged)
        for child in notification.childrenAdded:
            child.registerObserver(self.onNotify)
        for child in notification.childrenRemoved:
            child.removeObserver(self.onNotify)    
            
    def _extend(self, *args, **kwargs):
        self.extend(*args, **kwargs)
        
    def _removeItems(self, *args, **kwargs):
        self.removeItems(*args, **kwargs)