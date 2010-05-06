# -*- coding: utf-8 -*-

'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2010 Frank Niessink <frank@niessink.com>
Copyright (C) 2008 Jérôme Laheurte <fraca7@free.fr>

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

import wx
from taskcoachlib import patterns
from taskcoachlib.domain import base, date, categorizable, note, attachment
from taskcoachlib.domain.attribute import color, icon


class Task(note.NoteOwner, attachment.AttachmentOwner, 
           categorizable.CategorizableCompositeObject):
    
    def __init__(self, subject='', description='', 
                 dueDateTime=None, startDateTime=None, completionDateTime=None,
                 budget=None, priority=0, id=None, hourlyFee=0, # pylint: disable-msg=W0622
                 fixedFee=0, reminder=None, categories=None,
                 efforts=None, shouldMarkCompletedWhenAllChildrenCompleted=None, 
                 recurrence=None, percentageComplete=0, *args, **kwargs):
        kwargs['id'] = id
        kwargs['subject'] = subject
        kwargs['description'] = description
        kwargs['categories'] = categories
        super(Task, self).__init__(*args, **kwargs)
        self.__dueDateTime = base.Attribute(dueDateTime or date.DateTime(), self, 
                                            self.dueDateTimeEvent)
        self.__startDateTime = base.Attribute(startDateTime or date.Now(), self, 
                                              self.startDateTimeEvent)
        self.__completionDateTime = base.Attribute(completionDateTime or date.DateTime(), 
                                                   self, self.completionDateTimeEvent)
        percentageComplete = 100 if self.__completionDateTime.get() != date.DateTime() else percentageComplete
        self.__percentageComplete = base.Attribute(percentageComplete, 
                                                   self, self.percentageCompleteEvent)
        self.__budget = base.Attribute(budget or date.TimeDelta(), self, 
                                       self.budgetEvent)
        self._efforts = efforts or []
        self.__priority = base.Attribute(priority, self, self.priorityEvent)
        self.__hourlyFee = base.Attribute(hourlyFee, self, self.hourlyFeeEvent)
        self.__fixedFee = base.Attribute(fixedFee, self, self.fixedFeeEvent)
        self.__reminder = base.Attribute(reminder, self, self.reminderEvent)
        self._recurrence = date.Recurrence() if recurrence is None else recurrence
        self._shouldMarkCompletedWhenAllChildrenCompleted = \
            shouldMarkCompletedWhenAllChildrenCompleted
        for effort in self._efforts:
            effort.setTask(self)

    def __setstate__(self, state, event=None):
        notify = event is None
        event = event or patterns.Event()
        super(Task, self).__setstate__(state, event)
        self.setStartDateTime(state['startDateTime'], event)
        self.setDueDateTime(state['dueDateTime'], event)
        self.setCompletionDateTime(state['completionDateTime'], event)
        self.setPercentageComplete(state['percentageComplete'], event)
        self.setRecurrence(state['recurrence'], event)
        self.setReminder(state['reminder'], event)
        self.setEfforts(state['efforts'], event)
        self.setBudget(state['budget'], event)
        self.setPriority(state['priority'], event)
        self.setHourlyFee(state['hourlyFee'], event)
        self.setFixedFee(state['fixedFee'], event)
        self.setShouldMarkCompletedWhenAllChildrenCompleted( \
            state['shouldMarkCompletedWhenAllChildrenCompleted'], event)
        if notify:
            event.send()
        
    def __getstate__(self):
        state = super(Task, self).__getstate__()
        state.update(dict(dueDateTime=self.__dueDateTime.get(), 
            startDateTime=self.__startDateTime.get(),  
            completionDateTime=self.__completionDateTime.get(),
            percentageComplete=self.__percentageComplete.get(),
            children=self.children(), parent=self.parent(), 
            efforts=self._efforts, budget=self.__budget.get(), 
            priority=self.__priority.get(), 
            hourlyFee=self.__hourlyFee.get(), fixedFee=self.__fixedFee.get(), 
            recurrence=self._recurrence.copy(),
            reminder=self.__reminder.get(),
            shouldMarkCompletedWhenAllChildrenCompleted=\
                self._shouldMarkCompletedWhenAllChildrenCompleted))
        return state

    def __getcopystate__(self):
        state = super(Task, self).__getcopystate__()
        state.update(dict(dueDateTime=self.__dueDateTime.get(), 
            startDateTime=self.__startDateTime.get(), 
            completionDateTime=self.__completionDateTime.get(),
            percentageComplete=self.__percentageComplete.get(), 
            efforts=[effort.copy() for effort in self._efforts], 
            budget=self.__budget.get(), priority=self.__priority.get(), 
            hourlyFee=self.__hourlyFee.get(), fixedFee=self.__fixedFee.get(), 
            recurrence=self._recurrence.copy(),
            reminder=self.__reminder.get(), 
            shouldMarkCompletedWhenAllChildrenCompleted=\
                self._shouldMarkCompletedWhenAllChildrenCompleted))
        return state
        
    def allChildrenCompleted(self):
        ''' Return whether all children (non-recursively) are completed. '''
        children = self.children()
        return all(child.completed() for child in children) if children \
            else False        

    def newChild(self, subject='New subtask'): # pylint: disable-msg=W0221
        ''' Subtask constructor '''
        return super(Task, self).newChild(subject=subject, 
            dueDateTime=self.dueDateTime(), 
            startDateTime=max(date.Now(), self.startDateTime()), parent=self)

    def addChild(self, child, event=None):
        if child in self.children():
            return
        notify = event is None
        event = event or patterns.Event()
        super(Task, self).addChild(child, event)
        self.childChangeEvent(child, event)
            
        if self.shouldBeMarkedCompleted():
            self.setCompletionDateTime(child.completionDateTime(), event)
        elif self.completed() and not child.completed():
            self.setCompletionDateTime(date.DateTime(), event)
            
        if child.dueDateTime() > self.dueDateTime():
            self.setDueDateTime(child.dueDateTime(), event)           
        if child.startDateTime() < self.startDateTime():
            self.setStartDateTime(child.startDateTime(), event)

        if notify:
            event.send()
        
    def removeChild(self, child, event=None):
        if child not in self.children():
            return
        notify = event is None
        event = event or patterns.Event()
        super(Task, self).removeChild(child, event)
        self.childChangeEvent(child, event)
            
        if self.shouldBeMarkedCompleted(): 
            # The removed child was the last uncompleted child
            self.setCompletionDateTime(date.Now(), event)
        
        if notify:    
            event.send()
            
    def childChangeEvent(self, child, event):
        childHasTotalTimeSpent = child.timeSpent(recursive=True)
        childHasTotalBudget = child.budget(recursive=True)
        childHasTotalBudgetLeft = child.budgetLeft(recursive=True)
        childHasTotalRevenue = child.revenue(recursive=True)
        childTotalPriority = child.priority(recursive=True)
        # Determine what changes due to the child being added or removed:
        if childHasTotalTimeSpent:
            self.totalTimeSpentEvent(event)
        if childHasTotalRevenue:
            self.totalRevenueEvent(event)
        if childHasTotalBudget:
            self.totalBudgetEvent(event)
        if childHasTotalBudgetLeft or (childHasTotalTimeSpent and \
                                       (childHasTotalBudget or self.budget())):
            self.totalBudgetLeftEvent(event)
        if childTotalPriority > self.priority():
            self.totalPriorityEvent(event)
        if child.isBeingTracked(recursive=True):
            activeEfforts = child.activeEfforts(recursive=True)
            if self.isBeingTracked(recursive=True):
                self.startTrackingEvent(event, *activeEfforts) # pylint: disable-msg=W0142
            else:
                self.stopTrackingEvent(event, *activeEfforts) # pylint: disable-msg=W0142
        
    def dueDateTime(self, recursive=False):
        if recursive:
            childrenDueDateTimes = [child.dueDateTime(recursive=True) for child in \
                                    self.children() if not child.completed()]
            return min(childrenDueDateTimes + [self.__dueDateTime.get()])
        else:
            return self.__dueDateTime.get()

    def setDueDateTime(self, dueDate, event=None):
        self.__dueDateTime.set(dueDate, event)
            
    def dueDateTimeEvent(self, event):
        dueDateTime = self.dueDateTime()
        event.addSource(self, dueDateTime, type='task.dueDateTime')
        for child in self.children():
            if child.dueDateTime() > dueDateTime:
                child.setDueDateTime(dueDateTime, event)
        if self.parent():
            parent = self.parent()
            if dueDateTime > parent.dueDateTime():
                parent.setDueDateTime(dueDateTime, event)

    def startDateTime(self, recursive=False):
        if recursive:
            childrenStartDateTimes = [child.startDateTime(recursive=True) for child in \
                                      self.children() if not child.completed()]
            return min(childrenStartDateTimes + [self.__startDateTime.get()])
        else:
            return self.__startDateTime.get()

    def setStartDateTime(self, startDateTime, event=None):
        self.__startDateTime.set(startDateTime, event)
            
    def startDateTimeEvent(self, event):
        startDateTime = self.startDateTime()
        event.addSource(self, startDateTime, type='task.startDateTime')
        if not self.recurrence(True):
            for child in self.children():
                if startDateTime > child.startDateTime():
                    child.setStartDateTime(startDateTime, event)
            parent = self.parent()
            if parent and startDateTime < parent.startDateTime():
                parent.setStartDateTime(startDateTime, event)
                
    def timeLeft(self, recursive=False):
        return self.dueDateTime(recursive) - date.Now()
        
    def completionDateTime(self, recursive=False):
        if recursive:
            childrenCompletionDateTimes = [child.completionDateTime(recursive=True) \
                for child in self.children() if child.completed()]
            return max(childrenCompletionDateTimes + [self.__completionDateTime.get()])
        else:
            return self.__completionDateTime.get()

    def setCompletionDateTime(self, completionDateTime=None, event=None):
        completionDateTime = completionDateTime or date.Now()
        if completionDateTime == self.__completionDateTime.get():
            return
        notify = event is None
        event = event or patterns.Event()
        if completionDateTime != date.DateTime() and self.recurrence():
            self.recur(event)
        else:
            parent = self.parent()
            if parent:
                oldParentTotalPriority = parent.priority(recursive=True) 
            self.__completionDateTime.set(completionDateTime, event)
            if parent and parent.priority(recursive=True) != \
                          oldParentTotalPriority:
                self.totalPriorityEvent(event)              
            if completionDateTime != date.DateTime():
                self.setReminder(None, event)
            self.setPercentageComplete(100 if completionDateTime != date.DateTime() else 0, 
                                       event)
            if parent:
                if self.completed():
                    if parent.shouldBeMarkedCompleted():
                        parent.setCompletionDateTime(completionDateTime, event)
                else:
                    if parent.completed():
                        parent.setCompletionDateTime(date.DateTime(), event)
            if self.completed():
                for child in self.children():
                    if not child.completed():
                        child.setRecurrence(event=event)
                        child.setCompletionDateTime(completionDateTime, event)
                
                if self.isBeingTracked():
                    self.stopTracking(event)
                    
        if notify:
            event.send()
        
    def completionDateTimeEvent(self, event):
        completionDateTime = self.completionDateTime()
        event.addSource(self, completionDateTime, type='task.completionDateTime')

    def shouldBeMarkedCompleted(self):
        ''' Return whether this task should be marked completed. It should be
            marked completed when 1) it's not completed, 2) all of its children
            are completed, 3) its setting says it should be completed when
            all of its children are completed. '''
        shouldMarkCompletedAccordingToSetting = \
            self.settings.getboolean('behavior', # pylint: disable-msg=E1101
                'markparentcompletedwhenallchildrencompleted')
        shouldMarkCompletedAccordingToTask = \
            self.shouldMarkCompletedWhenAllChildrenCompleted()
        return ((shouldMarkCompletedAccordingToTask == True) or \
                ((shouldMarkCompletedAccordingToTask == None) and \
                  shouldMarkCompletedAccordingToSetting)) and \
               (not self.completed()) and self.allChildrenCompleted()
      
    def completed(self):
        return self.completionDateTime() != date.DateTime()

    def overdue(self):
        return self.dueDateTime() < date.Now() and not self.completed()

    def inactive(self):
        return self.startDateTime() > date.Now() and not self.completed()
        
    def active(self):
        return not self.inactive() and not self.completed()

    def dueSoon(self):
        manyDays = self.settings.getint('behavior', 'duesoondays') # pylint: disable-msg=E1101
        return (0 <= self.timeLeft().days < manyDays and not self.completed())

    def dueToday(self):
        return (self.dueDateTime().date() == date.Today() and not self.completed())

    def dueTomorrow(self):
        return (self.dueDateTime().date() == date.Tomorrow() and not self.completed())
    
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
            return
        wasTracking = self.isBeingTracked()
        self._efforts.append(effort)
        notify = event is None
        event = event or patterns.Event()
        self.addEffortEvent(event, effort)
        if effort.isBeingTracked() and not wasTracking:
            self.startTrackingEvent(event, effort)
        self.timeSpentEvent(event, effort)
        if notify:
            event.send()
  
    def addEffortEvent(self, event, *efforts):
        event.addSource(self, *efforts, **dict(type='task.effort.add'))
          
    def startTrackingEvent(self, event, *efforts):    
        for ancestor in [self] + self.ancestors():
            event.addSource(ancestor, *efforts, 
                            **dict(type=ancestor.trackStartEventType()))

    def removeEffort(self, effort, event=None):
        if effort not in self._efforts:
            return
        self._efforts.remove(effort)
        notify = event is None
        event = event or patterns.Event()
        self.removeEffortEvent(event, effort)
        if effort.isBeingTracked() and not self.isBeingTracked():
            self.stopTrackingEvent(event, effort)
        self.timeSpentEvent(event, effort)
        if notify:
            event.send()
        
    def removeEffortEvent(self, event, *efforts):
        event.addSource(self, *efforts, **dict(type='task.effort.remove'))
        
    def stopTrackingEvent(self, event, *efforts):
        for ancestor in [self] + self.ancestors():
            event.addSource(ancestor, *efforts, 
                            **dict(type=ancestor.trackStopEventType()))
            
    def timeSpentEvent(self, event, effort):
        event.addSource(self, self.timeSpent(), type='task.timeSpent')
        self.totalTimeSpentEvent(event, effort)
        if self.budget():
            self.budgetLeftEvent(event)
        elif self.budget(recursive=True):
            self.totalBudgetLeftEvent(event)
        if self.hourlyFee() > 0:
            self.revenueEvent(event)
    
    def totalTimeSpentEvent(self, event, *efforts):
        for ancestor in [self] + self.ancestors():
            event.addSource(ancestor, *efforts, 
                            **dict(type=ancestor.totalTimeSpentChangedEventType()))
    
    def revenueEvent(self, event):
        event.addSource(self, self.revenue(), type='task.revenue')
        self.totalRevenueEvent(event)
    
    def totalRevenueEvent(self, event):
        for ancestor in [self] + self.ancestors():
            event.addSource(ancestor, ancestor.revenue(recursive=True), 
                            type='task.totalRevenue')
    
    def setEfforts(self, efforts, event=None):
        if efforts == self._efforts:
            return
        notify = event is None
        event = event or patterns.Event() 
        oldEfforts = self._efforts
        self._efforts = efforts
        self.removeEffortEvent(event, oldEfforts)
        self.addEffortEvent(event, efforts)
        if notify:
            event.send()

    def timeSpent(self, recursive=False):
        return sum((effort.duration() for effort in self.efforts(recursive)), 
                   date.TimeDelta())

    def stopTracking(self, event=None):
        notify = event is None
        event = event or patterns.Event()
        for effort in self.activeEfforts():
            effort.setStop(event=event)
        if notify:
            event.send()
                
    def budget(self, recursive=False):
        result = self.__budget.get()
        if recursive:
            for task in self.children():
                result += task.budget(recursive)
        return result
        
    def setBudget(self, budget, event=None):
        self.__budget.set(budget, event)
        
    def budgetEvent(self, event):
        event.addSource(self, self.budget(), type='task.budget')
        self.totalBudgetEvent(event)
        self.budgetLeftEvent(event)
    
    def totalBudgetEvent(self, event):
        for ancestor in [self] + self.ancestors():
            event.addSource(ancestor, ancestor.budget(recursive=True), 
                            type='task.totalBudget')
        
    def budgetLeftEvent(self, event):
        event.addSource(self, self.budgetLeft(), type='task.budgetLeft')
        self.totalBudgetLeftEvent(event)
    
    def totalBudgetLeftEvent(self, event):
        for ancestor in [self] + self.ancestors():
            event.addSource(ancestor, ancestor.budgetLeft(recursive=True), 
                            type='task.totalBudgetLeft')
    
    def budgetLeft(self, recursive=False):
        budget = self.budget(recursive)
        return budget - self.timeSpent(recursive) if budget else budget

    def foregroundColor(self, recursive=False):
        fgColor = super(Task, self).foregroundColor(recursive)
        if not recursive:
            return fgColor
        statusColor = self.statusColor()
        if statusColor == wx.BLACK:
            return fgColor
        elif fgColor == None:
            return statusColor
        else:
            return color.ColorMixer.mix((fgColor, statusColor))
    
    def statusColor(self):
        ''' Return the current color of task, based on its status (completed,
            overdue, duesoon, inactive, or active). '''
        if self.completed():
            status = 'completed'
        elif self.overdue(): 
            status = 'overdue'
        elif self.dueSoon():
            status = 'duesoon'
        elif self.inactive(): 
            status = 'inactive'
        else:
            status = 'active'
        return self.colorForStatus(status)
    
    @classmethod
    def colorForStatus(class_, status):
        return wx.Colour(*eval(class_.settings.get('color', '%stasks'%status)))
    
    def foregroundColorChangedEvent(self, event):
        super(Task, self).foregroundColorChangedEvent(event)
        fgColor = self.foregroundColor()
        for task in [self] + self.childrenWithoutOwnForegroundColor():
            for eachEffort in task.efforts():
                event.addSource(eachEffort, fgColor, 
                                type=eachEffort.foregroundColorChangedEventType())
    
    def backgroundColorChangedEvent(self, event):
        super(Task, self).backgroundColorChangedEvent(event)
        bgColor = self.backgroundColor()
        for task in [self] + self.childrenWithoutOwnBackgroundColor():
            for eachEffort in task.efforts():
                event.addSource(eachEffort, bgColor, 
                                type=eachEffort.backgroundColorChangedEventType())

    def icon(self, recursive=False):
        icon = super(Task, self).icon(recursive=False)
        if not icon and recursive:
            icon = self.categoryIcon() or self.__stateBasedIcon(selected=False)
        return self.pluralOrSingularIcon(icon)

    def selectedIcon(self, recursive=False):
        icon = super(Task, self).selectedIcon(recursive=False)
        if not icon and recursive:
            icon = self.categorySelectedIcon() or self.__stateBasedIcon(selected=True)
        return self.pluralOrSingularIcon(icon)

    stateColorMap = (('completed', '_green'), ('overdue', '_red'),
                     ('dueSoon', '_orange'), ('inactive', '_grey'))

    def __stateBasedIcon(self, selected=False):
        if self.isBeingTracked():
            taskIcon = 'clock'
        else:
            taskIcon = 'led'
            for state, color in self.stateColorMap:
                if getattr(self, state)():
                    taskIcon += color
                    break
            else:
                taskIcon += '_blue'
            taskIcon = self.pluralOrSingularIcon(taskIcon+'_icon')[:-len('_icon')]
            hasChildren = any(child for child in self.children() if not child.isDeleted())
            taskIcon += '_open' if selected and hasChildren else ''
        return taskIcon + '_icon'
    
    @classmethod
    def totalTimeSpentChangedEventType(class_):
        return 'task.totalTimeSpent'

    @classmethod
    def trackStartEventType(class_):
        return '%s.track.start'%class_

    @classmethod
    def trackStopEventType(class_):
        return '%s.track.stop'%class_
    
    # percentage Complete
    
    def percentageComplete(self, recursive=False):
        percentages = [self.__percentageComplete.get()] 
        if recursive:
            percentages.extend([child.percentageComplete(recursive) for child in self.children()])
        return sum(percentages)/len(percentages)
    
    def setPercentageComplete(self, percentage, event=None):
        if percentage == self.percentageComplete():
            return
        notify = event is None
        event = event or patterns.Event()
        oldPercentage = self.percentageComplete()
        self.__percentageComplete.set(percentage, event)
        if percentage == 100 and oldPercentage != 100 and self.completionDateTime() == date.DateTime():
            self.setCompletionDateTime(date.Now(), event)
        elif oldPercentage == 100 and percentage != 100 and self.completionDateTime() != date.DateTime():
            self.setCompletionDateTime(date.DateTime(), event)
        if notify:
            event.send()
    
    def percentageCompleteEvent(self, event):
        event.addSource(self, self.percentageComplete(), 
                        type='task.percentageComplete')
        self.totalPercentageCompleteEvent(event)
        
    def totalPercentageCompleteEvent(self, event):
        for ancestor in [self] + self.ancestors():
            event.addSource(ancestor, ancestor.percentageComplete(recursive=True), 
                            **dict(type='task.totalPercentageComplete'))

        
    # priority
    
    def priority(self, recursive=False):
        if recursive:
            childPriorities = [child.priority(recursive=True) \
                               for child in self.children() \
                               if not child.completed()]
            return max(childPriorities + [self.__priority.get()])
        else:
            return self.__priority.get()
        
    def setPriority(self, priority, event=None):
        self.__priority.set(priority, event)
        
    def priorityEvent(self, event):
        event.addSource(self, self.priority(), type='task.priority')
        self.totalPriorityEvent(event)
    
    def totalPriorityEvent(self, event):
        for ancestor in [self] + self.ancestors():
            event.addSource(ancestor, ancestor.priority(recursive=True),
                            type='task.totalPriority')
                
    # revenue
    
    def hourlyFee(self, recursive=False): # pylint: disable-msg=W0613
        return self.__hourlyFee.get()
    
    def setHourlyFee(self, hourlyFee, event=None):
        self.__hourlyFee.set(hourlyFee, event)

    def hourlyFeeEvent(self, event):
        event.addSource(self, self.hourlyFee(), 
                        type=self.hourlyFeeChangedEventType())
        if self.timeSpent() > date.TimeDelta():
            for objectWithRevenue in [self] + self.efforts():
                objectWithRevenue.revenueEvent(event)
            
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
        return self.__fixedFee.get() + childFixedFees
    
    def setFixedFee(self, fixedFee, event=None):
        self.__fixedFee.set(fixedFee, event)
        
    def fixedFeeEvent(self, event):
        event.addSource(self, self.fixedFee(), type='task.fixedFee')
        self.totalFixedFeeEvent(event)
        self.revenueEvent(event)
    
    def totalFixedFeeEvent(self, event):
        for ancestor in [self] + self.ancestors():
            event.addSource(ancestor, ancestor.fixedFee(recursive=True),
                            type='task.totalFixedFee')
        
    # reminder
    
    def reminder(self, recursive=False): # pylint: disable-msg=W0613
        return self.__reminder.get()

    def setReminder(self, reminderDateTime=None, event=None):
        if reminderDateTime == date.DateTime.max:
            reminderDateTime = None
        self.__reminder.set(reminderDateTime, event)
            
    def reminderEvent(self, event):
        event.addSource(self, self.reminder(), type='task.reminder')
                    
    # Recurrence
    
    def recurrence(self, recursive=False):
        if not self._recurrence and recursive and self.parent():
            return self.parent().recurrence(recursive)
        else:
            return self._recurrence
        
    def setRecurrence(self, recurrence=None, event=None):
        recurrence = recurrence or date.Recurrence()
        if recurrence == self._recurrence:
            return
        notify = event is None
        event = event or patterns.Event()
        self._recurrence = recurrence
        event.addSource(self, recurrence, type='task.recurrence')
        if notify:
            event.send()
            
    def recur(self, event=None):
        notify = event is None
        event = event or patterns.Event()
        self.setCompletionDateTime(date.DateTime(), event)
        nextStartDateTime = self.recurrence(recursive=True)(self.startDateTime(), next=False)
        self.setStartDateTime(nextStartDateTime, event)
        nextDueDateTime = self.recurrence(recursive=True)(self.dueDateTime(), next=False)
        self.setDueDateTime(nextDueDateTime, event)
        if self.reminder():
            nextReminder = self.recurrence(recursive=True)(self.reminder(), next=False)
            self.setReminder(nextReminder, event)
        for child in self.children():
            if not child.recurrence():
                child.recur(event)
        self.recurrence()(next=True)
        if notify:
            event.send()
                        
    # behavior
    
    def setShouldMarkCompletedWhenAllChildrenCompleted(self, newValue, event=None):
        if newValue == self._shouldMarkCompletedWhenAllChildrenCompleted:
            return
        notify = event is None
        event = event or patterns.Event() 
        self._shouldMarkCompletedWhenAllChildrenCompleted = newValue
        event.addSource(self, newValue, 
                        type='task.setting.shouldMarkCompletedWhenAllChildrenCompleted')
        if notify:
            event.send()

    def shouldMarkCompletedWhenAllChildrenCompleted(self):
        return self._shouldMarkCompletedWhenAllChildrenCompleted
    
    @classmethod
    def modificationEventTypes(class_):
        eventTypes = super(Task, class_).modificationEventTypes()
        return eventTypes + ['task.dueDateTime', 'task.startDateTime', 
                             'task.completionDateTime', 
                             'task.effort.add', 'task.effort.remove', 
                             'task.budget', 'task.percentageComplete', 
                             'task.priority', 
                             class_.hourlyFeeChangedEventType(), 
                             'task.fixedFee',
                             'task.reminder', 'task.recurrence',
                             'task.setting.shouldMarkCompletedWhenAllChildrenCompleted']
