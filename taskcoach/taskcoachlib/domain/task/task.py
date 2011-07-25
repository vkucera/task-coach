# -*- coding: utf-8 -*-

'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2011 Task Coach developers <developers@taskcoach.org>
Copyright (C) 2010 Svetoslav Trochev <sal_electronics@hotmail.com>

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
from taskcoachlib.domain.attribute import color


class Task(note.NoteOwner, attachment.AttachmentOwner, 
           categorizable.CategorizableCompositeObject):
    
    maxDateTime = date.DateTime()
    
    def __init__(self, subject='', description='', 
                 dueDateTime=None, startDateTime=None, completionDateTime=None,
                 budget=None, priority=0, id=None, hourlyFee=0, # pylint: disable-msg=W0622
                 fixedFee=0, reminder=None, reminderBeforeSnooze=None, categories=None,
                 efforts=None, shouldMarkCompletedWhenAllChildrenCompleted=None, 
                 recurrence=None, percentageComplete=0, prerequisites=None,
                 dependencies=None, *args, **kwargs):
        kwargs['id'] = id
        kwargs['subject'] = subject
        kwargs['description'] = description
        kwargs['categories'] = categories
        super(Task, self).__init__(*args, **kwargs)
        self.__dueSoonHours = self.settings.getint('behavior', 'duesoonhours') # pylint: disable-msg=E1101
        Attribute, SetAttribute = base.Attribute, base.SetAttribute
        maxDateTime = self.maxDateTime    
        self.__dueDateTime = Attribute(dueDateTime or maxDateTime, self, 
                                       self.dueDateTimeEvent)
        self.__startDateTime = Attribute(startDateTime or maxDateTime, self, 
                                         self.startDateTimeEvent)
        self.__completionDateTime = Attribute(completionDateTime or maxDateTime, 
                                              self, self.completionDateTimeEvent)
        percentageComplete = 100 if self.__completionDateTime.get() != maxDateTime else percentageComplete
        self.__percentageComplete = Attribute(percentageComplete, 
                                              self, self.percentageCompleteEvent)
        self.__budget = Attribute(budget or date.TimeDelta(), self, 
                                  self.budgetEvent)
        self._efforts = efforts or []
        self.__priority = Attribute(priority, self, self.priorityEvent)
        self.__hourlyFee = Attribute(hourlyFee, self, self.hourlyFeeEvent)
        self.__fixedFee = Attribute(fixedFee, self, self.fixedFeeEvent)
        self.__reminder = Attribute(reminder or maxDateTime, self, self.reminderEvent)
        self.__reminderBeforeSnooze = reminderBeforeSnooze or self.__reminder.get()
        self._recurrence = date.Recurrence() if recurrence is None else recurrence
        self.__prerequisites = SetAttribute(prerequisites or [], self, 
                                            changeEvent=self.prerequisitesEvent)
        self.__dependencies = SetAttribute(dependencies or [], self, 
                                           changeEvent=self.dependenciesEvent)
        self._shouldMarkCompletedWhenAllChildrenCompleted = \
            shouldMarkCompletedWhenAllChildrenCompleted
        for effort in self._efforts:
            effort.setTask(self)
        self.registerObserver = registerObserver = patterns.Publisher().registerObserver
        self.removeObserver = patterns.Publisher().removeObserver
        for eventType in 'active', 'inactive', 'completed', 'duesoon', 'overdue':
            registerObserver(self.__computeRecursiveForegroundColor, 'fgcolor.%stasks'%eventType)
            registerObserver(self.__computeRecursiveBackgroundColor, 'bgcolor.%stasks'%eventType)
            registerObserver(self.__computeRecursiveIcon, 'icon.%stasks'%eventType)
            registerObserver(self.__computeRecursiveSelectedIcon, 'icon.%stasks'%eventType)
        registerObserver(self.onDueSoonHoursChanged, 'behavior.duesoonhours')

        now = date.Now()
        if now < self.__dueDateTime.get() < maxDateTime:
            registerObserver(self.onOverDue, 
                             date.Clock.eventType(self.__dueDateTime.get() + date.oneSecond))
        if now < self.__startDateTime.get() < maxDateTime:
            registerObserver(self.onStarted,
                             date.Clock.eventType(self.__startDateTime.get() + date.oneSecond))

    @patterns.eventSource
    def __setstate__(self, state, event=None):
        super(Task, self).__setstate__(state, event=event)
        self.setStartDateTime(state['startDateTime'], event=event)
        self.setDueDateTime(state['dueDateTime'], event=event)
        self.setCompletionDateTime(state['completionDateTime'], event=event)
        self.setPercentageComplete(state['percentageComplete'], event=event)
        self.setRecurrence(state['recurrence'], event=event)
        self.setReminder(state['reminder'], event=event)
        self.setEfforts(state['efforts'], event=event)
        self.setBudget(state['budget'], event=event)
        self.setPriority(state['priority'], event=event)
        self.setHourlyFee(state['hourlyFee'], event=event)
        self.setFixedFee(state['fixedFee'], event=event)
        self.setPrerequisites(state['prerequisites'], event=event)
        self.setDependencies(state['dependencies'], event=event)
        self.setShouldMarkCompletedWhenAllChildrenCompleted( \
            state['shouldMarkCompletedWhenAllChildrenCompleted'], event=event)
        
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
            prerequisites=self.__prerequisites.get(),
            dependencies=self.__dependencies.get(),
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

    @classmethod
    def monitoredAttributes(class_):
        return categorizable.CategorizableCompositeObject.monitoredAttributes() + \
               ['startDateTime', 'dueDateTime', 'completionDateTime',
                'percentageComplete', 'recurrence', 'reminder', 'budget',
                'priority', 'hourlyFee', 'fixedFee',
                'shouldMarkCompletedWhenAllChildrenCompleted']

    @patterns.eventSource
    def addCategory(self, *categories, **kwargs):
        super(Task, self).addCategory(*categories, **kwargs)
        self.recomputeAppearance(True, event=kwargs.pop('event'))

    @patterns.eventSource
    def removeCategory(self, *categories, **kwargs):
        super(Task, self).removeCategory(*categories, **kwargs)
        self.recomputeAppearance(True, event=kwargs.pop('event'))

    @patterns.eventSource
    def setCategories(self, *categories, **kwargs):
        super(Task, self).setCategories(*categories, **kwargs)
        self.recomputeAppearance(True, event=kwargs.pop('event'))
        
    def allChildrenCompleted(self):
        ''' Return whether all children (non-recursively) are completed. '''
        children = self.children()
        return all(child.completed() for child in children) if children \
            else False        

    def newChild(self, subject='New subtask'): # pylint: disable-msg=W0221
        ''' Subtask constructor '''
        return super(Task, self).newChild(subject=subject, parent=self)

    @patterns.eventSource
    def addChild(self, child, event=None):
        if child in self.children():
            return
        super(Task, self).addChild(child, event=event)
        self.childChangeEvent(child, event)
        if self.shouldBeMarkedCompleted():
            self.setCompletionDateTime(child.completionDateTime(), event=event)
        elif self.completed() and not child.completed():
            self.setCompletionDateTime(self.maxDateTime, event=event)
        if child.dueDateTime() > self.dueDateTime():
            self.setDueDateTime(child.dueDateTime(), event=event)           
        if child.startDateTime() < self.startDateTime():
            self.setStartDateTime(child.startDateTime(), event=event)

    @patterns.eventSource
    def removeChild(self, child, event=None):
        if child not in self.children():
            return
        super(Task, self).removeChild(child, event=event)
        self.childChangeEvent(child, event)    
        if self.shouldBeMarkedCompleted(): 
            # The removed child was the last uncompleted child
            self.setCompletionDateTime(date.Now(), event=event)
                    
    def childChangeEvent(self, child, event):
        childHasTimeSpent = child.timeSpent(recursive=True)
        childHasBudget = child.budget(recursive=True)
        childHasBudgetLeft = child.budgetLeft(recursive=True)
        childHasRevenue = child.revenue(recursive=True)
        childPriority = child.priority(recursive=True)
        # Determine what changes due to the child being added or removed:
        if childHasTimeSpent:
            self.timeSpentEvent(event, *child.efforts())
        if childHasRevenue:
            self.revenueEvent(event)
        if childHasBudget:
            self.budgetEvent(event)
        if childHasBudgetLeft or (childHasTimeSpent and \
                                  (childHasBudget or self.budget())):
            self.budgetLeftEvent(event)
        if childPriority > self.priority():
            self.priorityEvent(event)
        if child.isBeingTracked(recursive=True):
            activeEfforts = child.activeEfforts(recursive=True)
            if self.isBeingTracked(recursive=True):
                self.startTrackingEvent(event, *activeEfforts) # pylint: disable-msg=W0142
            else:
                self.stopTrackingEvent(event, *activeEfforts) # pylint: disable-msg=W0142
    
    @patterns.eventSource    
    def setSubject(self, subject, event=None):
        super(Task, self).setSubject(subject, event=event)
        # The subject of a dependency of our prerequisites has changed, notify:
        for prerequisite in self.prerequisites():
            event.addSource(prerequisite, subject, type='task.dependency.subject')
        # The subject of a prerequisite of our dependencies has changed, notify:
        for dependency in self.dependencies():
            event.addSource(dependency, subject, type='task.prerequisite.subject')

    # Due date
            
    def dueDateTime(self, recursive=False):
        if recursive:
            childrenDueDateTimes = [child.dueDateTime(recursive=True) for child in \
                                    self.children() if not child.completed()]
            return min(childrenDueDateTimes + [self.__dueDateTime.get()])
        else:
            return self.__dueDateTime.get()

    @patterns.eventSource
    def setDueDateTime(self, dueDateTime, event=None):
        self.removeObserver(self.onOverDue)
        self.removeObserver(self.onDueSoon)
        self.__dueDateTime.set(dueDateTime, event=event)
        if dueDateTime != self.maxDateTime:
            self.registerObserver(self.onOverDue, date.Clock.eventType(dueDateTime + date.oneSecond))
            if self.__dueSoonHours > 0:
                dueSoonDateTime = dueDateTime + date.oneSecond - date.TimeDelta(hours=self.__dueSoonHours)
                if dueSoonDateTime > date.Now():
                    self.registerObserver(self.onDueSoon, date.Clock.eventType(dueSoonDateTime))
            
    def dueDateTimeEvent(self, event):
        dueDateTime = self.dueDateTime()
        event.addSource(self, dueDateTime, type=self.dueDateTimeChangedEventType())
        for child in self.children():
            if child.dueDateTime() > dueDateTime:
                child.setDueDateTime(dueDateTime, event=event)
        if self.parent():
            parent = self.parent()
            if dueDateTime > parent.dueDateTime():
                parent.setDueDateTime(dueDateTime, event=event)
        self.recomputeAppearance(event=event)

    @classmethod
    def dueDateTimeChangedEventType(class_):
        return '%s.dueDateTime' % class_

    def onOverDue(self, event): # pylint: disable-msg=W0613
        self.recomputeAppearance()
        
    def onDueSoon(self, event): # pylint: disable-msg=W0613
        self.recomputeAppearance()
        
    @staticmethod
    def dueDateTimeSortFunction(**kwargs):
        recursive = kwargs.get('treeMode', False)
        return lambda task: task.dueDateTime(recursive=recursive)
    
    @classmethod
    def dueDateTimeSortEventTypes(class_):
        ''' The event types that influence the due date time sort order. '''
        return (class_.dueDateTimeChangedEventType(),)
    
    # Start date
    
    def startDateTime(self, recursive=False):
        if recursive:
            childrenStartDateTimes = [child.startDateTime(recursive=True) for child in \
                                      self.children() if not child.completed()]
            return min(childrenStartDateTimes + [self.__startDateTime.get()])
        else:
            return self.__startDateTime.get()

    @patterns.eventSource
    def setStartDateTime(self, startDateTime, event=None):
        self.removeObserver(self.onStarted)
        self.__startDateTime.set(startDateTime, event=event)
        if startDateTime != self.maxDateTime:
            self.registerObserver(self.onStarted, date.Clock.eventType(startDateTime + date.oneSecond))
            
    def startDateTimeEvent(self, event):
        startDateTime = self.startDateTime()
        event.addSource(self, startDateTime, type=self.startDateTimeChangedEventType())
        if not self.recurrence(recursive=True, upwards=True):
            for child in self.children():
                if startDateTime > child.startDateTime():
                    child.setStartDateTime(startDateTime, event=event)
            parent = self.parent()
            if parent and startDateTime < parent.startDateTime():
                parent.setStartDateTime(startDateTime, event=event)
        self.recomputeAppearance(event=event)

    @classmethod
    def startDateTimeChangedEventType(class_):
        return '%s.startDateTime' % class_

    def onStarted(self, event): # pylint: disable-msg=W0613
        self.recomputeAppearance()
        
    @staticmethod
    def startDateTimeSortFunction(**kwargs):
        recursive = kwargs.get('treeMode', False)
        return lambda task: task.startDateTime(recursive=recursive)
    
    @classmethod
    def startDateTimeSortEventTypes(class_):
        ''' The event types that influence the start date time sort order. '''
        return (class_.startDateTimeChangedEventType(),)

    def timeLeft(self, recursive=False):
        return self.dueDateTime(recursive) - date.Now()

    @staticmethod
    def timeLeftSortFunction(**kwargs):
        recursive = kwargs.get('treeMode', False)
        return lambda task: task.timeLeft(recursive=recursive)
    
    @classmethod
    def timeLeftSortEventTypes(class_):
        ''' The event types that influence the time left sort order. '''
        return (class_.dueDateTimeChangedEventType(),)
                    
    # Completion date
            
    def completionDateTime(self, recursive=False):
        if recursive:
            childrenCompletionDateTimes = [child.completionDateTime(recursive=True) \
                for child in self.children() if child.completed()]
            return max(childrenCompletionDateTimes + [self.__completionDateTime.get()])
        else:
            return self.__completionDateTime.get()

    @patterns.eventSource
    def setCompletionDateTime(self, completionDateTime=None, event=None):
        completionDateTime = completionDateTime or date.Now()
        if completionDateTime == self.__completionDateTime.get():
            return
        if completionDateTime != self.maxDateTime and self.recurrence():
            self.recur(completionDateTime, event=event)
        else:
            parent = self.parent()
            if parent:
                oldParentPriority = parent.priority(recursive=True)
            self.__completionDateTime.set(completionDateTime, event=event)
            if parent and parent.priority(recursive=True) != oldParentPriority:
                self.priorityEvent(event)              
            if completionDateTime != self.maxDateTime:
                self.setReminder(None, event)
            self.setPercentageComplete(100 if completionDateTime != self.maxDateTime else 0, 
                                       event=event)
            if parent:
                if self.completed():
                    if parent.shouldBeMarkedCompleted():
                        parent.setCompletionDateTime(completionDateTime, event=event)
                else:
                    if parent.completed():
                        parent.setCompletionDateTime(self.maxDateTime, event=event)
            if self.completed():
                for child in self.children():
                    if not child.completed():
                        child.setRecurrence(event=event)
                        child.setCompletionDateTime(completionDateTime, event=event)
                if self.isBeingTracked():
                    self.stopTracking(event=event)                    
            self.recomputeAppearance(event=event)
            
    def completionDateTimeEvent(self, event):
        event.addSource(self, self.completionDateTime(), type=self.completionDateTimeChangedEventType())
        for dependency in self.dependencies():
            dependency.recomputeAppearance(recursive=True, event=event)

    @classmethod
    def completionDateTimeChangedEventType(class_):
        return '%s.completionDateTime' % class_

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
      
    @staticmethod  
    def completionDateTimeSortFunction(**kwargs):
        recursive = kwargs.get('treeMode', False)
        return lambda task: task.completionDateTime(recursive=recursive)

    @classmethod
    def completionDateTimeSortEventTypes(class_):
        ''' The event types that influence the completion date time sort order. '''
        return (class_.completionDateTimeChangedEventType(),)

    # Task state
    
    def completed(self):
        return self.completionDateTime() != self.maxDateTime

    def overdue(self):
        return self.dueDateTime() < date.Now() and not self.completed()

    def inactive(self):
        if self.completed():
            return False # Completed tasks are never inactive
        if date.Now() < self.startDateTime() < self.maxDateTime:
            return True # Start at a specific future datetime, so inactive now
        if self.parent() and self.parent().inactive():
            return True
        if self.prerequisites():
            # We're inactive as long as not all prerequisites are completed
            return any([not prerequisite.completed() for prerequisite in self.prerequisites()])
        else:
            # We're inactive only if we have no startDateTime at all 
            return self.startDateTime() == self.maxDateTime
        
    def active(self):
        return not self.inactive() and not self.completed()

    def dueSoon(self):
        return (0 <= self.timeLeft().hours() < self.__dueSoonHours and not self.completed())
    
    def onDueSoonHoursChanged(self, event):
        self.removeObserver(self.onDueSoon)
        self.__dueSoonHours = int(event.value())
        dueDateTime = self.dueDateTime()
        if dueDateTime != self.maxDateTime:
            newDueSoonDateTime = dueDateTime + date.oneSecond - date.TimeDelta(hours=self.__dueSoonHours)
            self.registerObserver(self.onDueSoon, date.Clock.eventType(newDueSoonDateTime))    
        self.recomputeAppearance()
            
    # effort related methods:

    def efforts(self, recursive=False):
        childEfforts = []
        if recursive:
            for child in self.children():
                childEfforts.extend(child.efforts(recursive=True))
        return self._efforts + childEfforts

    def isBeingTracked(self, recursive=False):
        return self.activeEfforts(recursive)

    def activeEfforts(self, recursive=False):
        return [effort for effort in self.efforts(recursive) \
            if effort.isBeingTracked()]
    
    @patterns.eventSource    
    def addEffort(self, effort, event=None):
        if effort in self._efforts:
            return
        wasTracking = self.isBeingTracked()
        self._efforts.append(effort)
        self.addEffortEvent(event, effort)
        if effort.isBeingTracked() and not wasTracking:
            self.startTrackingEvent(event, effort)
        self.timeSpentEvent(event, effort)
  
    def addEffortEvent(self, event, *efforts):
        event.addSource(self, *efforts, **dict(type='task.effort.add'))
          
    def startTrackingEvent(self, event, *efforts):
        self.recomputeAppearance(event=event)    
        for ancestor in [self] + self.ancestors():
            event.addSource(ancestor, *efforts, 
                            **dict(type=ancestor.trackStartEventType()))

    @patterns.eventSource
    def removeEffort(self, effort, event=None):
        if effort not in self._efforts:
            return
        self._efforts.remove(effort)
        self.removeEffortEvent(event, effort)
        if effort.isBeingTracked() and not self.isBeingTracked():
            self.stopTrackingEvent(event, effort)
        self.timeSpentEvent(event, effort)
        
    def removeEffortEvent(self, event, *efforts):
        event.addSource(self, *efforts, **dict(type='task.effort.remove'))

    @patterns.eventSource
    def stopTracking(self, event=None):
        for effort in self.activeEfforts():
            effort.setStop(event=event)
                        
    def stopTrackingEvent(self, event, *efforts):
        self.recomputeAppearance(event=event)    
        for ancestor in [self] + self.ancestors():
            event.addSource(ancestor, *efforts, 
                            **dict(type=ancestor.trackStopEventType()))
        
    @patterns.eventSource
    def setEfforts(self, efforts, event=None):
        if efforts == self._efforts:
            return
        oldEfforts = self._efforts
        self._efforts = efforts
        # pylint: disable-msg=W0142
        self.removeEffortEvent(event, *oldEfforts)
        self.addEffortEvent(event, *efforts)
        self.timeSpentEvent(event, *(oldEfforts + efforts))
        
    @classmethod
    def trackStartEventType(class_):
        return '%s.track.start'%class_

    @classmethod
    def trackStopEventType(class_):
        return '%s.track.stop'%class_

    # Time spent
    
    def timeSpent(self, recursive=False):
        return sum((effort.duration() for effort in self.efforts(recursive)), 
                   date.TimeDelta())

    def timeSpentEvent(self, event, *efforts):
        event.addSource(self, *efforts, **dict(type='task.timeSpent'))
        for ancestor in self.ancestors():
            event.addSource(ancestor, *efforts, **dict(type='task.timeSpent'))
        if self.budget(recursive=True):
            self.budgetLeftEvent(event)
        if self.hourlyFee() > 0:
            self.revenueEvent(event)

    @staticmethod
    def timeSpentSortFunction(**kwargs):
        recursive = kwargs.get('treeMode', False)
        return lambda task: task.timeSpent(recursive=recursive)
    
    @classmethod
    def timeSpentSortEventTypes(class_):
        ''' The event types that influence the time spent sort order. '''
        return ('task.timeSpent',)

    
    # Budget
    
    def budget(self, recursive=False):
        result = self.__budget.get()
        if recursive:
            for task in self.children():
                result += task.budget(recursive)
        return result
        
    def setBudget(self, budget, event=None):
        self.__budget.set(budget, event=event)
        
    def budgetEvent(self, event):
        event.addSource(self, self.budget(), type=self.budgetChangedEventType())
        for ancestor in self.ancestors():
            event.addSource(ancestor, ancestor.budget(recursive=True), 
                            type=self.budgetChangedEventType())
        self.budgetLeftEvent(event)

    @classmethod
    def budgetChangedEventType(class_):
        return '%s.budget' % class_

    @staticmethod
    def budgetSortFunction(**kwargs):
        recursive = kwargs.get('treeMode', False)
        return lambda task: task.budget(recursive=recursive)
    
    @classmethod
    def budgetSortEventTypes(class_):
        ''' The event types that influence the budget sort order. '''
        return (class_.budgetChangedEventType(),)

    # Budget left
    
    def budgetLeft(self, recursive=False):
        budget = self.budget(recursive)
        return budget - self.timeSpent(recursive) if budget else budget

    def budgetLeftEvent(self, event):
        event.addSource(self, self.budgetLeft(), type='task.budgetLeft')
        for ancestor in self.ancestors():
            event.addSource(ancestor, ancestor.budgetLeft(recursive=True), 
                            type='task.budgetLeft')

    @staticmethod
    def budgetLeftSortFunction(**kwargs):
        recursive = kwargs.get('treeMode', False)
        return lambda task: task.budgetLeft(recursive=recursive)

    @classmethod
    def budgetLeftSortEventTypes(class_):
        ''' The event types that influence the budget left sort order. '''
        return ('task.budgetLeft',)

    # Foreground color

    def setForegroundColor(self, *args, **kwargs):
        super(Task, self).setForegroundColor(*args, **kwargs)
        self.__computeRecursiveForegroundColor()
    
    def foregroundColor(self, recursive=False):
        if not recursive:
            return super(Task, self).foregroundColor(recursive)
        try:
            return self.__recursiveForegroundColor
        except AttributeError:
            return self.__computeRecursiveForegroundColor()
        
    def __computeRecursiveForegroundColor(self, *args, **kwargs): # pylint: disable-msg=W0613
        fgColor = super(Task, self).foregroundColor(recursive=True)
        statusColor = self.statusFgColor()
        if statusColor == wx.BLACK:
            recursiveColor = fgColor
        elif fgColor == None:
            recursiveColor = statusColor
        else:
            recursiveColor = color.ColorMixer.mix((fgColor, statusColor))
        self.__recursiveForegroundColor = recursiveColor # pylint: disable-msg=W0201
        return recursiveColor
    
    def statusFgColor(self):
        ''' Return the current color of task, based on its status (completed,
            overdue, duesoon, inactive, or active). '''            
        return self.fgColorForStatus(self.status())
    
    @classmethod
    def fgColorForStatus(class_, status):
        return wx.Colour(*eval(class_.settings.get('fgcolor', '%stasks'%status))) # pylint: disable-msg=E1101

    def appearanceChangedEvent(self, event):
        self.__computeRecursiveForegroundColor()
        self.__computeRecursiveBackgroundColor()
        self.__computeRecursiveIcon()
        self.__computeRecursiveSelectedIcon()
        super(Task, self).appearanceChangedEvent(event)
        for eachEffort in self.efforts():
            eachEffort.appearanceChangedEvent(event)
        
    def status(self):
        if self.completed():
            return 'completed'
        elif self.overdue(): 
            return 'overdue'
        elif self.dueSoon():
            return 'duesoon'
        elif self.inactive(): 
            return 'inactive'
        else:
            return 'active'
        
    # Background color
    
    def setBackgroundColor(self, *args, **kwargs):
        super(Task, self).setBackgroundColor(*args, **kwargs)
        self.__computeRecursiveBackgroundColor()
        
    def backgroundColor(self, recursive=False):
        if not recursive:
            return super(Task, self).backgroundColor(recursive)
        try:
            return self.__recursiveBackgroundColor
        except AttributeError:
            return self.__computeRecursiveBackgroundColor()
        
    def __computeRecursiveBackgroundColor(self, *args, **kwargs): # pylint: disable-msg=W0613
        bgColor = super(Task, self).backgroundColor(recursive=True)
        statusColor = self.statusBgColor()
        if statusColor == wx.WHITE:
            recursiveColor = bgColor
        elif bgColor == None:
            recursiveColor = statusColor
        else:
            recursiveColor = color.ColorMixer.mix((bgColor, statusColor))
        self.__recursiveBackgroundColor = recursiveColor # pylint: disable-msg=W0201
        return recursiveColor
    
    def statusBgColor(self):
        ''' Return the current color of task, based on its status (completed,
            overdue, duesoon, inactive, or active). '''            
        return self.bgColorForStatus(self.status())
    
    @classmethod
    def bgColorForStatus(class_, status):
        return wx.Colour(*eval(class_.settings.get('bgcolor', '%stasks'%status))) # pylint: disable-msg=E1101
    
    # Font

    def font(self, recursive=False):
        myFont = super(Task, self).font()
        if myFont or not recursive:
            return myFont
        recursiveFont = super(Task, self).font(recursive=True)
        if recursiveFont:
            return recursiveFont
        else:
            return self.statusFont()

    def statusFont(self):
        ''' Return the current font of task, based on its status (completed,
            overdue, duesoon, inactive, or active). '''
        return self.fontForStatus(self.status())            

    @classmethod
    def fontForStatus(class_, status):
        nativeInfoString = class_.settings.get('font', '%stasks'%status) # pylint: disable-msg=E1101
        return wx.FontFromNativeInfoString(nativeInfoString) if nativeInfoString else None
                
    # Icon
    
    def icon(self, recursive=False):
        if recursive and self.isBeingTracked():
            return 'clock_icon'
        myIcon = super(Task, self).icon()
        if recursive and not myIcon:
            try:
                myIcon = self.__recursiveIcon
            except AttributeError:
                myIcon = self.__computeRecursiveIcon()
        return self.pluralOrSingularIcon(myIcon)
    
    def __computeRecursiveIcon(self, *args, **kwargs): # pylint: disable-msg=W0613
        # pylint: disable-msg=W0201
        self.__recursiveIcon = self.categoryIcon() or self.statusIcon()
        return self.__recursiveIcon

    def selectedIcon(self, recursive=False):
        if recursive and self.isBeingTracked():
            return 'clock_icon'
        myIcon = super(Task, self).selectedIcon()
        if recursive and not myIcon:
            try:
                myIcon = self.__recursiveSelectedIcon
            except AttributeError:
                myIcon = self.__computeRecursiveSelectedIcon() 
        return self.pluralOrSingularIcon(myIcon)
        
    def __computeRecursiveSelectedIcon(self, *args, **kwargs): # pylint: disable-msg=W0613
        # pylint: disable-msg=W0201
        self.__recursiveSelectedIcon = self.categorySelectedIcon() or self.statusIcon(selected=True)
        return self.__recursiveSelectedIcon

    def statusIcon(self, selected=False):
        ''' Return the current icon of the task, based on its status (completed,
            overdue, duesoon, inactive, or active). '''
        return self.iconForStatus(self.status(), selected)            

    def iconForStatus(self, status, selected=False):
        iconName = self.settings.get('icon', '%stasks'%status) # pylint: disable-msg=E1101
        iconName = self.pluralOrSingularIcon(iconName)
        if selected and iconName.startswith('folder'):
            iconName = iconName[:-len('_icon')] + '_open_icon' 
        return iconName

    @patterns.eventSource
    def recomputeAppearance(self, recursive=False, event=None):
        # Need to prepare for AttributeError because the cached recursive values
        # are not set in __init__ for performance reasons
        try:
            previousForegroundColor = self.__recursiveForegroundColor
            previousBackgroundColor = self.__recursiveBackgroundColor
            previousRecursiveIcon = self.__recursiveIcon
            previousRecursiveSelectedIcon = self.__recursiveSelectedIcon
        except AttributeError:
            previousForegroundColor = None
            previousBackgroundColor = None
            previousRecursiveIcon = None
            previousRecursiveSelectedIcon = None
        self.__computeRecursiveForegroundColor()
        self.__computeRecursiveBackgroundColor()
        self.__computeRecursiveIcon()
        self.__computeRecursiveSelectedIcon()
        if self.__recursiveForegroundColor != previousForegroundColor or \
           self.__recursiveBackgroundColor != previousBackgroundColor or \
           self.__recursiveIcon != previousRecursiveIcon or \
           self.__recursiveSelectedIcon != previousRecursiveSelectedIcon:
            event.addSource(self, type=self.appearanceChangedEventType())
        if recursive:
            for child in self.children():
                child.recomputeAppearance(recursive=True, event=event)
                
    # percentage Complete
    
    def percentageComplete(self, recursive=False):
        myPercentage = self.__percentageComplete.get()
        if recursive:
            # We ignore our own percentageComplete when we are marked complete
            # when all children are completed *and* our percentageComplete is 0
            percentages = []
            if myPercentage > 0 or not self.shouldMarkCompletedWhenAllChildrenCompleted():
                percentages.append(myPercentage)
            percentages.extend([child.percentageComplete(recursive) for child in self.children()])
            return sum(percentages)/len(percentages) if percentages else 0
        else:
            return myPercentage
        
    @patterns.eventSource
    def setPercentageComplete(self, percentage, event=None):
        if percentage == self.percentageComplete():
            return
        oldPercentage = self.percentageComplete()
        self.__percentageComplete.set(percentage, event=event)
        if percentage == 100 and oldPercentage != 100 and self.completionDateTime() == self.maxDateTime:
            self.setCompletionDateTime(date.Now(), event=event)
        elif oldPercentage == 100 and percentage != 100 and self.completionDateTime() != self.maxDateTime:
            self.setCompletionDateTime(self.maxDateTime, event=event)
    
    def percentageCompleteEvent(self, event):
        event.addSource(self, self.percentageComplete(), 
                        type=self.percentageCompleteChangedEventType())
        for ancestor in self.ancestors():
            event.addSource(ancestor, ancestor.percentageComplete(recursive=True), 
                            type=self.percentageCompleteChangedEventType())
    
    @staticmethod
    def percentageCompleteSortFunction(**kwargs):
        recursive = kwargs.get('treeMode', False)
        return lambda task: task.percentageComplete(recursive=recursive)

    @classmethod
    def percentageCompleteSortEventTypes(class_):
        ''' The event types that influence the percentage complete sort order. '''
        return (class_.percentageCompleteChangedEventType(),)

    @classmethod
    def percentageCompleteChangedEventType(class_):
        return '%s.percentageComplete' % class_
       
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
        self.__priority.set(priority, event=event)
        
    def priorityEvent(self, event):
        event.addSource(self, self.priority(), type=self.priorityChangedEventType())
        for ancestor in self.ancestors():
            event.addSource(ancestor, ancestor.priority(recursive=True),
                            type=self.priorityChangedEventType())

    @classmethod
    def priorityChangedEventType(class_):
        return '%s.priority' % class_

    @staticmethod
    def prioritySortFunction(**kwargs):
        recursive = kwargs.get('treeMode', False)
        return lambda task: task.priority(recursive=recursive)

    @classmethod
    def prioritySortEventTypes(class_):
        ''' The event types that influence the priority sort order. '''
        return (class_.priorityChangedEventType(),)
    
    # Hourly fee
    
    def hourlyFee(self, recursive=False): # pylint: disable-msg=W0613
        return self.__hourlyFee.get()
    
    def setHourlyFee(self, hourlyFee, event=None):
        self.__hourlyFee.set(hourlyFee, event=event)

    def hourlyFeeEvent(self, event):
        event.addSource(self, self.hourlyFee(), 
                        type=self.hourlyFeeChangedEventType())
        if self.timeSpent() > date.TimeDelta():
            for objectWithRevenue in [self] + self.efforts():
                objectWithRevenue.revenueEvent(event)
            
    @classmethod
    def hourlyFeeChangedEventType(class_):
        return '%s.hourlyFee'%class_
    
    @staticmethod # pylint: disable-msg=W0613
    def hourlyFeeSortFunction(**kwargs): 
        return lambda task: task.hourlyFee()

    @classmethod
    def hourlyFeeSortEventTypes(class_):
        ''' The event types that influence the hourly fee sort order. '''
        return (class_.hourlyFeeChangedEventType(),)
    
    # Fixed fee
                 
    def fixedFee(self, recursive=False):
        childFixedFees = sum(child.fixedFee(recursive) for child in 
                             self.children()) if recursive else 0
        return self.__fixedFee.get() + childFixedFees
    
    def setFixedFee(self, fixedFee, event=None):
        self.__fixedFee.set(fixedFee, event=event)

    @classmethod
    def fixedFeeChangedEventType(class_):
        return '%s.fixedFee' % class_

    def fixedFeeEvent(self, event):
        event.addSource(self, self.fixedFee(), type=self.fixedFeeChangedEventType())
        for ancestor in self.ancestors():
            event.addSource(ancestor, ancestor.fixedFee(recursive=True),
                            type=self.fixedFeeChangedEventType())
        self.revenueEvent(event)

    @staticmethod
    def fixedFeeSortFunction(**kwargs):
        recursive = kwargs.get('treeMode', False)
        return lambda task: task.fixedFee(recursive=recursive)

    @classmethod
    def fixedFeeSortEventTypes(class_):
        ''' The event types that influence the fixed fee sort order. '''
        return (class_.fixedFeeChangedEventType(),)

    # Revenue        
        
    def revenue(self, recursive=False):
        childRevenues = sum(child.revenue(recursive) for child in 
                            self.children()) if recursive else 0
        return self.timeSpent().hours() * self.hourlyFee() + self.fixedFee() + \
               childRevenues

    def revenueEvent(self, event):
        event.addSource(self, self.revenue(), type='task.revenue')
        for ancestor in self.ancestors():
            event.addSource(ancestor, ancestor.revenue(recursive=False), 
                            type='task.revenue')

    @staticmethod
    def revenueSortFunction(**kwargs):            
        recursive = kwargs.get('treeMode', False)
        return lambda task: task.revenue(recursive=recursive)

    @classmethod
    def revenueSortEventTypes(class_):
        ''' The event types that influence the revenue sort order. '''
        return ('task.revenue',)
    
    # reminder
    
    def reminder(self, recursive=False, includeSnooze=True): # pylint: disable-msg=W0613
        if recursive:
            reminders = [child.reminder(recursive=True) for child in \
                         self.children()] + [self.__reminder.get()]
            reminders = [reminder for reminder in reminders if reminder]
            return min(reminders) if reminders else None
        else:
            return self.__reminder.get() if includeSnooze else self.__reminderBeforeSnooze

    def setReminder(self, reminderDateTime=None, event=None):
        if reminderDateTime == self.maxDateTime:
            reminderDateTime = None
        self.__reminder.set(reminderDateTime, event=event)
        self.__reminderBeforeSnooze = reminderDateTime
        
    def snoozeReminder(self, timeDelta, event=None, now=date.Now):
        newReminderDateTime = now() + timeDelta if timeDelta else None
        self.__reminder.set(newReminderDateTime, event=event)

    def reminderEvent(self, event):
        event.addSource(self, self.reminder(), type=self.reminderChangedEventType())
    
    @staticmethod
    def reminderSortFunction(**kwargs):
        recursive = kwargs.get('treeMode', False)
        maxDateTime = date.DateTime()
        return lambda task: task.reminder(recursive=recursive) or maxDateTime

    @classmethod
    def reminderSortEventTypes(class_):
        ''' The event types that influence the reminder sort order. '''
        return (class_.reminderChangedEventType(),)

    @classmethod
    def reminderChangedEventType(class_):
        return '%s.reminder' % class_

    # Recurrence
    
    def recurrence(self, recursive=False, upwards=False):
        if not self._recurrence and recursive and upwards and self.parent():
            return self.parent().recurrence(recursive, upwards)
        elif recursive and not upwards:
            recurrences = [child.recurrence() for child in self.children(recursive)]
            recurrences.append(self._recurrence)
            recurrences = [r for r in recurrences if r]
            return min(recurrences) if recurrences else self._recurrence
        else:
            return self._recurrence

    @patterns.eventSource
    def setRecurrence(self, recurrence=None, event=None):
        recurrence = recurrence or date.Recurrence()
        if recurrence == self._recurrence:
            return
        self._recurrence = recurrence
        event.addSource(self, recurrence, type=self.recurrenceChangedEventType())

    @patterns.eventSource
    def recur(self, completionDateTime=None, event=None):
        completionDateTime = completionDateTime or date.Now()
        self.setCompletionDateTime(self.maxDateTime, event=event)
        recur = self.recurrence(recursive=True, upwards=True)
        
        currentDueDateTime = self.dueDateTime()
        if currentDueDateTime != date.DateTime():        
            basisForRecurrence = completionDateTime if recur.recurBasedOnCompletion else currentDueDateTime 
            nextDueDateTime = recur(basisForRecurrence, next=False)
            nextDueDateTime = nextDueDateTime.replace(hour=currentDueDateTime.hour,
                                                      minute=currentDueDateTime.minute,
                                                      second=currentDueDateTime.second,
                                                      microsecond=currentDueDateTime.microsecond)
            self.setDueDateTime(nextDueDateTime, event=event)
        
        currentStartDateTime = self.startDateTime()
        if currentStartDateTime != date.DateTime():        
            if date.DateTime() not in (currentStartDateTime, currentDueDateTime):
                taskDuration = currentDueDateTime - currentStartDateTime
                nextStartDateTime = nextDueDateTime - taskDuration
            else:
                basisForRecurrence = completionDateTime if recur.recurBasedOnCompletion else currentStartDateTime
                nextStartDateTime = recur(basisForRecurrence, next=False)
            nextStartDateTime = nextStartDateTime.replace(hour=currentStartDateTime.hour,
                                                          minute=currentStartDateTime.minute,
                                                          second=currentStartDateTime.second,
                                                          microsecond=currentStartDateTime.microsecond)
            self.setStartDateTime(nextStartDateTime, event=event)
        
        self.setPercentageComplete(0, event=event)
        if self.reminder():
            nextReminder = recur(self.reminder(includeSnooze=False), next=False)
            self.setReminder(nextReminder, event=event)
        for child in self.children():
            if not child.recurrence():
                child.recur(completionDateTime, event=event)
        self.recurrence()(next=True)

    @staticmethod
    def recurrenceSortFunction(**kwargs):
        recursive = kwargs.get('treeMode', False)
        return lambda task: task.recurrence(recursive=recursive)

    @classmethod
    def recurrenceSortEventTypes(class_):
        ''' The event types that influence the recurrence sort order. '''
        return (class_.recurrenceChangedEventType(),)

    @classmethod
    def recurrenceChangedEventType(class_):
        return '%s.recurrence' % class_

    # Prerequisites
    
    def prerequisites(self, recursive=False):
        prerequisites = self.__prerequisites.get() 
        if recursive:
            for child in self.children():
                prerequisites |= child.prerequisites(recursive)
        return prerequisites
    
    @patterns.eventSource
    def setPrerequisites(self, prerequisites, event=None):
        self.__prerequisites.set(set(prerequisites), event=event)
        self.recomputeAppearance(recursive=True, event=event)
        
    @patterns.eventSource
    def addPrerequisites(self, prerequisites, event=None):
        self.__prerequisites.add(set(prerequisites), event=event)
        self.recomputeAppearance(recursive=True, event=event)
        
    @patterns.eventSource
    def removePrerequisites(self, prerequisites, event=None):
        self.__prerequisites.remove(set(prerequisites), event=event)
        self.recomputeAppearance(recursive=True, event=event)
        
    @patterns.eventSource
    def addTaskAsDependencyOf(self, prerequisites, event=None):
        for prerequisite in prerequisites:
            prerequisite.addDependencies([self], event=event)
    
    @patterns.eventSource
    def removeTaskAsDependencyOf(self, prerequisites, event=None):
        for prerequisite in prerequisites:
            prerequisite.removeDependencies([self], event=event)
            
    def prerequisitesEvent(self, event, *prerequisites):
        event.addSource(self, *prerequisites, **dict(type='task.prerequisites'))
        self.recomputeAppearance(event=event)

    @staticmethod
    def prerequisitesSortFunction(**kwargs):
        ''' Return a sort key for sorting by prerequisites. Since a task can 
            have multiple prerequisites we first sort the prerequisites by their
            subjects. If the sorter is in tree mode, we also take the 
            prerequisites of the children of the task into account, after the 
            prerequisites of the task itself. '''
        def sortKeyFunction(task):
            def sortedSubjects(items):
                return sorted([item.subject(recursive=True) for item in items])
            prerequisites = task.prerequisites()
            sortedPrerequisiteSubjects = sortedSubjects(prerequisites)
            if kwargs.get('treeMode', False):
                childPrerequisites = task.prerequisites(recursive=True) - prerequisites
                sortedPrerequisiteSubjects.extend(sortedSubjects(childPrerequisites)) 
            return sortedPrerequisiteSubjects
        return sortKeyFunction

    @classmethod
    def prerequisitesSortEventTypes(class_):
        ''' The event types that influence the prerequisites sort order. '''
        return ('task.prerequisites')

    # Dependencies
    
    def dependencies(self, recursive=False):
        dependencies = self.__dependencies.get()
        if recursive:
            for child in self.children():
                dependencies |= child.dependencies(recursive)
        return dependencies

    def setDependencies(self, dependencies, event=None):
        self.__dependencies.set(set(dependencies), event=event)
    
    def addDependencies(self, dependencies, event=None):
        self.__dependencies.add(set(dependencies), event=event)
                
    def removeDependencies(self, dependencies, event=None):
        self.__dependencies.remove(set(dependencies), event=event)
        
    @patterns.eventSource
    def addTaskAsPrerequisiteOf(self, dependencies, event=None):
        for dependency in dependencies:
            dependency.addPrerequisites([self], event=event)
            
    @patterns.eventSource
    def removeTaskAsPrerequisiteOf(self, dependencies, event=None):
        for dependency in dependencies:
            dependency.removePrerequisites([self], event=event)      

    def dependenciesEvent(self, event, *dependencies):
        event.addSource(self, *dependencies, **dict(type='task.dependencies'))

    @staticmethod
    def dependenciesSortFunction(**kwargs):
        ''' Return a sort key for sorting by dependencies. Since a task can 
            have multiple dependencies we first sort the dependencies by their
            subjects. If the sorter is in tree mode, we also take the 
            dependencies of the children of the task into account, after the 
            dependencies of the task itself. '''
        def sortKeyFunction(task):
            def sortedSubjects(items):
                return sorted([item.subject(recursive=True) for item in items])
            dependencies = task.dependencies()
            sortedDependencySubjects = sortedSubjects(dependencies)
            if kwargs.get('treeMode', False):
                childDependencies = task.dependencies(recursive=True) - dependencies
                sortedDependencySubjects.extend(sortedSubjects(childDependencies)) 
            return sortedDependencySubjects
        return sortKeyFunction

    @classmethod
    def dependenciesSortEventTypes(class_):
        ''' The event types that influence the dependencies sort order. '''
        return ('task.dependencies',)
                
    # behavior
    
    @patterns.eventSource
    def setShouldMarkCompletedWhenAllChildrenCompleted(self, newValue, event=None):
        if newValue == self._shouldMarkCompletedWhenAllChildrenCompleted:
            return
        self._shouldMarkCompletedWhenAllChildrenCompleted = newValue
        event.addSource(self, newValue, 
                        type=self.shouldMarkCompletedWhenAllChildrenCompletedChangedEventType())
        event.addSource(self, self.percentageComplete(recursive=True), 
                        type=self.percentageCompleteChangedEventType())

    def shouldMarkCompletedWhenAllChildrenCompleted(self):
        return self._shouldMarkCompletedWhenAllChildrenCompleted

    @classmethod
    def shouldMarkCompletedWhenAllChildrenCompletedChangedEventType(class_):
        return '%s.setting.shouldMarkCompletedWhenAllChildrenCompleted' % class_

    @classmethod
    def suggestedStartDateTime(cls, now=date.Now):
        return cls.suggestedDateTime('defaultstartdatetime', now)
    
    @classmethod
    def suggestedDueDateTime(cls, now=date.Now):
        return cls.suggestedDateTime('defaultduedatetime', now)
        
    @classmethod
    def suggestedCompletionDateTime(cls, now=date.Now):
        return cls.suggestedDateTime('defaultcompletiondatetime', now)
    
    @classmethod
    def suggestedReminderDateTime(cls, now=date.Now):
        return cls.suggestedDateTime('defaultreminderdatetime', now)
    
    @classmethod    
    def suggestedDateTime(cls, defaultDateTimeSetting, now=date.Now):
        # pylint: disable-msg=E1101
        defaultDateTime = cls.settings.get('view', defaultDateTimeSetting)
        if defaultDateTime == 'today_startofday':
            return now().startOfDay()
        elif defaultDateTime == 'today_startofworkingday':
            startHour = cls.settings.getint('view', 'efforthourstart')
            return now().replace(hour=startHour, minute=0,
                                 second=0, microsecond=0)
        elif defaultDateTime == 'today_currenttime':
            return now()
        elif defaultDateTime == 'today_endofworkingday':
            endHour = cls.settings.getint('view', 'efforthourend')
            return now().replace(hour=endHour, minute=0,
                                 second=0, microsecond=0)
        elif defaultDateTime == 'today_endofday':
            return now().endOfDay()
        elif defaultDateTime == 'tomorrow_startofday':
            return (now() + date.oneDay).startOfDay()
        elif defaultDateTime == 'tomorrow_startofworkingday':
            startHour = cls.settings.getint('view', 'efforthourstart')
            return (now() + date.oneDay).replace(hour=startHour, minute=0, 
                                                 second=0, microsecond=0)
        elif defaultDateTime == 'tomorrow_currenttime':
            return now() + date.TimeDelta(hours=24)
        elif defaultDateTime == 'tomorrow_endofworkingday':
            endHour = cls.settings.getint('view', 'efforthourend')
            return (now() + date.oneDay).replace(hour=endHour, minute=0,
                                                 second=0, microsecond=0)
        elif defaultDateTime == 'tomorrow_endofday':
            return (now() + date.oneDay).endOfDay()
        
    @classmethod
    def modificationEventTypes(class_):
        eventTypes = super(Task, class_).modificationEventTypes()
        return eventTypes + [class_.dueDateTimeChangedEventType(),
                             class_.startDateTimeChangedEventType(),
                             class_.completionDateTimeChangedEventType(),
                             'task.effort.add', 'task.effort.remove', 
                             class_.budgetChangedEventType(),
                             class_.percentageCompleteChangedEventType(),
                             class_.priorityChangedEventType(),
                             class_.hourlyFeeChangedEventType(), 
                             class_.fixedFeeChangedEventType(),
                             class_.reminderChangedEventType(),
                             class_.recurrenceChangedEventType(),
                             'task.prerequisites', 'task.dependencies',
                             class_.shouldMarkCompletedWhenAllChildrenCompletedChangedEventType()]
