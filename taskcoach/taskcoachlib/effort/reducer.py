import patterns, effort, sets, time, log

        
class EffortReducer(patterns.ObservableListObserver):     
    def __init__(self, *args, **kwargs):
        self.__taskAndTimeToCompositesMapping = {}
        self.__effortToCompositeMapping = {}
        super(EffortReducer, self).__init__(*args, **kwargs)
        
    def onNotify(self, notification, *args, **kwargs):
        self.stopNotifying()
        effortsRemoved, changedComposites1 = self.removeEfforts(notification.itemsRemoved + notification.itemsChanged)
        effortsAdded, changedComposites2 = self.addEfforts(notification.itemsAdded + notification.itemsChanged)
        self.startNotifying()
        changedComposites = changedComposites1 + changedComposites2
        self.notifyObservers(patterns.observer.Notification(self, 
            itemsAdded=effortsAdded, itemsRemoved=effortsRemoved, 
            itemsChanged=changedComposites))
                
    def addEfforts(self, newEfforts):
        newComposites = []
        changedComposites = []
        for newEffort in newEfforts:
            for task in [newEffort.task()] + newEffort.task().ancestors():
                key = (task.id(), self.timePeriod(newEffort))
                composite = self.__taskAndTimeToCompositesMapping.setdefault(key, effort.CompositeEffort(task, *self.timePeriod(newEffort)))
                composite.append(newEffort)
                if len(composite) == 1:
                    newComposites.append(composite)
                else:
                    changedComposites.append(composite)
                self.__effortToCompositeMapping.setdefault(newEffort, []).append(composite)
        self._extend(newComposites)
        return newComposites, changedComposites

    def removeEfforts(self, removedEfforts):
        removedComposites = []
        changedComposites = []
        for removedEffort in removedEfforts:
            composites = self.__effortToCompositeMapping.pop(removedEffort)
            for composite in composites:
                composite.remove(removedEffort)
                if len(composite) == 0:
                    removedComposites.append(composite)
                    if composite in changedComposites:
                        changedComposites.remove(composite)
                    key = (composite.task().id(), self.timePeriod(composite))
                    del self.__taskAndTimeToCompositesMapping[key]
                else:
                    changedComposites.append(composite)            
        self._removeItems(removedComposites)
        return removedComposites, changedComposites


class EffortPerDay(EffortReducer):        
    def timePeriod(self, effort):
        return effort.getStart().startOfDay(), effort.getStart().endOfDay()

class EffortPerWeek(EffortReducer): 
    def timePeriod(self, effort):
        return effort.getStart().startOfWeek(), effort.getStart().endOfWeek()

class EffortPerMonth(EffortReducer):
    def timePeriod(self, effort):
        return effort.getStart().startOfMonth(), effort.getStart().endOfMonth()
        
