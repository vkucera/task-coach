import patterns, re, sets
import domain.date as date

class Filter(patterns.ObservableListObserver):
    def __init__(self, *args, **kwargs):
        self.setTreeMode(kwargs.pop('treeMode', False))
        super(Filter, self).__init__(*args, **kwargs)
        
    def setTreeMode(self, treeMode):
        self.__treeMode = treeMode
        
    def treeMode(self):
        return self.__treeMode

    def extendSelf(self, items):
        itemsToAddToSelf = [item for item in items if self.filter(item)]
        super(Filter, self).extendSelf(itemsToAddToSelf)

    def removeItemsFromSelf(self, items):
        itemsToRemoveFromSelf = [item for item in items if item in self]
        super(Filter, self).removeItemsFromSelf(itemsToRemoveFromSelf)
        
    def reset(self):
        self.removeItemsFromSelf(self.original())
        self.extendSelf(self.original())
            
    def filter(self, item):
        ''' filter returns False if the item should be hidden. '''
        raise NotImplementedError

    def rootTasks(self):
        return [task for task in self if task.parent() is None]

    def onSettingChanged(self, event):
        self.reset()

    
class ViewFilter(Filter):
    def __init__(self, *args, **kwargs):
        self.__settings = kwargs.pop('settings')
        for setting in ('tasksdue', 'completedtasks', 'inactivetasks',
                        'activetasks', 'overduetasks', 'overbudgetasks'):
            self.__settings.registerObserver(self.onSettingChanged,
                'view.%s'%setting)
        super(ViewFilter, self).__init__(*args, **kwargs)

    def extendSelf(self, tasks):
        super(ViewFilter, self).extendSelf(tasks)
        for task in tasks:
            task.registerObserver(self.onTaskChange, 'task.dueDate',
                'task.startDate', 'task.completionDate', 'task.budget',
                'task.effort.add', 'task.effort.remove')
            task.registerObserver(self.onEffortAdded, 'task.effort.add')
            task.registerObserver(self.onEffortRemoved, 'task.effort.remove')
            for effort in task.efforts():
                effort.registerObserver(self.onEffortChanged,
                    'effort.start', 'effort.stop')

    def removeItemsFromSelf(self, tasks):
        super(ViewFilter, self).removeItemsFromSelf(tasks)
        for task in tasks:
            task.removeObservers(self.onTaskChange, self.onEffortAdded,
                self.onEffortRemoved)
            for effort in task.efforts():
                effort.removeObserver(self.onEffortChanged)

    def onTaskChange(self, event):
        self.addOrRemoveTask(event.source())

    def addOrRemoveTask(self, task):
        if self.filter(task):
            if task not in self:
                self.extendSelf([task])
        else:
            if task in self:
                self.removeItemsFromSelf([task])
        
    def onEffortAdded(self, event):
        for effort in event.values():
            self.registerObserver(self.onEffortChanged, 'effort.start', 
                'effort.stop')

    def onEffortRemoved(self, event):
        for effort in event.values():
            self.removeObserver(self.onEffortChanged)

    def onEffortChanged(self, event):
        self.addOrRemoveTask(event.source().task())

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
        settings = self.__settings
        result = True
        if task.completed() and not settings.getboolean('view', 'completedtasks'):
            result = False
        elif task.inactive() and not settings.getboolean('view', 'inactivetasks'):
            result = False
        elif task.overdue() and not settings.getboolean('view', 'overduetasks'):
            result = False
        elif task.active() and not settings.getboolean('view', 'activetasks'):
            result = False
        elif task.budgetLeft(recursive=True) < date.TimeDelta() and not \
                settings.getboolean('view', 'overbudgettasks'):
            result = False
        elif task.dueDate(recursive=self.treeMode()) > self.getViewTasksDueBeforeDate():
            result = False        
        return result


class CompositeFilter(Filter):
    ''' Filter composite tasks '''
    def __init__(self, *args, **kwargs):
        self.__settings = kwargs.pop('settings')
        self.__settings.registerObserver(self.onSettingChanged, 
                                         'view.compositetasks')
        super(CompositeFilter, self).__init__(*args, **kwargs)

    def onAddItem(self, event):
        super(CompositeFilter, self).onAddItem(event)
        for task in event.values():
            task.registerObserver(self.onAddChild, 'task.child.add')
            task.registerObserver(self.onRemoveChild, 'task.child.remove')

    def onRemoveItem(self, event):
        super(CompositeFilter, self).onRemoveItem(event)
        for task in event.values():
            task.removeObservers(self.onAddChild, self.onRemoveChild)

    def onAddChild(self, event):
        task = event.source()
        if task in self and not self.filter(task):
            self.removeItemsFromSelf([task])

    def onRemoveChild(self, event):
        task = event.source()
        if task not in self and self.filter(task):
            self.extendSelf([task])
        
    def filter(self, task):
        return (not task.children()) or \
            self.__settings.getboolean('view', 'compositetasks')
    

class SearchFilter(Filter):
    def __init__(self, *args, **kwargs):
        self.__settings = kwargs.pop('settings')
        self.__settings.registerObserver(self.onSettingChanged, 
            'view.tasksearchfilterstring', 'view.tasksearchfiltermatchcase')
        super(SearchFilter, self).__init__(*args, **kwargs)

    def filter(self, task):
        return self.__matches(task)
        
    def __matches(self, task):
        return re.search('.*%s.*'%self.__settings.get('view', 
            'tasksearchfilterstring'), 
            self.__taskSubject(task), 
            self.__matchCase())

    def __taskSubject(self, task):
        subject = task.subject()
        if self.treeMode():
            subject += ' '.join([child.subject() for child in task.allChildren()
                if child in self.original()])
        return subject
    
    def __matchCase(self):
        if self.__settings.getboolean('view', 'tasksearchfiltermatchcase'):
            return 0
        else:
            return re.IGNORECASE


class CategoryFilter(Filter):
    def __init__(self, *args, **kwargs):
        self._categories = sets.Set()
        self.__settings = kwargs.pop('settings')
        self.__settings.registerObserver(self.onSettingChanged, 
            'view.taskcategoryfiltermatchall')
        super(CategoryFilter, self).__init__(*args, **kwargs)
        
    def filter(self, task):
        if not self._categories:
            return True
        filterOnlyWhenAllCategoriesMatch = self.__settings.getboolean('view', 
            'taskcategoryfiltermatchall')
        matches = [category in task.categories(recursive=True) 
                   for category in self._categories]
        if filterOnlyWhenAllCategoriesMatch:
            return False not in matches
        else:
            return True in matches
            
    def addCategory(self, category):
        self._categories.add(category)
        self.notifyObservers(patterns.Event(self, 'filter.category.add',
            category))
        self.reset()
        
    def removeCategory(self, category):
        self._categories.discard(category)
        self.notifyObservers(patterns.Event(self, 'filter.category.remove', 
            category))
        self.reset()
        
    def removeAllCategories(self):
        self._categories.clear()
        self.notifyObservers(patterns.Event(self, 'filter.category.removeall'))
        self.reset()
            
    def filteredCategories(self):
        return self._categories
                
