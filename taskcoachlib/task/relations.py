''' Partly inspired by http://www.atug.com/andypatterns/rm.htm, but this 
RelationshipManager does not (at the moment) keep of list of relations, but
instead alters objects based on their relations. For example, if a task is
marked completed, it will mark all children completed. '''

import patterns, date

class TaskRelationshipManager:
    __metaclass__ = patterns.Singleton
    
    def startManaging(self, task):
        task.registerObserver(self.onNotify)
        
    def stopManaging(self, task):
        task.removeObserver(self.onNotify)
        
    def onNotify(self, notification):
        task = notification.source
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