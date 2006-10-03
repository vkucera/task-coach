''' Partly inspired by http://www.atug.com/andypatterns/rm.htm, but this 
RelationshipManager does not (at the moment) keep of list of relations, but
instead alters objects based on their relations. For example, if a task is
marked completed, the RelationshipManager will mark all children completed. '''

import domain.date as date
import task
import patterns

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
        task = event.source()
        self.__setStartDateChildren(task)
        if task.parent():
            self.__setStartDateParent(task.parent(), task)

    def onDueDate(self, event):
        task = event.source()
        self.__setDueDateChildren(task)
        if task.parent():
            self.__setDueDateParent(task.parent(), task)

    def onCompletionDate(self, event):
        task = event.source()
        if task.parent():
            self.__markParentCompletedOrUncompletedIfNecessary(task.parent(), 
                task)
        if task.completed():
            self.__markUncompletedChildrenCompleted(task)
            if task.isBeingTracked():
                task.stopTracking()

    def onAddChild(self, event):
        task, child = event.source(), event.value()
        self.__markParentCompletedOrUncompletedIfNecessary(task, child)
        self.__setDueDateParent(task, child)
        if child.startDate() < task.startDate():
            task.setStartDate(child.startDate())

    def onRemoveChild(self, event):
        task = event.source()
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
        for child in task.children():
            if not child.completed():
                child.setCompletionDate(task.completionDate())
    
    def __setDueDateChildren(self, task):
        for child in task.children():
            if child.dueDate() > task.dueDate():
                child.setDueDate(task.dueDate())
                
    def __setDueDateParent(self, parent, child):
        if child.dueDate() > parent.dueDate():
            parent.setDueDate(child.dueDate())
            
    def __setStartDateChildren(self, task):
        for child in task.children():
            if task.startDate() > child.startDate():
                child.setStartDate(task.startDate())
    
    def __setStartDateParent(self, parent, child):
        if child.startDate() < parent.startDate():
            parent.setStartDate(child.startDate())
