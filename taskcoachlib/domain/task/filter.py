import patterns, re, task
from domain import base, date
    

class ViewFilter(base.Filter):
    def __init__(self, *args, **kwargs):
        self.__dueDateFilter = self.stringToDueDate(kwargs.pop('dueDateFilter', 'Unlimited'))
        self.__hideActiveTasks = kwargs.pop('hideActiveTasks', False)
        self.__hideCompletedTasks = kwargs.pop('hideCompletedTasks', False)
        self.__hideInactiveTasks = kwargs.pop('hideInactiveTasks', False)
        self.__hideOverdueTasks = kwargs.pop('hideOverdueTasks', False)
        self.__hideOverbudgetTasks = kwargs.pop('hideOverbudgetTasks', False)
        self.__hideCompositeTasks = kwargs.pop('hideCompositeTasks', False)
        for eventType in ('task.dueDate', 'task.startDate', 
                          'task.completionDate', 'task.budgetLeft',
                          task.Task.addChildEventType(),
                          task.Task.removeChildEventType()):
            patterns.Publisher().registerObserver(self.onTaskChange,
                eventType=eventType)
        super(ViewFilter, self).__init__(*args, **kwargs)

    def onTaskChange(self, event):
        self.addOrRemoveTask(event.source())

    def addOrRemoveTask(self, task):
        if self.filterTask(task):
            if task in self.observable() and task not in self:
                self.extendSelf([task])
        else:
            self.removeItemsFromSelf([task])
            
    def setFilteredByDueDate(self, dueDateString):
        self.__dueDateFilter = self.stringToDueDate(dueDateString)
        self.reset()
    
    def hideActiveTasks(self, hide=True):
        self.__hideActiveTasks = hide
        self.reset()

    def hideInactiveTasks(self, hide=True):
        self.__hideInactiveTasks = hide
        self.reset()
        
    def hideCompletedTasks(self, hide=True):
        self.__hideCompletedTasks = hide
        self.reset()
        
    def hideOverbudgetTasks(self, hide=True):
        self.__hideOverbudgetTasks = hide
        self.reset()
        
    def hideOverdueTasks(self, hide=True):
        self.__hideOverdueTasks = hide
        self.reset()
        
    def hideCompositeTasks(self, hide=True):
        self.__hideCompositeTasks = hide
        self.reset()
        
    def filter(self, tasks):
        return [task for task in tasks if self.filterTask(task)]
    
    def filterTask(self, task):
        result = True
        if self.__hideCompletedTasks and task.completed():
            result = False
        elif self.__hideInactiveTasks and task.inactive():
            result = False
        elif self.__hideOverdueTasks and task.overdue():
            result = False
        elif self.__hideActiveTasks and task.active():
            result = False
        elif self.__hideOverbudgetTasks and \
            task.budgetLeft(recursive=True) < date.TimeDelta():
            result = False
        elif self.__hideCompositeTasks and task.children():
            result = False
        elif task.dueDate(recursive=self.treeMode()) > self.__dueDateFilter:
            result = False
        return result

    @staticmethod
    def stringToDueDate(dueDateString):
        dateFactory = { 'Today' : date.Today, 
                        'Tomorrow' : date.Tomorrow,
                        'Workweek' : date.NextFriday, 
                        'Week' : date.NextSunday, 
                        'Month' : date.LastDayOfCurrentMonth, 
                        'Year' : date.LastDayOfCurrentYear, 
                        'Unlimited' : date.Date }        
        return dateFactory[dueDateString]()
                    

class CategoryFilter(base.Filter):
    def __init__(self, *args, **kwargs):
        self.__settings = kwargs.pop('settings')
        self.__categories = kwargs.pop('categories')
        patterns.Publisher().registerObserver(self.onCategoryChanged,
            eventType=self.__categories.addItemEventType())
        patterns.Publisher().registerObserver(self.onCategoryChanged,
            eventType=self.__categories.removeItemEventType())
        patterns.Publisher().registerObserver(self.onSettingChanged, 
            eventType='view.taskcategoryfiltermatchall')
        patterns.Publisher().registerObserver(self.onSettingChanged,
            eventType='category.filter')
        super(CategoryFilter, self).__init__(*args, **kwargs)
        
    def filter(self, tasks):
        filteredCategories = [category for category in self.__categories 
                              if category.isFiltered()]
        if not filteredCategories:
            return tasks
        filterOnlyWhenAllCategoriesMatch = self.__settings.getboolean('view', 
            'taskcategoryfiltermatchall')
        return [task for task in tasks if self.filterTask(task, 
                filteredCategories, filterOnlyWhenAllCategoriesMatch)]
        
    def filterTask(self, task, filteredCategories, 
                   filterOnlyWhenAllCategoriesMatch):
        matches = [category.contains(task, self.treeMode()) 
                   for category in filteredCategories]
        if filterOnlyWhenAllCategoriesMatch:
            return False not in matches
        else:
            return True in matches
        
    def onCategoryChanged(self, event):
        self.reset()
