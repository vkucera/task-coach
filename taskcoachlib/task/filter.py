import patterns, date
import re

class Filter(patterns.ObservableListObserver):
    def onNotify(self, notification, *args, **kwargs):
        self.stopNotifying()
        itemsAdded = self._addItemsIfNecessary(notification.itemsAdded + notification.itemsChanged)
        itemsRemoved = self._removeItemsIfNecessary(notification.itemsRemoved + notification.itemsChanged)
        self.startNotifying()
        itemsChanged = [item for item in notification.itemsChanged if item in self]
        self.notifyObservers(patterns.observer.Notification(self, itemsAdded=itemsAdded,
            itemsRemoved=itemsRemoved, itemsChanged=itemsChanged))
        
    def _addItemsIfNecessary(self, items):
        itemsToAdd = [item for item in items if self.filter(item) and not item in self]
        self._extend(itemsToAdd)
        return itemsToAdd
        
    def _removeItemsIfNecessary(self, items):
        itemsToRemove = [item for item in items if item in self and (not self.filter(item) \
            or not item in self.original())]
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


