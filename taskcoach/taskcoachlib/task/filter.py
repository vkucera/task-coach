import patterns, date, re, sets


class Filter(patterns.ObservableListObserver):
    def processChanges(self, notification):
        oldSelf = self[:]
        self[:] = [item for item in self.original() if self.filter(item)]
        itemsAdded = [item for item in self if item not in oldSelf]
        itemsRemoved = [item for item in oldSelf if item not in self]
        itemsChanged = [item for item in notification.itemsChanged if item in self and item not in itemsAdded+itemsRemoved]
        return itemsAdded, itemsRemoved, itemsChanged
            
    def filter(self, item):
        raise NotImplementedError

    def rootTasks(self):
        return [task for task in self if task.parent() is None]

    
class ViewFilter(Filter):
    def __init__(self, *args, **kwargs):
        super(ViewFilter, self).__init__(*args, **kwargs)
        self.setViewAll()
        
    def setViewAll(self):
        self._viewCompletedTasks = self._viewInactiveTasks = \
            self._viewActiveTasks = self._viewOverDueTasks = \
            self._viewOverBudgetTasks = True
        self._viewTasksDueBeforeDate = date.Date()
        self.reset()

    def setViewCompletedTasks(self, viewCompletedTasks):
        self._viewCompletedTasks = viewCompletedTasks
        self.reset()

    def setViewInactiveTasks(self, viewInactiveTasks):
        self._viewInactiveTasks = viewInactiveTasks
        self.reset()
        
    def setViewActiveTasks(self, viewActiveTasks):
        self._viewActiveTasks = viewActiveTasks
        self.reset()

    def setViewOverDueTasks(self, viewOverDueTasks):
        self._viewOverDueTasks = viewOverDueTasks
        self.reset()
        
    def setViewOverBudgetTasks(self, viewOverBudgetTasks):
        self._viewOverBudgetTasks = viewOverBudgetTasks
        self.reset()
        
    def viewTasksDueBefore(self, dateString):
        dateFactory = { 'Today' : date.Today, 
                        'Tomorrow' : date.Tomorrow,
                        'Workweek' : date.NextFriday, 
                        'Week' : date.NextSunday, 
                        'Month' : date.LastDayOfCurrentMonth, 
                        'Year' : date.LastDayOfCurrentYear, 
                        'Unlimited' : date.Date }
        self._viewTasksDueBeforeDate = dateFactory[dateString]()
        self.reset()
              
    def filter(self, task):
        if task.completed() and not self._viewCompletedTasks:
            return False
        if task.inactive() and not self._viewInactiveTasks:
            return False
        if task.overdue() and not self._viewOverDueTasks:
            return False
        if task.active() and not self._viewActiveTasks:
            return False
        if task.budgetLeft(recursive=True) < date.TimeDelta() and not self._viewOverBudgetTasks:
            return False
        if task.dueDate() > self._viewTasksDueBeforeDate:
            return False        
        return True


class CompositeFilter(Filter):
    ''' Filter composite tasks '''
    def __init__(self, *args, **kwargs):
        self._viewCompositeTasks = True
        super(CompositeFilter, self).__init__(*args, **kwargs)

    def setViewCompositeTasks(self, viewCompositeTasks):
        self._viewCompositeTasks = viewCompositeTasks
        self.reset()

    def filter(self, task):
        if task.children() and not self._viewCompositeTasks:
            return False
        else:
            return True
    

class SearchFilter(Filter):
    def __init__(self, *args, **kwargs):
        self.subject = ''
        self.flag = re.IGNORECASE
        super(SearchFilter, self).__init__(*args, **kwargs)

    def filter(self, task):
        childSubjects = ''.join([child.subject() for child in task.allChildren()
            if child in self.original()])
        return re.search('.*%s.*'%self.subject, task.subject()+childSubjects, self.flag)

    def setSubject(self, subject=''):
        self.subject = subject
        self.reset()

    def setMatchCase(self, match):
        if match:
            self.flag = 0
        else:
            self.flag = re.IGNORECASE
        self.reset()


class CategoryFilter(Filter):
    def __init__(self, *args, **kwargs):
        self._categories = sets.Set()
        super(CategoryFilter, self).__init__(*args, **kwargs)
        
    def filter(self, task):
        return not (task.categories(recursive=True) & self._categories) 
        
    def addCategory(self, category):
        self._categories.add(category)
        self.reset()
        
    def removeCategory(self, category):
        self._categories.discard(category)
        self.reset()
        
    def removeAllCategories(self):
        self._categories.clear()
        self.reset()
            
    def filteredCategories(self):
        return self._categories
        