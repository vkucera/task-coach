import patterns
from i18n import _
import domain.date as date
import task

            
class TaskList(patterns.CompositeSet):
    # FIXME: TaskList should be called TaskCollection or TaskSet

    def _nrInterestingTasks(self, isInteresting):
        interestingTasks = [task for task in self if isInteresting(task)]
        return len(interestingTasks)

    def nrCompleted(self):
        return self._nrInterestingTasks(task.Task.completed)

    def nrOverdue(self):
        return self._nrInterestingTasks(task.Task.overdue)

    def nrInactive(self):
        return self._nrInterestingTasks(task.Task.inactive)

    def nrDueToday(self):
        return self._nrInterestingTasks(task.Task.dueToday)
    
    def nrBeingTracked(self):
        return self._nrInterestingTasks(task.Task.isBeingTracked)

    def allCompleted(self):
        nrCompleted = self.nrCompleted()
        return nrCompleted > 0 and nrCompleted == len(self)
            
    def efforts(self):
        result = []
        for task in self:
            result.extend(task.efforts())
        return result
    
    def __allDates(self):        
        realDates = [aDate for task in self 
            for aDate in (task.startDate(), task.dueDate(), task.completionDate()) 
            if aDate != date.Date()]
        if realDates:
            return realDates
        else:
            return [date.Date()]
            
    def minDate(self):      
        return min(self.__allDates())
          
    def maxDate(self):
        return max(self.__allDates())
        
    def originalLength(self):
        ''' Provide a way for bypassing the __len__ method of decorators. '''
        return len(self)

        
class SingleTaskList(TaskList):
    pass