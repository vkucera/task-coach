import patterns                    

class MaxDateTimeMixin:
    def maxDateTime(self):
        stopTimes = [effort.getStop() for effort in self if effort.getStop() is not None]
        if stopTimes:
            return max(stopTimes)
        else:
            return None
    
                        
class EffortList(patterns.ObservableListObserver, MaxDateTimeMixin):
    ''' EffortList observes a TaskList and contains all effort records of
        all tasks in the underlying TaskList. '''
        
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

    def originalLength(self):
        ''' Do not delegate originalLength to the underlying TaskList because
        that would return a number of tasks, and not the number of effort 
        records.'''
        return len(self)
        
    def removeItems(self, efforts):
        ''' We override ObservableListObserver.removeItems because the default
            implementation is to remove the arguments from the original list,
            which in this case would mean removing efforts from a task list.
            Since that wouldn't work we remove the efforts from the tasks by
            hand. '''
        for effort in efforts:
            effort.task().removeEffort(effort)

    def extend(self, efforts):
        ''' We override ObservableListObserver.extend because the default
            implementation is to add the arguments to the original list,
            which in this case would mean adding efforts to a task list.
            Since that wouldn't work we add the efforts to the tasks by
            hand. '''
        for effort in efforts:
            effort.task().addEffort(effort)


class SingleTaskEffortList(patterns.ObservableListObserver, MaxDateTimeMixin):
    ''' SingleTaskEffortList filters an EffortList so it contains the efforts for 
        one task (including its children). '''
    
    # FIXME: SingleTaskEffortList is not a real ObservableListObserver because
    # it is observing a single task and not a list
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
        if notification.childAdded:
            notification.childAdded.registerObserver(self.onNotify)
        if notification.childRemoved:
            notification.childRemoved.removeObserver(self.onNotify)    

    def removeItems(self, efforts):
        ''' We override ObservableListObserver.removeItems because the default
            implementation is to remove the arguments from the original list,
            which in this case would mean removing efforts from a task.
            Since that wouldn't work we remove the efforts from the tasks by
            hand. '''
        for effort in efforts:
            effort.task().removeEffort(effort)

    def extend(self, efforts):
        ''' We override ObservableListObserver.extend because the default
            implementation is to add the arguments to the original list,
            which in this case would mean adding efforts to a task.
            Since that wouldn't work we add the efforts to the tasks by
            hand. '''
        for effort in efforts:
            effort.task().addEffort(effort)

