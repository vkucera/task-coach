import patterns, effort, sets

class EffortReducer(patterns.ObservableListObserver):
    def __init__(self, *args, **kwargs):
        super(EffortReducer, self).__init__(*args, **kwargs)
        self.addEfforts(self.original())
        
    def onNotify(self, notification, *args, **kwargs):
        self.stopNotifying()
        effortsRemoved, changedComposites1 = self.removeEfforts(notification.effortsRemoved + notification.effortsChanged)
        effortsAdded, changedComposites2 = self.addEfforts(notification.effortsAdded + notification.effortsChanged)
        self.startNotifying()
        changedComposites = changedComposites1 + changedComposites2
        self.notifyObservers(patterns.observer.Notification(self, 
            effortsAdded=effortsAdded, effortsRemoved=effortsRemoved, 
            effortsChanged=changedComposites))
        
    def addEfforts(self, newEfforts):
        newComposites = []
        changedComposites = []
        for newEffort in newEfforts:
            for task in [newEffort.task()] + newEffort.task().ancestors():
                for compositeEffort in self + newComposites:
                    if self.effortFitsInComposite(compositeEffort, newEffort, task):
                        compositeEffort.append(newEffort)
                        if compositeEffort not in changedComposites:
                            changedComposites.append(compositeEffort)
                        break
                else:
                    newComposites.append(effort.CompositeEffort(task, [newEffort]))
        self._extend(newComposites)
        return newComposites, changedComposites

    def removeEfforts(self, removedEfforts):
        changedComposites = []
        for removedEffort in removedEfforts:
            for compositeEffort in self:
                if removedEffort in compositeEffort:
                    compositeEffort.remove(removedEffort)
                    if compositeEffort not in changedComposites:
                        changedComposites.append(compositeEffort)
        removedComposites = [compositeEffort for compositeEffort in self if len(compositeEffort) == 0]
        self._removeItems(removedComposites)
        return removedComposites, changedComposites
                

    def effortFitsInComposite(self, compositeEffort, effort, task):
        return compositeEffort.task() == task and \
            self.sameTimePeriod(compositeEffort, effort)
            
    def sameTask(self, effort1, effort2):
        return effort1.task() == effort2.task()

    def sameTimePeriod(self, compositeEffort, effort):
        raise NotImplementedError

    def sameYear(self, effort1, effort2):
        return effort1.getStart().year == effort2.getStart().year

    def sameMonth(self, effort1, effort2):
        return self.sameYear(effort1, effort2) and \
            effort1.getStart().month == effort2.getStart().month

    def sameWeek(self, effort1, effort2):
        return self.sameYear(effort1, effort2) and \
            effort1.getStart().weeknumber() == effort2.getStart().weeknumber()
    
    def sameDay(self, effort1, effort2):
        return effort1.getStart().date() == effort2.getStart().date()


class EffortPerDay(EffortReducer):
    def sameTimePeriod(self, compositeEffort, effort):
        return self.sameDay(compositeEffort, effort)
        

class EffortPerWeek(EffortReducer): 
    def sameTimePeriod(self, compositeEffort, effort):
        return self.sameWeek(compositeEffort, effort)        


class EffortPerMonth(EffortReducer):
    def sameTimePeriod(self, compositeEffort, effort):
        return self.sameMonth(compositeEffort, effort)
