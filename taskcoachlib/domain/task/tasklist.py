import patterns, wx
from i18n import _
import domain.date as date
import task

def newTaskMenuText():
    # There is a bug in wxWidget/wxPython on the Mac that causes the 
    # INSERT accelerator to be mapped so some other key sequence ('c' in
    # this case) so that whenever that key sequence is typed, this command
    # is invoked. Hence, we use a different accelarator on the Mac.
    menuText = _('&New task...')
    if '__WXMAC__' in wx.PlatformInfo:
        menuText += u'\tCtrl+N'
    else:
        menuText += u'\tCtrl+INS'
    return menuText

            
class TaskList(patterns.CompositeSet):
    # FIXME: TaskList should be called TaskCollection or TaskSet

    newItemMenuText = newTaskMenuText()
    newItemHelpText = _('Insert a new task')
    editItemMenuText = _('&Edit task...')
    editItemHelpText = _('Edit the selected task')
    deleteItemMenuText= _('&Delete task\tCtrl+DEL')
    deleteItemHelpText= _('Delete the selected task(s)')
    
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