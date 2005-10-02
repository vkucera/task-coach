import patterns, date, re, sets


class Filter(patterns.ObservableListObserver):
    def __init__(self, *args, **kwargs):
        self.__treeMode = kwargs.pop('treeMode', False)
        super(Filter, self).__init__(*args, **kwargs)
        
    def treeMode(self):
        return self.__treeMode
        
    def processChanges(self, notification):
        oldSelf = self[:]
        self[:] = [item for item in self.original() if self.filter(item)]
        notification['itemsAdded'] = [item for item in self if item not in oldSelf]
        notification['itemsRemoved'] = [item for item in oldSelf if item not in self]
        notification['itemsChanged'] = [item for item in notification.itemsChanged if item in self and item not in notification.itemsAdded+notification.itemsRemoved]
        return notification
            
    def filter(self, item):
        raise NotImplementedError

    def rootTasks(self):
        return [task for task in self if task.parent() is None]

    def onSettingChanged(self, notification):
        self.reset()

    
class ViewFilter(Filter):
    def __init__(self, *args, **kwargs):
        self.__settings = kwargs.pop('settings')
        for setting in ('tasksdue', 'completedtasks', 'inactivetasks',
                        'activetasks', 'overduetasks', 'overbudgetasks'):
            self.__settings.registerObserver(self.onSettingChanged, ('view', setting))
        super(ViewFilter, self).__init__(*args, **kwargs)
        
    def getViewTasksDueBeforeDate(self):
        dateFactory = { 'Today' : date.Today, 
                        'Tomorrow' : date.Tomorrow,
                        'Workweek' : date.NextFriday, 
                        'Week' : date.NextSunday, 
                        'Month' : date.LastDayOfCurrentMonth, 
                        'Year' : date.LastDayOfCurrentYear, 
                        'Unlimited' : date.Date }        
        return dateFactory[self.__settings.get('view', 'tasksdue')]()
        
    def filter(self, task):
        if task.completed() and not self.__settings.getboolean('view', 'completedtasks'):
            return False
        if task.inactive() and not self.__settings.getboolean('view', 'inactivetasks'):
            return False
        if task.overdue() and not self.__settings.getboolean('view', 'overduetasks'):
            return False
        if task.active() and not self.__settings.getboolean('view', 'activetasks'):
            return False
        if task.budgetLeft(recursive=True) < date.TimeDelta() and not \
            self.__settings.getboolean('view', 'overbudgettasks'):
            return False
        if task.dueDate(recursive=self.treeMode()) > self.getViewTasksDueBeforeDate():
            return False        
        return True


class CompositeFilter(Filter):
    ''' Filter composite tasks '''
    def __init__(self, *args, **kwargs):
        self.__settings = kwargs.pop('settings')
        self.__settings.registerObserver(self.onSettingChanged, 
                                         ('view', 'compositetasks'))
        super(CompositeFilter, self).__init__(*args, **kwargs)

    def filter(self, task):
        if task.children() and not \
            self.__settings.getboolean('view', 'compositetasks'):
            return False
        else:
            return True
    

class SearchFilter(Filter):
    def __init__(self, *args, **kwargs):
        self.__subject = ''
        self.__flag = re.IGNORECASE
        super(SearchFilter, self).__init__(*args, **kwargs)

    def filter(self, task):
        childSubjects = ''.join([child.subject() for child in task.allChildren()
            if child in self.original()])
        return re.search('.*%s.*'%self.__subject, task.subject()+childSubjects, self.__flag)

    def setSubject(self, subject=''):
        self.__subject = subject
        self.reset()

    def getSubject(self):
        return self.__subject
        
    def setMatchCase(self, match):
        if match:
            self.__flag = 0
        else:
            self.__flag = re.IGNORECASE
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
        
