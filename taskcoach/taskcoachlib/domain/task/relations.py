''' Partly inspired by http://www.atug.com/andypatterns/rm.htm, but this 
RelationshipManager does not (at the moment) keep of list of relations, but
instead alters objects based on their relations. For example, if a task is
marked completed, the RelationshipManager will mark all children completed. '''

import patterns, config
import domain.date as date

class TaskRelationshipManager(object):
    def __init__(self, *args, **kwargs):
        #self.__settings = kwargs.pop('settings')
        taskList = kwargs.pop('taskList')
        for task in taskList:
            self.startManaging(task)
        taskList.registerObserver(self.onTaskListChanged)    
        super(TaskRelationshipManager, self).__init__(*args, **kwargs)

    def onTaskListChanged(self, notification):
        for task in notification.itemsAdded:
            self.startManaging(task)
        for task in notification.itemsRemoved:
            self.stopManaging(task)
            
    def startManaging(self, task):
        task.registerObserver(self.onNotify)
        
    def stopManaging(self, task):
        task.removeObserver(self.onNotify)
    
    def onNotify(self, notification):
        task = notification.source
        # NB: This assumes each notification has only one of the following flags
        # set to True:
        if notification.completionDateChanged:
            if task.parent():
                self.__markParentCompletedOrUncompletedIfNecessary(task.parent(), task)
            if task.completed():
                self.__markUncompletedChildrenCompleted(task)
                if task.isBeingTracked():
                    task.stopTracking()
        elif notification.dueDateChanged:
            self.__setDueDateChildren(task)
            if task.parent():
                self.__setDueDateParent(task.parent(), task)
        elif notification.startDateChanged:
            self.__setStartDateChildren(task)
            if task.parent():
                self.__setStartDateParent(task.parent(), task)
        elif notification.childAdded:
            child = notification.childAdded
            self.__markParentCompletedOrUncompletedIfNecessary(task, child)
            self.__setDueDateParent(task, child)
            if child.startDate() < task.startDate():
                task.setStartDate(child.startDate())
        elif notification.childRemoved:
            self.__markTaskCompletedIfNecessary(task, date.Today())
        
    def __markParentCompletedOrUncompletedIfNecessary(self, parent, child):
        if child.completed():
            self.__markTaskCompletedIfNecessary(parent, child.completionDate())
        else:
            self.__markTaskUncompletedIfNecessary(parent)
                
    def __markTaskCompletedIfNecessary(self, task, completionDate):
        if task.allChildrenCompleted() and not task.completed():
            task.setCompletionDate(completionDate)
        
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
