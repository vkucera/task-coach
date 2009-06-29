'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2009 Frank Niessink <frank@niessink.com>

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


''' Partly inspired by http://www.atug.com/andypatterns/rm.htm, but this 
RelationshipManager does not (at the moment) keep of list of relations, but
instead alters objects based on their relations. For example, if a task is
marked completed, the RelationshipManager will mark all children completed. '''

from taskcoachlib import patterns
from taskcoachlib.domain import date
import task


class TaskRelationshipManager(object):
    def __init__(self, *args, **kwargs):
        self.__settings = kwargs.pop('settings')
        taskList = kwargs.pop('taskList')
        super(TaskRelationshipManager, self).__init__(*args, **kwargs)
        self.handlers = (self.onStartDate, self.onDueDate, 
            self.onCompletionDate, self.onAddChild, self.onRemoveChild)
        self.eventTypes = ('task.startDate', 'task.dueDate', 
            'task.completionDate', task.Task.addChildEventType(), 
            task.Task.removeChildEventType())
        for handler, eventType in zip(self.handlers, self.eventTypes):
            patterns.Publisher().registerObserver(handler, eventType=eventType)        

    def onStartDate(self, event):
        for task in event.sources():
            if not task.recurrence(True): 
                # Let Task.recur() handle the change in start date
                self.__setStartDateChildren(task)
            if task.parent():
                self.__setStartDateParent(task.parent(), task)

    def onDueDate(self, event):
        for task in event.sources():
            self.__setDueDateChildren(task)
            if task.parent():
                self.__setDueDateParent(task.parent(), task)

    def onCompletionDate(self, event):
        for task in event.sources():
            if task.parent():
                self.__markParentCompletedOrUncompletedIfNecessary(\
                    task.parent(), task)
            if task.completed():
                self.__markUncompletedChildrenCompleted(task)
                if task.isBeingTracked():
                    task.stopTracking()

    def onAddChild(self, event):
        for task in event.sources():
            child = event.value(task)
            self.__markParentCompletedOrUncompletedIfNecessary(task, child)
            self.__setDueDateParent(task, child)
            if child.startDate() < task.startDate():
                task.setStartDate(child.startDate())

    def onRemoveChild(self, event):
        for task in event.sources():
            self.__markTaskCompletedIfNecessary(task, date.Today())

    def __markParentCompletedOrUncompletedIfNecessary(self, parent, child):
        if child.completed():
            self.__markTaskCompletedIfNecessary(parent, child.completionDate())
        else:
            self.__markTaskUncompletedIfNecessary(parent)
                
    def __markTaskCompletedIfNecessary(self, task, completionDate):
        if task.allChildrenCompleted() and not task.completed() and \
                self.__shouldMarkTaskCompletedWhenAllChildrenCompleted(task):
            task.setCompletionDate(completionDate)
    
    def __shouldMarkTaskCompletedWhenAllChildrenCompleted(self, task):
        shouldMarkCompletedAccordingToSetting = \
            self.__settings.getboolean('behavior', 
                'markparentcompletedwhenallchildrencompleted')
        shouldMarkCompletedAccordingToTask = \
            task.shouldMarkCompletedWhenAllChildrenCompleted
        return (shouldMarkCompletedAccordingToTask == True) or \
            ((shouldMarkCompletedAccordingToTask == None) and \
              shouldMarkCompletedAccordingToSetting)
      
    def __markTaskUncompletedIfNecessary(self, task):
        if task.completed():
            task.setCompletionDate(date.Date())

    def __markUncompletedChildrenCompleted(self, task):
        taskCompletionDate = task.completionDate()
        for child in task.children():
            if not child.completed():
                child.setRecurrence()
                child.setCompletionDate(taskCompletionDate)
    
    def __setDueDateChildren(self, task):
        taskDueDate = task.dueDate()
        for child in task.children():
            if child.dueDate() > taskDueDate:
                child.setDueDate(taskDueDate)
                
    def __setDueDateParent(self, parent, child):
        if child.dueDate() > parent.dueDate():
            parent.setDueDate(child.dueDate())
            
    def __setStartDateChildren(self, task):
        taskStartDate = task.startDate()
        for child in task.children():
            if taskStartDate > child.startDate():
                child.setStartDate(taskStartDate)
    
    def __setStartDateParent(self, parent, child):
        if child.startDate() < parent.startDate():
            parent.setStartDate(child.startDate())
