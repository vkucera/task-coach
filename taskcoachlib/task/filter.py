import patterns, date
import re

class Filter(patterns.ObservableListObserver):
    def onNotify(self, notification, *args, **kwargs):
        self.stopNotifying()
        changedItemsNotInSelf = [item for item in notification.itemsChanged if item not in self]
        itemsAdded = self._addItemsIfNecessary(notification.itemsAdded + changedItemsNotInSelf)
        changedItemsInSelf = [item for item in notification.itemsChanged if item in self]
        itemsRemoved = self._removeItemsIfNecessary(notification.itemsRemoved + changedItemsInSelf)
        self.startNotifying()
        itemsChanged = [item for item in notification.itemsChanged if item not in itemsAdded+itemsRemoved and item in self]
        self.notifyObservers(patterns.observer.Notification(self, itemsAdded=itemsAdded,
            itemsRemoved=itemsRemoved, itemsChanged=itemsChanged))
        
    def _addItemsIfNecessary(self, items):
        itemsToAdd = [item for item in items if self.filter(item) and item not in self]
        self._extend(itemsToAdd)
        return itemsToAdd
        
    def _removeItemsIfNecessary(self, items):
        itemsToRemove = [item for item in items if item in self and (not self.filter(item) \
            or item not in self.original())]
        self._removeItems(itemsToRemove)
        return itemsToRemove    
                        
    def resetFilter(self):
        self.onNotify(patterns.observer.Notification(self.original(), itemsChanged=self.original()))
        
    def filter(self, item):
        raise NotImplementedError
    
    def rootTasks(self):
        # FIXME: This is duplicated from TaskList. 
        # Maybe Filter should be a subclass of TaskList?
        return [task for task in self if task.parent() is None]

    
class ViewFilter(Filter):
    def __init__(self, taskList):
        self._viewCompletedTasks = self._viewInactiveTasks = True
        self._viewTasksDueBeforeDate = date.Date()
        super(ViewFilter, self).__init__(taskList)

    def setViewCompletedTasks(self, viewCompletedTasks):
        self._viewCompletedTasks = viewCompletedTasks
        self.resetFilter()

    def setViewInactiveTasks(self, viewInactiveTasks):
        self._viewInactiveTasks = viewInactiveTasks
        self.resetFilter()

    def viewTasksDueBefore(self, dateString):
        dateFactory = { 'Today' : date.Today, 
                        'Tomorrow' : date.Tomorrow,
                        'Workweek' : date.NextFriday, 
                        'Week' : date.NextSunday, 
                        'Month' : date.LastDayOfCurrentMonth, 
                        'Year' : date.LastDayOfCurrentYear, 
                        'Unlimited' : date.Date }
        self._viewTasksDueBeforeDate = dateFactory[dateString]()
        self.resetFilter()
              
    def filter(self, task):
        if task.completed() and not self._viewCompletedTasks:
            return False
        if task.inactive() and not self._viewInactiveTasks:
            return False
        if task.dueDate() > self._viewTasksDueBeforeDate:
            return False
        return True


class CompositeFilter(Filter):
    ''' Filter composite tasks '''
    def __init__(self, taskList):
        self._viewCompositeTasks = True
        super(CompositeFilter, self).__init__(taskList)

    def setViewCompositeTasks(self, viewCompositeTasks):
        self._viewCompositeTasks = viewCompositeTasks
        self.resetFilter()

    def filter(self, task):
        if task.children() and not self._viewCompositeTasks:
            return False
        else:
            return True
    

class SearchFilter(Filter):
    def __init__(self, taskList):
        self.subject = ''
        self.flag = re.IGNORECASE
        super(SearchFilter, self).__init__(taskList)

    def filter(self, task):
        childSubjects = ''.join([child.subject() for child in task.allChildren()])
        return re.search('.*%s.*'%self.subject, task.subject()+childSubjects, self.flag)

    def setSubject(self, subject=''):
        self.subject = subject
        self.resetFilter()

    def setMatchCase(self, match):
        if match:
            self.flag = 0
        else:
            self.flag = re.IGNORECASE
        self.resetFilter()


