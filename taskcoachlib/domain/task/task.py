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

    def __setstate__(self, state, event=None):
        notify = event is None
        event = event or patterns.Event()
        event = super(Task, self).__setstate__(state, event)
        event = self.setStartDate(state['startDate'], event)
        event = self.setDueDate(state['dueDate'], event)
        event = self.setCompletionDate(state['completionDate'], event)
        event = self.setRecurrence(state['recurrence'], event)
        event = self.setReminder(state['reminder'], event)
        event = self.setEfforts(state['efforts'], event)
        event = self.setBudget(state['budget'], event)
        event = self.setPriority(state['priority'], event)
        event = self.setHourlyFee(state['hourlyFee'], event)
        event = self.setFixedFee(state['fixedFee'], event)
        event = self.setShouldMarkCompletedWhenAllChildrenCompleted( \
            state['shouldMarkCompletedWhenAllChildrenCompleted'], event)
        if notify:
            event.send()
        else:
            return event
        
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

    def addChild(self, child, event=None):
        if child in self.children():
            return event
        notify = event is None
        event = event or patterns.Event()
        oldTotalBudgetLeft = self.budgetLeft(recursive=True)
        oldTotalPriority = self.priority(recursive=True)
        super(Task, self).addChild(child, event)
        newTotalBudgetLeft = self.budgetLeft(recursive=True)
        if child.budget(recursive=True):
            event = self.totalBudgetEvent(event)
        if newTotalBudgetLeft != oldTotalBudgetLeft:
            event = self.totalBudgetLeftEvent(event)
        if child.timeSpent(recursive=True):
            event = self.totalTimeSpentEvent(event)
        if self.priority(recursive=True) != oldTotalPriority:
            event = self.totalPriorityEvent(event)
        if child.revenue(recursive=True):
            event = self.totalRevenueEvent(event)
        if child.isBeingTracked(recursive=True):
            event = self.startTrackingEvent(event, *child.activeEfforts(recursive=True))
            
        if self.shouldBeMarkedCompleted():
            self.setCompletionDate(child.completionDate(), event)
        elif self.completed() and not child.completed():
            self.setCompletionDate(date.Date(), event)

        if child.dueDate() > self.dueDate():
            self.setDueDate(child.dueDate(), event)            
        if child.startDate() < self.startDate():
            self.setStartDate(child.startDate(), event)

        if notify:
            event.send()
        else:
            return event
        
    def removeChild(self, child, event=None):
        if child not in self.children():
            return event
        notify = event is None
        event = event or patterns.Event()
        oldTotalBudgetLeft = self.budgetLeft(recursive=True)
        oldTotalPriority = self.priority(recursive=True)
        super(Task, self).removeChild(child, event)
        newTotalBudgetLeft = self.budgetLeft(recursive=True)
        if child.budget(recursive=True):
            event = self.totalBudgetEvent(event)
        if newTotalBudgetLeft != oldTotalBudgetLeft:
            event = self.totalBudgetLeftEvent(event)
        if child.timeSpent(recursive=True):
            event = self.totalTimeSpentEvent(event)
        if self.priority(recursive=True) != oldTotalPriority:
            event = self.totalPriorityEvent(event)
        if child.revenue(recursive=True):
            event = self.totalRevenueEvent(event)
        if child.isBeingTracked(recursive=True) and not \
            self.isBeingTracked(recursive=True):
            event = self.stopTrackingEvent(event, *child.activeEfforts(recursive=True))
            
        if self.shouldBeMarkedCompleted(): 
            # The removed child was the last uncompleted child
            self.setCompletionDate(date.Today(), event)
        
        if notify:    
            event.send()
        else:
            return event
        
    def dueDate(self, recursive=False):
        if recursive:
            childrenDueDates = [child.dueDate(recursive=True) for child in \
                                self.children() if not child.completed()]
            return min(childrenDueDates + [self._dueDate])
        else:
            return self._dueDate

    def setDueDate(self, dueDate, event=None):
        if dueDate == self._dueDate:
            return event

        notify = event is None
        event = event or patterns.Event()
        
        self._dueDate = dueDate
        event.addSource(self, dueDate, type='task.dueDate')

        for child in self.children():
            if child.dueDate() > dueDate:
                event = child.setDueDate(dueDate, event)
                
        if self.parent():
            parent = self.parent()
            if dueDate > parent.dueDate():
                event = parent.setDueDate(dueDate, event)
        
        if notify:
            event.send()
        else:
            return event

    def startDate(self, recursive=False):
        if recursive:
            childrenStartDates = [child.startDate(recursive=True) for child in \
                                  self.children() if not child.completed()]
            return min(childrenStartDates + [self._startDate])
        else:
            return self._startDate

    def setStartDate(self, startDate, event=None):
        if startDate == self._startDate:
            return event
        notify = event is None
        event = event or patterns.Event()
        self._startDate = startDate
        event.addSource(self, startDate, type='task.startDate')
        
        if not self.recurrence(True): 
            # Let Task.recur() handle the change in start date
            for child in self.children():
                if startDate > child.startDate():
                    child.setStartDate(startDate, event)
            
            parent = self.parent()
            if parent and startDate < parent.startDate():
                parent.setStartDate(startDate, event)
        
        if notify:
            event.send()
        else:
            return event

    def timeLeft(self, recursive=False):
        return self.dueDate(recursive) - date.Today()
        
    def completionDate(self, recursive=False):
        if recursive:
            childrenCompletionDates = [child.completionDate(recursive=True) \
                for child in self.children() if child.completed()]
            return max(childrenCompletionDates + [self._completionDate])
        else:
            return self._completionDate

    def setCompletionDate(self, completionDate=None, event=None):
        completionDate = completionDate or date.Today()
        if completionDate == self._completionDate:
            return event
        notify = event is None
        event = event or patterns.Event()
        if completionDate != date.Date() and self.recurrence():
            event = self.recur(event)
        else:
            parent = self.parent()
            if parent:
                oldParentTotalPriority = parent.priority(recursive=True) 
            self._completionDate = completionDate
            event.addSource(self, completionDate, type='task.completionDate')
            
            if parent and parent.priority(recursive=True) != \
                          oldParentTotalPriority:
                event = self.totalPriorityEvent(event)                    
            if completionDate != date.Date():
                event = self.setReminder(None, event)
                
            if parent:
                if self.completed():
                    if parent.shouldBeMarkedCompleted():
                        parent.setCompletionDate(completionDate, event)
                else:
                    if parent.completed():
                        parent.setCompletionDate(date.Date(), event)
            if self.completed():
                for child in self.children():
                    if not child.completed():
                        child.setRecurrence(event=event)
                        child.setCompletionDate(completionDate, event)
                
                if self.isBeingTracked():
                    self.stopTracking(event)
                    
        if notify:
            event.send()
        else:
            return event

    def shouldBeMarkedCompleted(self):
        ''' Return whether this task should be marked completed. It should be
            marked completed when 1) it's not completed, 2) all of its children
            are completed, 3) its setting says it should be completed when
            all of its children are completed. '''
        shouldMarkCompletedAccordingToSetting = \
            self.settings.getboolean('behavior', 
                'markparentcompletedwhenallchildrencompleted')
        shouldMarkCompletedAccordingToTask = \
            self.shouldMarkCompletedWhenAllChildrenCompleted()
        return ((shouldMarkCompletedAccordingToTask == True) or \
                ((shouldMarkCompletedAccordingToTask == None) and \
                  shouldMarkCompletedAccordingToSetting)) and \
               (not self.completed()) and self.allChildrenCompleted()
      
    def completed(self):
        return self.completionDate() != date.Date()

    def overdue(self):
        return self.dueDate() < date.Today() and not self.completed()

    def inactive(self):
        return (self.startDate() > date.Today()) and not self.completed()
        
    def active(self):
        return not self.inactive() and not self.completed()

    def dueSoon(self):
        manyDays = self.settings.getint('behavior', 'duesoondays')
        return (0 <= self.timeLeft().days < manyDays and not self.completed())

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
        
    def addEffort(self, effort, event=None):
        if effort in self._efforts:
            return event
        wasTracking = self.isBeingTracked()
        self._efforts.append(effort)
        notify = event is None
        event = event or patterns.Event()
        event = self.addEffortEvent(event, effort)
        if effort.isBeingTracked() and not wasTracking:
            event = self.startTrackingEvent(event, effort)
        event = self.timeSpentEvent(event, effort)
        if notify:
            event.send()
        else:
            return event
  
    def addEffortEvent(self, event, *efforts):
        event.addSource(self, *efforts, **dict(type='task.effort.add'))
        return event
          
    def startTrackingEvent(self, event, *efforts):    
        for ancestor in [self] + self.ancestors():
            event.addSource(ancestor, *efforts, 
                            **dict(type=ancestor.trackStartEventType()))
        return event

    def removeEffort(self, effort, event=None):
        if effort not in self._efforts:
            return event
        self._efforts.remove(effort)
        notify = event is None
        event = event or patterns.Event()
        event = self.removeEffortEvent(event, effort)
        if effort.isBeingTracked() and not self.isBeingTracked():
            event = self.stopTrackingEvent(event, effort)
        event = self.timeSpentEvent(event, effort)
        if notify:
            event.send()
        else:
            return event
        
    def removeEffortEvent(self, event, *efforts):
        event.addSource(self, *efforts, **dict(type='task.effort.remove'))
        return event
        
    def stopTrackingEvent(self, event, *efforts):
        for ancestor in [self] + self.ancestors():
            event.addSource(ancestor, *efforts, 
                            **dict(type=ancestor.trackStopEventType()))
        return event
            
    def timeSpentEvent(self, event, effort):
        event.addSource(self, self.timeSpent(), type='task.timeSpent')
        event = self.totalTimeSpentEvent(event, effort)
        if self.budget():
            event = self.budgetLeftEvent(event)
        elif self.budget(recursive=True):
            event = self.totalBudgetLeftEvent(event)
        if self.hourlyFee() > 0:
            event = self.revenueEvent(event)
        return event
    
    def totalTimeSpentEvent(self, event, *efforts):
        for ancestor in [self] + self.ancestors():
            event.addSource(ancestor, *efforts, 
                            **dict(type=ancestor.totalTimeSpentChangedEventType()))
        return event
    
    def revenueEvent(self, event):
        event.addSource(self, self.revenue(), type='task.revenue')
        return self.totalRevenueEvent(event)
    
    def totalRevenueEvent(self, event):
        for ancestor in [self] + self.ancestors():
            event.addSource(ancestor, ancestor.revenue(recursive=True), 
                            type='task.totalRevenue')
        return event
    
    def setEfforts(self, efforts, event=None):
        if efforts == self._efforts:
            return event
        notify = event is None
        event = event or patterns.Event() 
        oldEfforts = self._efforts
        self._efforts = efforts
        event = event.removeEffortEvent(event, oldEfforts)
        event = event.addEffortEvent(event, efforts)
        if notify:
            event.send()
        else:
            return event

    def timeSpent(self, recursive=False):
        return sum((effort.duration() for effort in self.efforts(recursive)), 
                   date.TimeDelta())

    def stopTracking(self, event=None):
        notify = event is None
        event = event or patterns.Event()
        for effort in self.activeEfforts():
            event = effort.setStop(event=event)
        if notify:
            event.send()
        else:
            return event
                
    def budget(self, recursive=False):
        result = self._budget
        if recursive:
            for task in self.children():
                result += task.budget(recursive)
        return result
        
    def setBudget(self, budget, event=None):
        if budget == self._budget:
            return event
        notify = event is None
        event = event or patterns.Event()
        self._budget = budget
        event = self.budgetEvent(event)
        if notify:
            event.send()
        else:
            return event
        
    def budgetEvent(self, event):
        event.addSource(self, self.budget(), type='task.budget')
        event = self.totalBudgetEvent(event)
        return self.budgetLeftEvent(event)
    
    def totalBudgetEvent(self, event):
        for ancestor in [self] + self.ancestors():
            event.addSource(ancestor, ancestor.budget(recursive=True), 
                            type='task.totalBudget')
        return event
        
    def budgetLeftEvent(self, event):
        event.addSource(self, self.budgetLeft(), type='task.budgetLeft')
        return self.totalBudgetLeftEvent(event)
    
    def totalBudgetLeftEvent(self, event):
        for ancestor in [self] + self.ancestors():
            event.addSource(ancestor, ancestor.budgetLeft(recursive=True), 
                            type='task.totalBudgetLeft')
        return event
    
    def budgetLeft(self, recursive=False):
        budget = self.budget(recursive)
        return budget - self.timeSpent(recursive) if budget else budget
    
    def colorChangedEvent(self, event):
        event = super(Task, self).colorChangedEvent(event)    
        from taskcoachlib.domain import effort # prevent circular import
        color = self.color()
        for task in [self] + self.childrenWithoutOwnColor():
            for eachEffort in task.efforts():
                event.addSource(eachEffort, color, type=eachEffort.colorChangedEventType())
        return event
                    
    @classmethod
    def totalTimeSpentChangedEventType(class_):
        return 'task.totalTimeSpent'

    @classmethod
    def trackStartEventType(class_):
        return '%s.track.start'%class_

    @classmethod
    def trackStopEventType(class_):
        return '%s.track.stop'%class_
        
    # priority
    
    def priority(self, recursive=False):
        if recursive:
            childPriorities = [child.priority(recursive=True) \
                               for child in self.children() \
                               if not child.completed()]
            return max(childPriorities + [self._priority])
        else:
            return self._priority
        
    def setPriority(self, priority, event=None):
        if priority == self._priority:
            return event
        notify = event is None
        event = event or patterns.Event()
        self._priority = priority
        event = self.priorityEvent(event)
        if notify:
            event.send()
        else:
            return event
        
    def priorityEvent(self, event):
        event.addSource(self, self.priority(), type='task.priority')
        return self.totalPriorityEvent(event)
    
    def totalPriorityEvent(self, event):
        for ancestor in [self] + self.ancestors():
            event.addSource(ancestor, ancestor.priority(recursive=True),
                            type='task.totalPriority')
        return event
                
    # revenue
    
    def hourlyFee(self, recursive=False):
        return self._hourlyFee
    
    def setHourlyFee(self, hourlyFee, event=None):
        if hourlyFee == self._hourlyFee:
            return event
        notify = event is None
        event = event or patterns.Event()
        self._hourlyFee = hourlyFee
        event = self.hourlyFeeEvent(event)
        if notify:
            event.send()
        else:
            return event

    def hourlyFeeEvent(self, event):
        event.addSource(self, self.hourlyFee(), 
                        type=self.hourlyFeeChangedEventType())
        if self.timeSpent() > date.TimeDelta():
            for objectWithRevenue in [self] + self.efforts():
                event = objectWithRevenue.revenueEvent(event)
        return event
            
    @classmethod
    def hourlyFeeChangedEventType(class_):
        return '%s.hourlyFee'%class_
                
    def revenue(self, recursive=False):
        childRevenues = sum(child.revenue(recursive) for child in 
                            self.children()) if recursive else 0
        return self.timeSpent().hours() * self.hourlyFee() + self.fixedFee() + \
               childRevenues
    
    def fixedFee(self, recursive=False):
        childFixedFees = sum(child.fixedFee(recursive) for child in 
                             self.children()) if recursive else 0
        return self._fixedFee + childFixedFees
    
    def setFixedFee(self, fixedFee, event=None):
        if fixedFee == self._fixedFee:
            return event
        notify = event is None
        event = event or patterns.Event()
        self._fixedFee = fixedFee
        event = self.fixedFeeEvent(event)
        event = self.revenueEvent(event)
        if notify:
            event.send()
        else:
            return event
        
    def fixedFeeEvent(self, event):
        event.addSource(self, self.fixedFee(), type='task.fixedFee')
        event = self.totalFixedFeeEvent(event)
        return event
    
    def totalFixedFeeEvent(self, event):
        for ancestor in [self] + self.ancestors():
            event.addSource(ancestor, ancestor.fixedFee(recursive=True),
                            type='task.totalFixedFee')
        return event
        
    # reminder
    
    def reminder(self, recursive=False):
        return self._reminder

    def setReminder(self, reminderDateTime=None, event=None):
        if reminderDateTime == date.DateTime.max:
            reminderDateTime = None
        if reminderDateTime == self._reminder:
            return event
        self._reminder = reminderDateTime
        notify = event is None
        event = event or patterns.Event()
        event.addSource(self, self._reminder, type='task.reminder')
        if notify:
            event.send()
        else:
            return event
                    
    # Recurrence
    
    def recurrence(self, recursive=False):
        if not self._recurrence and recursive and self.parent():
            return self.parent().recurrence(recursive)
        else:
            return self._recurrence
        
    def setRecurrence(self, recurrence=None, event=None):
        recurrence = recurrence or date.Recurrence()
        if recurrence == self._recurrence:
            return event
        notify = event is None
        event = event or patterns.Event()
        self._recurrence = recurrence
        event.addSource(self, recurrence, type='task.recurrence')
        if notify:
            event.send()
        else:
            return event
            
    def recur(self, event=None):
        notify = event is None
        event = event or patterns.Event()
        event = self.setCompletionDate(date.Date(), event)
        nextStartDate = self.recurrence(recursive=True)(self.startDate(), next=False)
        event = self.setStartDate(nextStartDate, event)
        nextDueDate = self.recurrence(recursive=True)(self.dueDate(), next=False)
        event = self.setDueDate(nextDueDate, event)
        if self.reminder():
            nextReminder = self.recurrence(recursive=True)(self.reminder(), next=False)
            event = self.setReminder(nextReminder, event)
        for child in self.children():
            if not child.recurrence():
                event = child.recur(event)
        self.recurrence()(next=True)
        if notify:
            event.send()
        else:
            return event
                        
    # behavior
    
    def setShouldMarkCompletedWhenAllChildrenCompleted(self, newValue, event=None):
        if newValue == self._shouldMarkCompletedWhenAllChildrenCompleted:
            return event
        notify = event is None
        event = event or patterns.Event() 
        self._shouldMarkCompletedWhenAllChildrenCompleted = newValue
        event.addSource(self, newValue, 
                        type='task.setting.shouldMarkCompletedWhenAllChildrenCompleted')
        if notify:
            event.send()
        else:
            return event

    def shouldMarkCompletedWhenAllChildrenCompleted(self):
        return self._shouldMarkCompletedWhenAllChildrenCompleted
    
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
