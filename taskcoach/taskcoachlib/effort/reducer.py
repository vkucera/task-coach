import patterns, effort

class EffortReducer(patterns.ObservableListObserver):
    def notifyChange(self, changedEfforts):
        self.notifyRemove(changedEfforts)
        self.notifyAdd(changedEfforts)

    def notifyAdd(self, newEfforts):
        for newEffort in newEfforts:
            for compositeEffort in self:
                if self.effortFitsInComposite(compositeEffort, newEffort):
                    compositeEffort.append(newEffort)
                    break
            else:
                newComposite = effort.CompositeEffort([newEffort])
                self._extend([newComposite])

    def notifyRemove(self, removedEfforts):
        for removedEffort in removedEfforts:
            for compositeEffort in self:
                if removedEffort in compositeEffort:
                    compositeEffort.remove(removedEffort)
                    if len(compositeEffort) == 0:
                        self._removeItems([compositeEffort])
                    break                

    def effortFitsInComposite(self, compositeEffort, effort):
        return self.sameTask(compositeEffort, effort) and \
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
