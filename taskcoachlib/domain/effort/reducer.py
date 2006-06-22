import patterns, effort, sets

# FIXME: EffortAggregator would be a better name for this
# file and this class
# TODO: give CompositeEffort a __hash__ method?

class EffortReducer(patterns.ObservableListObserver):
    ''' This class observers an EffortList and aggregates the individual effort
        records to CompositeEfforts, e.g. per day or per week. This class is 
        abstract. Subclasses should implement timePeriod(effort).'''
    
    def __init__(self, *args, **kwargs):
        self.__taskAndTimeToCompositesMapping = {}
        self.__effortToCompositeMapping = {}
        super(EffortReducer, self).__init__(*args, **kwargs)
        
    def onNotify(self, notification, *args, **kwargs):
        self.stopNotifying()
        compositesChangedKeys = self.removeEfforts(notification.itemsRemoved + notification.itemsChanged)
        compositesAdded, compositesChangedKeys = self.addEfforts(notification.itemsAdded + notification.itemsChanged, compositesChangedKeys)
        compositesRemoved, compositesChanged = self.__removeEmptyCompositeEfforts(compositesChangedKeys)
        self.startNotifying()
        self.notifyObservers(patterns.observer.Notification(self, 
            itemsAdded=compositesAdded, 
            itemsRemoved=compositesRemoved, 
            itemsChanged=compositesChanged))
                
    def addEfforts(self, newEfforts, changedCompositesKeys):
        newComposites = []
        for newEffort in newEfforts:
            for task in [newEffort.task()] + newEffort.task().ancestors():
                key = (task.id(), self.timePeriod(newEffort))
                if key in self.__taskAndTimeToCompositesMapping:
                    composite = self.__taskAndTimeToCompositesMapping[key]
                    changedCompositesKeys.add(key)
                else:
                    composite = self.__taskAndTimeToCompositesMapping[key] = effort.CompositeEffort(task, *self.timePeriod(newEffort))            
                    newComposites.append(composite)
                composite.append(newEffort)
                self.__effortToCompositeMapping.setdefault(newEffort, []).append(composite)
        self._extend(newComposites)
        return newComposites, changedCompositesKeys

    def removeEfforts(self, removedEfforts):
        changedCompositesKeys = sets.Set()
        for removedEffort in removedEfforts:
            try:
                composites = self.__effortToCompositeMapping.pop(removedEffort)
            except KeyError:
                continue # Huh, apparently removedEffort has been removed earlier or was never added?
            for composite in composites:
                composite.remove(removedEffort)
                changedCompositesKeys.add(self.__key(composite))
        return changedCompositesKeys
   
    def __removeEmptyCompositeEfforts(self, changedOrRemovedCompositesKeys):
        composites = [self.__taskAndTimeToCompositesMapping[key] \
                      for key in changedOrRemovedCompositesKeys]
        removedComposites = [composite for composite in composites \
                             if len(composite) == 0]
        changedComposites = [composite for composite in composites \
                             if len(composite) > 0]
        for composite in removedComposites:
            del self.__taskAndTimeToCompositesMapping[self.__key(composite)]
        self._removeItems(removedComposites)
        return removedComposites, changedComposites
            
    def __key(self, composite):
        return (composite.task().id(), self.timePeriod(composite))
    
    def __keysToComposites(self, keys):
        return [self.__taskAndTimeToCompositesMapping[key] for key in keys]
        
    def timePeriod(self, effort):
        raise NotImplementedError


class EffortPerDay(EffortReducer):        
    def timePeriod(self, effort):
        return effort.getStart().startOfDay(), effort.getStart().endOfDay()


class EffortPerWeek(EffortReducer): 
    def timePeriod(self, effort):
        return effort.getStart().startOfWeek(), effort.getStart().endOfWeek()


class EffortPerMonth(EffortReducer):
    def timePeriod(self, effort):
        return effort.getStart().startOfMonth(), effort.getStart().endOfMonth()
        
