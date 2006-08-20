import patterns, re
import domain.date as date

class Filter(patterns.SetDecorator):
    def __init__(self, *args, **kwargs):
        self.setTreeMode(kwargs.pop('treeMode', False))
        super(Filter, self).__init__(*args, **kwargs)
        
    def setTreeMode(self, treeMode):
        self.__treeMode = treeMode
        
    def treeMode(self):
        return self.__treeMode

    def extendSelf(self, items):
        super(Filter, self).extendSelf(self.filter(items))

    def removeItemsFromSelf(self, items):
        itemsToRemoveFromSelf = [item for item in items if item in self]
        super(Filter, self).removeItemsFromSelf(itemsToRemoveFromSelf)
        
    def reset(self):
        filteredItems = self.filter(self.observable())
        itemsToAdd = [item for item in filteredItems if item not in self]
        itemsToRemove = [item for item in self if item not in filteredItems]
        self.removeItemsFromSelf(itemsToRemove)
        self.extendSelf(itemsToAdd)
            
    def filter(self, items):
        ''' filter returns the items that pass the filter. '''
        raise NotImplementedError

    def rootTasks(self):
        return [task for task in self if task.parent() is None]

    def onSettingChanged(self, event):
        self.reset()

    
class ViewFilter(Filter):
    def __init__(self, *args, **kwargs):
        self.__settings = kwargs.pop('settings')
        for setting in ('tasksdue', 'completedtasks', 'inactivetasks',
                        'activetasks', 'overduetasks', 'overbudgettasks'):
            patterns.Publisher().registerObserver(self.onSettingChanged,
                eventType='view.%s'%setting)
        for eventType in ('task.dueDate', 'task.startDate', 
                          'task.completionDate', 'task.budgetLeft'):
            patterns.Publisher().registerObserver(self.onTaskChange,
                eventType=eventType)
        super(ViewFilter, self).__init__(*args, **kwargs)

    def onTaskChange(self, event):
        self.addOrRemoveTask(event.source())

    def addOrRemoveTask(self, task):
        if self.filter([task]):
            if task in self.observable() and task not in self:
                self.extendSelf([task])
        else:
            if task in self and task not in self.observable():
                self.removeItemsFromSelf([task])
        
    def getViewTasksDueBeforeDate(self):
        dateFactory = { 'Today' : date.Today, 
                        'Tomorrow' : date.Tomorrow,
                        'Workweek' : date.NextFriday, 
                        'Week' : date.NextSunday, 
                        'Month' : date.LastDayOfCurrentMonth, 
                        'Year' : date.LastDayOfCurrentYear, 
                        'Unlimited' : date.Date }        
        return dateFactory[self.__settings.get('view', 'tasksdue')]()
        
    def filter(self, tasks):
        settings = [not self.__settings.getboolean('view', setting) \
                    for setting in ('completedtasks', 'inactivetasks', 
                    'overduetasks', 'activetasks', 'overbudgettasks')]
        settings.append(self.getViewTasksDueBeforeDate())
        return [task for task in tasks if self.filterTask(task, *settings)]
    
    def filterTask(self, task, hideCompletedTasks, hideInactiveTasks, 
                   hideOverdueTasks, hideActiveTasks, hideOverBudgetTasks,
                   viewTasksDueBeforeDate):
        result = True
        if hideCompletedTasks and task.completed():
            result = False
        elif hideInactiveTasks and task.inactive():
            result = False
        elif hideOverdueTasks and task.overdue():
            result = False
        elif hideActiveTasks and task.active():
            result = False
        elif hideOverBudgetTasks and \
            task.budgetLeft(recursive=True) < date.TimeDelta():
            result = False
        elif task.dueDate(recursive=self.treeMode()) > viewTasksDueBeforeDate:
            result = False        
        return result
        
        
class CompositeFilter(Filter):
    ''' Filter composite tasks '''
    def __init__(self, *args, **kwargs):
        self.__settings = kwargs.pop('settings')
        patterns.Publisher().registerObserver(self.onSettingChanged, 
            eventType='view.compositetasks')
        patterns.Publisher().registerObserver(self.onAddChild, 
            eventType='task.child.add')
        patterns.Publisher().registerObserver(self.onRemoveChild, 
            eventType='task.child.remove')
        super(CompositeFilter, self).__init__(*args, **kwargs)
    
    def onAddChild(self, event):
        task = event.source()
        if task in self and not self.filter([task]):
            self.removeItemsFromSelf([task])

    def onRemoveChild(self, event):
        task = event.source()
        if task not in self and self.filter([task]):
            self.extendSelf([task])
        
    def filter(self, tasks):
        viewCompositeTasks = self.__settings.getboolean('view',
                                                        'compositetasks')
        return [task for task in tasks if (viewCompositeTasks or \
                not task.children())]
    

class SearchFilter(Filter):
    def __init__(self, *args, **kwargs):
        self.__settings = kwargs.pop('settings')
        for eventType in ('view.tasksearchfilterstring', 
                        'view.tasksearchfiltermatchcase'):
            patterns.Publisher().registerObserver(self.onSettingChanged, 
                eventType=eventType)
        super(SearchFilter, self).__init__(*args, **kwargs)

    def filter(self, tasks):
        taskSearchFilterString = self.__settings.get('view',
            'tasksearchfilterstring')
        regularExpression = re.compile(taskSearchFilterString, 
                                       self.__matchCase())
        return [task for task in tasks if \
                regularExpression.search(self.__taskSubject(task))]
        
    def __taskSubject(self, task):
        subject = task.subject()
        if self.treeMode():
            subject += ' '.join([child.subject() for child in task.allChildren()
                if child in self.observable()])
        return subject
    
    def __matchCase(self):
        if self.__settings.getboolean('view', 'tasksearchfiltermatchcase'):
            return 0
        else:
            return re.IGNORECASE


class CategoryFilter(Filter):
    def __init__(self, *args, **kwargs):
        self.__settings = kwargs.pop('settings')
        patterns.Publisher().registerObserver(self.onSettingChanged, 
            eventType='view.taskcategoryfiltermatchall')
        patterns.Publisher().registerObserver(self.onSettingChanged,
            eventType='view.taskcategoryfilterlist')
        super(CategoryFilter, self).__init__(*args, **kwargs)

    def filter(self, tasks):
        filteredCategories = self.__settings.getlist('view', 
                                                     'taskcategoryfilterlist')
        if not filteredCategories:
            return tasks
        filterOnlyWhenAllCategoriesMatch = self.__settings.getboolean('view', 
            'taskcategoryfiltermatchall')
        return [task for task in tasks if self.filterTask(task, 
                filteredCategories, filterOnlyWhenAllCategoriesMatch)]
        
    def filterTask(self, task, filteredCategories, 
                   filterOnlyWhenAllCategoriesMatch):
        taskCategories = task.categories(recursive=True)
        if self.treeMode():
            for child in task.children(recursive=True):
                taskCategories.update(child.categories())
        matches = [category in taskCategories for category in filteredCategories]
        if filterOnlyWhenAllCategoriesMatch:
            return False not in matches
        else:
            return True in matches