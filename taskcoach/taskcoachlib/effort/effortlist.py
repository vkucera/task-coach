import patterns                    
        
class EffortList(patterns.ObservableListObserver):
    def __init__(self, *args, **kwargs):
        super(EffortList, self).__init__(*args, **kwargs)
        self._extend(self.original().efforts())
        
    def onNotify(self, notification, *args, **kwargs):
        self.stopNotifying()
        # FIXME: dont expect effortsRemoved, but just itemsRemoved and 
        # let EffortList figure out what efforts are removed, etc.
        self._removeItems(notification.effortsRemoved)
        self._extend(notification.effortsAdded)
        self.startNotifying()
        self.notifyObservers(patterns.observer.Notification(self, 
            notification), *args, **kwargs)
        
        
class SingleTaskEffortList(patterns.ObservableObservablesList):
    ''' SingleTaskEffortList filters an EffortList so it contains the efforts for 
        one task (including its children). '''
        
    def __init__(self, task, *args, **kwargs):
        super(SingleTaskEffortList, self).__init__(*args, **kwargs)
        task.registerObserver(self.onTaskNotify)
        efforts = task.efforts()
        for child in task.allChildren():
            efforts.extend(child.efforts())
        self.extend(efforts)
        
    def onTaskNotify(self, notification, *args, **kwargs):
        if not (notification.effortsAdded or notification.effortsRemoved):
            return
        self.stopNotifying()
        self.extend(notification.effortsAdded)
        self.removeItems(notification.effortsRemoved)
        self.startNotifying()
        myNotification = patterns.observer.Notification(self, 
            itemsAdded=notification.effortsAdded,
            itesmRemoved=notification.effortsRemoved)
        self.notifyObservers(myNotification)

