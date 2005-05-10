import patterns                    

class MaxDateTimeMixin:
    def maxDateTime(self):
        stopTimes = [effort.getStop() for effort in self if effort.getStop() is not None]
        if stopTimes:
            return max(stopTimes)
        else:
            return None
    
                        
class EffortList(patterns.ObservableListObserver, MaxDateTimeMixin):
    def onNotify(self, notification, *args, **kwargs):
        effortsToAdd, effortsToRemove = [], []
        for task in notification.itemsAdded:
            effortsToAdd.extend(task.efforts())
            task.registerObserver(self.onNotifyTask)
        for task in notification.itemsRemoved:
            effortsToRemove.extend(task.efforts())
            task.removeObserver(self.onNotifyTask)
        effortNotification = patterns.observer.Notification(notification.source, 
            itemsAdded=effortsToAdd, itemsRemoved=effortsToRemove)
        super(EffortList, self).onNotify(effortNotification, *args, **kwargs)
                
    def onNotifyTask(self, notification, *args, **kwargs):
        effortNotification = patterns.observer.Notification(notification.source, 
            itemsAdded=notification.effortsAdded, 
            itemsRemoved=notification.effortsRemoved,
            itemsChanged=notification.effortsChanged)
        super(EffortList, self).onNotify(effortNotification, *args, **kwargs)

        

class SingleTaskEffortList(patterns.ObservableListObserver, MaxDateTimeMixin):
    ''' SingleTaskEffortList filters an EffortList so it contains the efforts for 
        one task (including its children). '''
    
    # FIXME: SingleTaskEffortList is not a real ObservableListObserver
    def __init__(self, task, *args, **kwargs):
        super(SingleTaskEffortList, self).__init__(task, *args, **kwargs)
        for child in task.allChildren():
            child.registerObserver(self.onNotify)
        self._extend(task.efforts(recursive=True))
        
    def onNotify(self, notification, *args, **kwargs):
        effortNotification = patterns.observer.Notification(notification.source,
            itemsAdded=notification.effortsAdded, 
            itemsRemoved=notification.effortsRemoved,
            itemsChanged=notification.effortsChanged)
        super(SingleTaskEffortList, self).onNotify(effortNotification, *args, **kwargs)
        for child in notification.childrenAdded:
            child.registerObserver(self.onNotify)
        for child in notification.childrenRemoved:
            child.removeObserver(self.onNotify)    

