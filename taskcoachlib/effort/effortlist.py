import patterns                    

                        
class EffortList(patterns.ObservableListObserver):
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
        

class SingleTaskEffortList(patterns.ObservableListObserver):
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
            