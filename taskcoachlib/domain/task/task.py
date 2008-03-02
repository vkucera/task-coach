'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>

Task Coach is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Task Coach is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import patterns, time, copy
from domain import date, category


class Task(category.CategorizableCompositeObject):
    def __init__(self, subject='', description='', dueDate=None, 
            startDate=None, completionDate=None, budget=None, 
            priority=0, id=None, hourlyFee=0,
            fixedFee=0, reminder=None, attachments=None, categories=None,
            efforts=None,
            shouldMarkCompletedWhenAllChildrenCompleted=None, 
            recurrence='', recurrenceCount=0, maxRecurrenceCount=0,
            *args, **kwargs):
        kwargs['id'] = id
        kwargs['subject'] = subject
        kwargs['description'] = description
        kwargs['categories'] = categories
        super(Task, self).__init__(*args, **kwargs)
        self._dueDate        = dueDate or date.Date()
        self._startDate      = startDate or date.Today()
        self._completionDate = completionDate or date.Date()
        self._budget         = budget or date.TimeDelta()
        self._efforts        = efforts or []
        for effort in self._efforts:
            effort.setTask(self)
        self._priority       = priority
        self._hourlyFee      = hourlyFee
        self._fixedFee       = fixedFee
        self._reminder       = reminder
        self._attachments    = attachments or []
        self._recurrence     = recurrence
        self._recurrenceCount = recurrenceCount
        self._maxRecurrenceCount = maxRecurrenceCount
        self._shouldMarkCompletedWhenAllChildrenCompleted = \
            shouldMarkCompletedWhenAllChildrenCompleted
            
    def __setstate__(self, state):
        super(Task, self).__setstate__(state)
        self.setStartDate(state['startDate'])
        self.setDueDate(state['dueDate'])
        self.setCompletionDate(state['completionDate'])
        self.setRecurrence(state['recurrence'])
        self.setRecurrenceCount(state['recurrenceCount'])
        self.setMaxRecurrenceCount(state['maxRecurrenceCount'])
        self.replaceChildren(state['children'])
        self.replaceParent(state['parent'])
        self.setEfforts(state['efforts'])
        self.setBudget(state['budget'])
        self.setCategories(state['categories'])
        self.setPriority(state['priority'])
        self.setAttachments(state['attachments'])
        self.setHourlyFee(state['hourlyFee'])
        self.setFixedFee(state['fixedFee'])
        self.shouldMarkCompletedWhenAllChildrenCompleted = \
            state['shouldMarkCompletedWhenAllChildrenCompleted']
            
    def __getstate__(self):
        state = super(Task, self).__getstate__()
        state.update(dict(dueDate=self._dueDate, 
            startDate=self._startDate, completionDate=self._completionDate, 
            children=self.children(), parent=self.parent(), 
            efforts=self._efforts, budget=self._budget,
            categories=set(self._categories), priority=self._priority, 
            attachments=self._attachments[:], hourlyFee=self._hourlyFee, 
            fixedFee=self._fixedFee, recurrence=self._recurrence,
            recurrenceCount=self._recurrenceCount, 
            maxRecurrenceCount=self._maxRecurrenceCount,
            shouldMarkCompletedWhenAllChildrenCompleted=\
                self._shouldMarkCompletedWhenAllChildrenCompleted))
        return state
        
    def allChildrenCompleted(self):
        if not self.children():
            return False
        for child in self.children():
            if not child.completed():
                return False
        return True

    def copy(self):
        ''' Copy constructor '''
        return self.__class__(self.subject(), self.description(), 
            self.dueDate(), self.startDate(), self.completionDate(),
            parent=self.parent(), 
            budget=self.budget(), priority=self.priority(), 
            categories=set(self.categories()), fixedFee=self.fixedFee(),
            hourlyFee=self.hourlyFee(), attachments=self.attachments()[:],
            reminder=self.reminder(), recurrence=self.recurrence(),
            recurrenceCount=self.recurrenceCount(), 
            maxRecurrenceCount=self.maxRecurrenceCount(),
            shouldMarkCompletedWhenAllChildrenCompleted=\
                self.shouldMarkCompletedWhenAllChildrenCompleted,
            children=[child.copy() for child in self.children()])
    
    def newChild(self, subject='New subtask'):
        ''' Subtask constructor '''
        return super(Task, self).newChild(subject=subject, 
            dueDate=self.dueDate(),
            startDate=max(date.Today(), self.startDate()), parent=self)

    def addChild(self, child):
        if child in self.children():
            return
        oldTotalBudgetLeft = self.budgetLeft(recursive=True)
        oldTotalPriority = self.priority(recursive=True)
        super(Task, self).addChild(child)
        self.notifyObservers(patterns.Event(self, Task.addChildEventType(), child))
        newTotalBudgetLeft = self.budgetLeft(recursive=True)
        if child.budget(recursive=True):
            self.notifyObserversOfTotalBudgetChange()
        if newTotalBudgetLeft != oldTotalBudgetLeft:
            self.notifyObserversOfTotalBudgetLeftChange()
        if child.timeSpent(recursive=True):
            self.notifyObserversOfTotalTimeSpentChange()
        if child.priority(recursive=True) > oldTotalPriority:
            self.notifyObserversOfTotalPriorityChange()
        if child.revenue(recursive=True):
            self.notifyObserversOfTotalRevenueChange()
        if child.isBeingTracked(recursive=True):
            self.notifyObserversOfStartTracking(*child.activeEfforts(recursive=True))

    def removeChild(self, child):
        if child not in self.children():
            return
        oldTotalBudgetLeft = self.budgetLeft(recursive=True)
        oldTotalPriority = self.priority(recursive=True)
        super(Task, self).removeChild(child)
        newTotalBudgetLeft = self.budgetLeft(recursive=True)
        if child.budget(recursive=True):
            self.notifyObserversOfTotalBudgetChange()
        if newTotalBudgetLeft != oldTotalBudgetLeft:
            self.notifyObserversOfTotalBudgetLeftChange()
        if child.timeSpent(recursive=True):
            self.notifyObserversOfTotalTimeSpentChange()
        if child.priority(recursive=True) == oldTotalPriority:
            self.notifyObserversOfTotalPriorityChange()
        if child.revenue(recursive=True):
            self.notifyObserversOfTotalRevenueChange()
        if child.isBeingTracked(recursive=True) and not \
            self.isBeingTracked(recursive=True):
            self.notifyObserversOfStopTracking(*child.activeEfforts(recursive=True))

    def dueDate(self, recursive=False):
        if recursive:
            childrenDueDates = [child.dueDate(recursive=True) for child in self.children() if not child.completed()]
            return min(childrenDueDates + [self._dueDate])
        else:
            return self._dueDate

    def setDueDate(self, dueDate):
        if dueDate != self._dueDate:
            self._dueDate = dueDate
            self.notifyObservers(patterns.Event(self, 'task.dueDate', dueDate))

    def startDate(self, recursive=False):
        if recursive:
            childrenStartDates = [child.startDate(recursive=True) for child in self.children() if not child.completed()]
            return min(childrenStartDates+[self._startDate])
        else:
            return self._startDate

    def setStartDate(self, startDate):
        if startDate != self._startDate:
            self._startDate = startDate
            self.notifyObservers(patterns.Event(self, 'task.startDate', 
                startDate))

    def timeLeft(self, recursive=False):
        return self.dueDate(recursive) - date.Today()
        
    def completionDate(self, recursive=False):
        if recursive:
            childrenCompletionDates = [child.completionDate(recursive=True) \
                for child in self.children() if child.completed()]
            return max(childrenCompletionDates+[self._completionDate])
        else:
            return self._completionDate

    def setCompletionDate(self, completionDate=None):
        completionDate = completionDate or date.Today()
        if completionDate != self._completionDate:
            if completionDate != date.Date() and self.recurrence():
                self.recur()
            else:
                self._completionDate = completionDate
                self.notifyObservers(patterns.Event(self, 'task.completionDate', 
                    completionDate))
                if completionDate != date.Date():
                    self.setReminder(None)
        
    def completed(self):
        return self.completionDate() != date.Date()

    def overdue(self):
        return self.dueDate() < date.Today() and not self.completed()

    def inactive(self):
        return (self.startDate() > date.Today()) and not self.completed()
        
    def active(self):
        return not self.inactive() and not self.completed()

    def dueToday(self):
        return (self.dueDate() == date.Today() and not self.completed())

    def dueTomorrow(self):
        return (self.dueDate() == date.Tomorrow() and not self.completed())
    
   # effort related methods:

    def efforts(self, recursive=False):
        childEfforts = []
        if recursive:
            for child in self.children():
                childEfforts.extend(child.efforts(recursive=True))
        return self._efforts + childEfforts

    def activeEfforts(self, recursive=False):
        return [effort for effort in self.efforts(recursive) \
            if effort.isBeingTracked()]

    def isBeingTracked(self, recursive=False):
        return self.activeEfforts(recursive)
        
    def addEffort(self, effort):
        wasTracking = self.isBeingTracked()
        if effort not in self._efforts:
            self._efforts.append(effort)
            self.notifyObservers(patterns.Event(self, 'task.effort.add', 
                effort))
            if effort.isBeingTracked() and not wasTracking:
                self.notifyObserversOfStartTracking(effort)
            self.notifyObserversOfTimeSpentChange(effort)
        
    def removeEffort(self, effort):
        if effort in self._efforts:
            self._efforts.remove(effort)
            self.notifyObservers(patterns.Event(self, 'task.effort.remove', 
                effort))
            if effort.isBeingTracked() and not self.isBeingTracked():
                self.notifyObserversOfStopTracking(effort)
            self.notifyObserversOfTimeSpentChange(effort)

    def setEfforts(self, efforts):
        self._efforts = efforts # FIXME: no notification?

    def timeSpent(self, recursive=False):
        if recursive:
            return self._myTimeSpent() + self._childrenTimeSpent()
        else:
            return self._myTimeSpent()
    
    def stopTracking(self):
        stoppedEfforts = []
        for effort in self.activeEfforts():
            effort.setStop()
            stoppedEfforts.append(effort)
        return stoppedEfforts
                
    def budget(self, recursive=False):
        result = self._budget
        if recursive:
            for task in self.children():
                result += task.budget(recursive)
        return result
        
    def setBudget(self, budget):
        if budget != self._budget:
            self._budget = budget
            self.notifyObserversOfBudgetChange()
            self.notifyObserversOfBudgetLeftChange()
        
    def budgetLeft(self, recursive=False):
        budget = self.budget(recursive)
        if budget:
            return budget - self.timeSpent(recursive)
        else:
            return budget

    def _myTimeSpent(self):
        return sum([effort.duration() for effort in self.efforts()], 
            date.TimeDelta())
    
    def _childrenTimeSpent(self):
        return sum([child.timeSpent(recursive=True) \
            for child in self.children()], date.TimeDelta())

    def notifyObserversOfBudgetChange(self):
        self.notifyObservers(patterns.Event(self, 'task.budget', self.budget()))
        self.notifyObserversOfTotalBudgetChange()

    def notifyObserversOfTotalBudgetChange(self):
        self.notifyObservers(patterns.Event(self, 'task.totalBudget',
            self.budget(recursive=True)))
        parent = self.parent()
        if parent: 
            parent.notifyObserversOfTotalBudgetChange()

    def notifyObserversOfBudgetLeftChange(self):
        self.notifyObservers(patterns.Event(self, 'task.budgetLeft',
            self.budgetLeft()))
        self.notifyObserversOfTotalBudgetLeftChange()
        
    def notifyObserversOfTotalBudgetLeftChange(self):
        self.notifyObservers(patterns.Event(self, 'task.totalBudgetLeft', 
            self.budgetLeft(recursive=True)))
        parent = self.parent()
        if parent: 
            parent.notifyObserversOfTotalBudgetLeftChange()
        
    def notifyObserversOfTimeSpentChange(self, changedEffort):
        self.notifyObservers(patterns.Event(self, 'task.timeSpent', 
            self.timeSpent()))
        self.notifyObserversOfTotalTimeSpentChange(changedEffort)
        if self.budget():
            self.notifyObserversOfBudgetLeftChange()
        elif self.budget(recursive=True):
            self.notifyObserversOfTotalBudgetLeftChange()
        if self.hourlyFee() > 0:
            self.notifyObserversOfRevenueChange()
    
    def totalTimeSpentChangedEventType(self):
        return 'task(%s).totalTimeSpent'%self.id()

    def notifyObserversOfTotalTimeSpentChange(self, changedEffort=None):
        totalTimeSpent = self.timeSpent(recursive=True)
        self.notifyObservers(patterns.Event(self, 'task.totalTimeSpent', 
            totalTimeSpent))
        self.notifyObservers(patterns.Event(self, 
            self.totalTimeSpentChangedEventType(), changedEffort))
        parent = self.parent()
        if parent: 
            parent.notifyObserversOfTotalTimeSpentChange(changedEffort)

    def trackStartEventType(self):
        return 'task(%s).track.start'%self.id()

    def notifyObserversOfStartTracking(self, *trackedEfforts):
        # Notify observers interested in any task that starts tracking effort
        self.notifyObservers(patterns.Event(self, 'task.track.start',
            *trackedEfforts))
        # Notify observers interested in this task
        self.notifyObservers(patterns.Event(self, self.trackStartEventType(),
            *trackedEfforts))
        parent = self.parent()
        if parent: 
            parent.notifyObserversOfStartTracking(*trackedEfforts)

    def trackStopEventType(self):
        return 'task(%s).track.stop'%self.id()
    
    def notifyObserversOfStopTracking(self, *trackedEfforts):
        self.notifyObservers(patterns.Event(self, 'task.track.stop',
            *trackedEfforts))
        self.notifyObservers(patterns.Event(self, self.trackStopEventType(),
            *trackedEfforts))
        parent = self.parent()
        if parent: 
            parent.notifyObserversOfStopTracking(*trackedEfforts)

    # priority
    
    def priority(self, recursive=False):
        if recursive:
            childPriorities = [child.priority(recursive=True) \
                               for child in self.children()]
            return max(childPriorities + [self._priority])
        else:
            return self._priority
        
    def setPriority(self, priority):
        if priority != self._priority:
            self._priority = priority
            self.notifyObserversOfPriorityChange()
        
    def notifyObserversOfPriorityChange(self):
        self.notifyObservers(patterns.Event(self, 'task.priority', 
            self.priority()))
        self.notifyObserversOfTotalPriorityChange()

    def notifyObserversOfTotalPriorityChange(self):
        myTotalPriority = self.priority(recursive=True)
        self.notifyObservers(patterns.Event(self, 'task.totalPriority', 
            myTotalPriority))
        parent = self.parent()
        if parent and myTotalPriority == parent.priority(recursive=True):
            parent.notifyObserversOfTotalPriorityChange()

    # revenue
    
    def hourlyFee(self, recursive=False):
        return self._hourlyFee
    
    def setHourlyFee(self, hourlyFee):
        if hourlyFee != self._hourlyFee:
            self._hourlyFee = hourlyFee
            self.notifyObservers(patterns.Event(self, 'task.hourlyFee',
                hourlyFee))
            if self.timeSpent() > date.TimeDelta():
                self.notifyObserversOfRevenueChange()
        
    def revenue(self, recursive=False):
        if recursive:
            childRevenues = sum(child.revenue(recursive) for child in self.children())
        else:
            childRevenues = 0
        return self.timeSpent().hours() * self.hourlyFee() + self.fixedFee() + childRevenues
    
    def fixedFee(self, recursive=False):
        if recursive:
            childFixedFees = sum(child.fixedFee(recursive) for child in self.children())
        else:
            childFixedFees = 0
        return self._fixedFee + childFixedFees
    
    def setFixedFee(self, fixedFee):
        if fixedFee != self._fixedFee:
            self._fixedFee = fixedFee
            self.notifyObservers(patterns.Event(self, 'task.fixedFee',
                fixedFee))
            self.notifyObserversOfRevenueChange()

    def notifyObserversOfRevenueChange(self):
        self.notifyObservers(patterns.Event(self, 'task.revenue', 
            self.revenue()))
        self.notifyObserversOfTotalRevenueChange()
        
    def notifyObserversOfTotalRevenueChange(self):
        self.notifyObservers(patterns.Event(self, 'task.totalRevenue', 
            self.revenue(recursive=True)))
        parent = self.parent()
        if parent:
            parent.notifyObserversOfTotalRevenueChange()
        
    # reminder
    
    def reminder(self, recursive=False):
        return self._reminder

    def setReminder(self, reminderDateTime=None):
        if reminderDateTime == date.DateTime.max:
            reminderDateTime = None
        if reminderDateTime != self._reminder:
            self._reminder = reminderDateTime
            self.notifyObservers(patterns.Event(self, 'task.reminder', 
                self._reminder))
        
    # attachments
    
    def attachments(self):
        return self._attachments
        
    def addAttachments(self, *attachments):
        if attachments:
            self._attachments.extend(attachments)
            self.notifyObservers(patterns.Event(self, 'task.attachment.add', 
                *attachments))
        
    def removeAttachments(self, *attachments):
        attachmentsRemoved = []
        for attachment in attachments:
            if attachment in self._attachments:
                self._attachments.remove(attachment)
                attachmentsRemoved.append(attachment)
        if attachmentsRemoved:
            self.notifyObservers(patterns.Event(self, 'task.attachment.remove', 
                *attachmentsRemoved))
            
    def removeAllAttachments(self):
        self.removeAttachments(*self._attachments)
            
    def setAttachments(self, attachments):
        self._attachments = attachments # FIXME: no notification?

    # Recurrence
    
    def recurrence(self, recursive=False):
        if not self._recurrence and recursive and self.parent():
            return self.parent().recurrence(recursive)
        else:
            return self._recurrence
        
    def setRecurrence(self, recurrence=''):
        self._recurrence = recurrence

    def nextRecurrence(self, aDate):
        return date.next(aDate, self.recurrence(True))
    
    def recur(self):
        self._recurrenceCount += 1
        self.setCompletionDate(date.Date())
        self.setStartDate(self.nextRecurrence(self.startDate()))
        self.setDueDate(self.nextRecurrence(self.dueDate()))
        for child in self.children():
            if not child.recurrence():
                child.recur()
        if self.maxRecurrenceCount() and self.recurrenceCount() >= self.maxRecurrenceCount():
            self.setRecurrence()
            
    def recurrenceCount(self):
        return self._recurrenceCount
    
    def setRecurrenceCount(self, recurrenceCount):
        self._recurrenceCount = recurrenceCount

    def maxRecurrenceCount(self):
        return self._maxRecurrenceCount

    def setMaxRecurrenceCount(self, maxRecurrenceCount):
        self._maxRecurrenceCount = maxRecurrenceCount
    
    # behavior
    
    # To experiment, this attribute is coded by means of a property, which
    # means you can set it like this: task.shouldMark... = True
    
    def __setShouldMarkCompletedWhenAllChildrenCompleted(self, newValue):
        if newValue == self._shouldMarkCompletedWhenAllChildrenCompleted:
            return
        self._shouldMarkCompletedWhenAllChildrenCompleted = newValue
        self.notifyObservers(patterns.Event(self,
            'task.setting.shouldMarkCompletedWhenAllChildrenCompleted',
            newValue))

    def __getShouldMarkCompletedWhenAllChildrenCompleted(self):
        return self._shouldMarkCompletedWhenAllChildrenCompleted
    
    shouldMarkCompletedWhenAllChildrenCompleted = \
        property(fget=__getShouldMarkCompletedWhenAllChildrenCompleted,
                 fset=__setShouldMarkCompletedWhenAllChildrenCompleted)

