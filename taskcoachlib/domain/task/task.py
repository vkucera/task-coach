'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2009 Frank Niessink <frank@niessink.com>
Copyright (C) 2008 Jerome Laheurte <fraca7@free.fr>

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

from taskcoachlib import patterns
from taskcoachlib.domain import date, category, note, attachment


class Task(note.NoteOwner, attachment.AttachmentOwner, 
           category.CategorizableCompositeObject):
    def __init__(self, subject='', description='', dueDate=None, 
            startDate=None, completionDate=None, budget=None, 
            priority=0, id=None, hourlyFee=0,
            fixedFee=0, reminder=None, categories=None,
            efforts=None, shouldMarkCompletedWhenAllChildrenCompleted=None, 
            recurrence=None, *args, **kwargs):
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
        self._priority       = priority
        self._hourlyFee      = hourlyFee
        self._fixedFee       = fixedFee
        self._reminder       = reminder
        if recurrence is None:
            recurrence = date.Recurrence()
        self._recurrence     = recurrence
        self._shouldMarkCompletedWhenAllChildrenCompleted = \
            shouldMarkCompletedWhenAllChildrenCompleted
        for effort in self._efforts:
            effort.setTask(self)

    def __setstate__(self, state):
        super(Task, self).__setstate__(state)
        self.setStartDate(state['startDate'])
        self.setDueDate(state['dueDate'])
        self.setCompletionDate(state['completionDate'])
        self.setRecurrence(state['recurrence'])
        self.setReminder(state['reminder'])
        self.replaceChildren(state['children'])
        self.replaceParent(state['parent'])
        self.setEfforts(state['efforts'])
        self.setBudget(state['budget'])
        self.setCategories(state['categories'])
        self.setPriority(state['priority'])
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
            hourlyFee=self._hourlyFee, fixedFee=self._fixedFee, 
            recurrence=self._recurrence.copy(),
            reminder=self._reminder,
            shouldMarkCompletedWhenAllChildrenCompleted=\
                self._shouldMarkCompletedWhenAllChildrenCompleted))
        return state

    def __getcopystate__(self):
        state = super(Task, self).__getcopystate__()
        state.update(dict(dueDate=self._dueDate, 
            startDate=self._startDate, completionDate=self._completionDate, 
            efforts=[effort.copy() for effort in self._efforts], 
            budget=self._budget, priority=self._priority, 
            hourlyFee=self._hourlyFee, fixedFee=self._fixedFee, 
            recurrence=self._recurrence.copy(),
            reminder=self.reminder(), 
            shouldMarkCompletedWhenAllChildrenCompleted=\
                self._shouldMarkCompletedWhenAllChildrenCompleted))
        return state
        
    def allChildrenCompleted(self):
        ''' Return whether all children (non-recursively) are completed. '''
        children = self.children()
        return all(child.completed() for child in children) if children \
            else False        

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
        newTotalBudgetLeft = self.budgetLeft(recursive=True)
        if child.budget(recursive=True):
            self.notifyObserversOfTotalBudgetChange()
        if newTotalBudgetLeft != oldTotalBudgetLeft:
            self.notifyObserversOfTotalBudgetLeftChange()
        if child.timeSpent(recursive=True):
            self.notifyObserversOfTotalTimeSpentChange()
        if self.priority(recursive=True) != oldTotalPriority:
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
        if self.priority(recursive=True) != oldTotalPriority:
            self.notifyObserversOfTotalPriorityChange()
        if child.revenue(recursive=True):
            self.notifyObserversOfTotalRevenueChange()
        if child.isBeingTracked(recursive=True) and not \
            self.isBeingTracked(recursive=True):
            self.notifyObserversOfStopTracking(*child.activeEfforts(recursive=True))

    def dueDate(self, recursive=False):
        if recursive:
            childrenDueDates = [child.dueDate(recursive=True) for child in \
                                self.children() if not child.completed()]
            return min(childrenDueDates + [self._dueDate])
        else:
            return self._dueDate

    def setDueDate(self, dueDate):
        if dueDate != self._dueDate:
            self._dueDate = dueDate
            self.notifyObserversOfAttributeChange('task.dueDate', dueDate)

    def startDate(self, recursive=False):
        if recursive:
            childrenStartDates = [child.startDate(recursive=True) for child in \
                                  self.children() if not child.completed()]
            return min(childrenStartDates + [self._startDate])
        else:
            return self._startDate

    def setStartDate(self, startDate):
        if startDate != self._startDate:
            self._startDate = startDate
            self.notifyObserversOfAttributeChange('task.startDate', startDate)

    def timeLeft(self, recursive=False):
        return self.dueDate(recursive) - date.Today()
        
    def completionDate(self, recursive=False):
        if recursive:
            childrenCompletionDates = [child.completionDate(recursive=True) \
                for child in self.children() if child.completed()]
            return max(childrenCompletionDates + [self._completionDate])
        else:
            return self._completionDate

    def setCompletionDate(self, completionDate=None):
        completionDate = completionDate or date.Today()
        if completionDate != self._completionDate:
            if completionDate != date.Date() and self.recurrence():
                self.recur()
            else:
                parent = self.parent()
                if parent:
                    oldParentTotalPriority = parent.priority(recursive=True) 
                self._completionDate = completionDate
                self.notifyObserversOfAttributeChange('task.completionDate', 
                    completionDate)
                if parent and parent.priority(recursive=True) != \
                              oldParentTotalPriority:
                    parent.notifyObserversOfTotalPriorityChange()                    
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
            self.notifyObserversOfAttributeChange('task.effort.add', effort)
            if effort.isBeingTracked() and not wasTracking:
                self.notifyObserversOfStartTracking(effort)
            self.notifyObserversOfTimeSpentChange(effort)
        
    def removeEffort(self, effort):
        if effort in self._efforts:
            self._efforts.remove(effort)
            self.notifyObserversOfAttributeChange('task.effort.remove', effort)
            if effort.isBeingTracked() and not self.isBeingTracked():
                self.notifyObserversOfStopTracking(effort)
            self.notifyObserversOfTimeSpentChange(effort)

    def setEfforts(self, efforts):
        self._efforts = efforts # FIXME: no notification?

    def timeSpent(self, recursive=False):
        return sum((effort.duration() for effort in self.efforts(recursive)), 
                   date.TimeDelta())

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
        return budget - self.timeSpent(recursive) if budget else budget
    
    def notifyObserversOfColorChange(self, color):
        super(Task, self).notifyObserversOfColorChange(color)
        self.notifyEffortObserversOfColorChange(color)
        
    def notifyEffortObserversOfColorChange(self, color):
        from taskcoachlib.domain import effort # prevent circular import
        event = patterns.Event(effort.Effort.colorChangedEventType())
        for task in [self] + self.childrenWithoutOwnColor():
            for eachEffort in task.efforts():
                event.addSource(eachEffort, color)
        self.notifyObservers(event)

    def notifyObserversOfBudgetChange(self):
        self.notifyObserversOfAttributeChange('task.budget', self.budget())
        self.notifyObserversOfTotalBudgetChange()

    def notifyObserversOfTotalBudgetChange(self):
        self.notifyObserversOfTotalAttributeChange('task.totalBudget', 
                                                   Task.budget)

    def notifyObserversOfBudgetLeftChange(self):
        self.notifyObserversOfAttributeChange('task.budgetLeft', 
                                              self.budgetLeft())
        self.notifyObserversOfTotalBudgetLeftChange()
        
    def notifyObserversOfTotalBudgetLeftChange(self):
        self.notifyObserversOfTotalAttributeChange('task.totalBudgetLeft', 
                                                   Task.budgetLeft)
        
    def notifyObserversOfTimeSpentChange(self, changedEffort):
        self.notifyObserversOfAttributeChange('task.timeSpent', 
                                              self.timeSpent())
        self.notifyObserversOfTotalTimeSpentChange(changedEffort)
        if self.budget():
            self.notifyObserversOfBudgetLeftChange()
        elif self.budget(recursive=True):
            self.notifyObserversOfTotalBudgetLeftChange()
        if self.hourlyFee() > 0:
            self.notifyObserversOfRevenueChange()
    
    @classmethod
    def totalTimeSpentChangedEventType(class_):
        return 'task.totalTimeSpent'

    def notifyObserversOfTotalTimeSpentChange(self, changedEffort=None):
        self.notifyObserversOfTotalAttributeChange( \
            self.totalTimeSpentChangedEventType(), changedEffort)

    @classmethod
    def trackStartEventType(class_):
        return '%s.track.start'%class_

    def notifyObserversOfStartTracking(self, *trackedEfforts):
        self.notifyObserversOfTotalAttributeChange( \
            self.trackStartEventType(), *trackedEfforts)

    @classmethod
    def trackStopEventType(class_):
        return '%s.track.stop'%class_
    
    def notifyObserversOfStopTracking(self, *trackedEfforts):
        self.notifyObserversOfTotalAttributeChange( \
            self.trackStopEventType(), *trackedEfforts)
        
    # priority
    
    def priority(self, recursive=False):
        if recursive:
            childPriorities = [child.priority(recursive=True) \
                               for child in self.children() \
                               if not child.completed()]
            return max(childPriorities + [self._priority])
        else:
            return self._priority
        
    def setPriority(self, priority):
        if priority != self._priority:
            self._priority = priority
            self.notifyObserversOfPriorityChange()
        
    def notifyObserversOfPriorityChange(self):
        self.notifyObserversOfAttributeChange('task.priority', self.priority())
        self.notifyObserversOfTotalPriorityChange()

    def notifyObserversOfTotalPriorityChange(self):
        self.notifyObserversOfTotalAttributeChange('task.totalPriority', 
                                                   Task.priority)
        
    # revenue
    
    def hourlyFee(self, recursive=False):
        return self._hourlyFee
    
    def setHourlyFee(self, hourlyFee):
        if hourlyFee != self._hourlyFee:
            self._hourlyFee = hourlyFee
            self.notifyObserversOfHourlyFeeChange(hourlyFee)

    @classmethod
    def hourlyFeeChangedEventType(class_):
        return '%s.hourlyFee'%class_
            
    def notifyObserversOfHourlyFeeChange(self, hourlyFee):
        self.notifyObserversOfAttributeChange(self.hourlyFeeChangedEventType(),
                                              hourlyFee)
        if self.timeSpent() > date.TimeDelta():
            self.notifyObserversOfRevenueChange()
            self.notifyEffortObserversOfRevenueChange()

    def notifyEffortObserversOfRevenueChange(self):
        event = patterns.Event('effort.revenue')
        for effort in self.efforts():
            event.addSource(effort, effort.revenue())
        self.notifyObservers(event)
                
    def revenue(self, recursive=False):
        childRevenues = sum(child.revenue(recursive) for child in 
                            self.children()) if recursive else 0
        return self.timeSpent().hours() * self.hourlyFee() + self.fixedFee() + \
               childRevenues
    
    def fixedFee(self, recursive=False):
        childFixedFees = sum(child.fixedFee(recursive) for child in 
                             self.children()) if recursive else 0
        return self._fixedFee + childFixedFees
    
    def setFixedFee(self, fixedFee):
        if fixedFee != self._fixedFee:
            self._fixedFee = fixedFee
            self.notifyObserversOfFixedFeeChange(fixedFee)
            self.notifyObserversOfRevenueChange()

    def notifyObserversOfFixedFeeChange(self, fixedFee):
        self.notifyObserversOfAttributeChange('task.fixedFee', fixedFee)
        self.notifyObserversOfTotalAttributeChange('task.totalFixedFee', 
                                                   Task.fixedFee)

    def notifyObserversOfRevenueChange(self):
        self.notifyObserversOfAttributeChange('task.revenue', self.revenue())
        self.notifyObserversOfTotalRevenueChange()
                    
    def notifyObserversOfTotalRevenueChange(self):
        self.notifyObserversOfTotalAttributeChange('task.totalRevenue', 
                                                   Task.revenue)
        
    # reminder
    
    def reminder(self, recursive=False):
        return self._reminder

    def setReminder(self, reminderDateTime=None):
        if reminderDateTime == date.DateTime.max:
            reminderDateTime = None
        if reminderDateTime != self._reminder:
            self._reminder = reminderDateTime
            self.notifyObserversOfAttributeChange('task.reminder', self._reminder)
                    
    # Recurrence
    
    def recurrence(self, recursive=False):
        if not self._recurrence and recursive and self.parent():
            return self.parent().recurrence(recursive)
        else:
            return self._recurrence
        
    def setRecurrence(self, recurrence=None):
        recurrence = recurrence or date.Recurrence()
        if recurrence != self._recurrence:
            self._recurrence = recurrence
            self.notifyObserversOfAttributeChange('task.recurrence', recurrence)
            
    def recur(self):
        for child in self.children():
            if not child.recurrence():
                child.recur()
        self.setCompletionDate(date.Date())
        self.setStartDate(self.recurrence(recursive=True)(self.startDate(), next=False))
        self.setDueDate(self.recurrence(recursive=True)(self.dueDate(), next=False))
        if self.reminder():
            self.setReminder(self.recurrence(recursive=True)(self.reminder(), next=False))
        self.recurrence()(next=True)
                        
    # behavior
    
    # To experiment, this attribute is coded by means of a property, which
    # means you can set it like this: task.shouldMark... = True
    
    def __setShouldMarkCompletedWhenAllChildrenCompleted(self, newValue):
        if newValue == self._shouldMarkCompletedWhenAllChildrenCompleted:
            return
        self._shouldMarkCompletedWhenAllChildrenCompleted = newValue
        self.notifyObserversOfAttributeChange( \
            'task.setting.shouldMarkCompletedWhenAllChildrenCompleted', 
            newValue)

    def __getShouldMarkCompletedWhenAllChildrenCompleted(self):
        return self._shouldMarkCompletedWhenAllChildrenCompleted
    
    shouldMarkCompletedWhenAllChildrenCompleted = \
        property(fget=__getShouldMarkCompletedWhenAllChildrenCompleted,
                 fset=__setShouldMarkCompletedWhenAllChildrenCompleted)
    
    @classmethod
    def modificationEventTypes(class_):
        eventTypes = super(Task, class_).modificationEventTypes()
        return eventTypes + ['task.dueDate', 'task.startDate', 
                             'task.completionDate', 'task.effort.add', 
                             'task.effort.remove', 'task.budget', 
                             'task.priority', 
                             class_.hourlyFeeChangedEventType(), 
                             'task.fixedFee',
                             'task.reminder', 'task.recurrence',
                             'task.setting.shouldMarkCompletedWhenAllChildrenCompleted']
        
    # utilities
        
    def notifyObserversOfTotalAttributeChange(self, eventType, *getterOrValues):
        if callable(getterOrValues[0]):
            getter = lambda instance: (getterOrValues[0](instance, recursive=True),)
        else:
            getter = lambda instance: getterOrValues
        event = patterns.Event(eventType, self, *getter(self))
        for ancestor in self.ancestors():
            event.addSource(ancestor, *getter(ancestor))
        self.notifyObservers(event)

    def notifyObserversOfAttributeChange(self, eventType, attributeValue):
        event = patterns.Event(eventType, self, attributeValue)
        self.notifyObservers(event)
