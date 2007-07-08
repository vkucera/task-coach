import patterns
from domain import date


class Sorter(patterns.ListDecorator):
    def __init__(self, *args, **kwargs):
        self.__treeMode = kwargs.pop('treeMode', False)
        self.__sortKey = kwargs.pop('sortBy', 'subject')
        self.__sortAscending = kwargs.pop('sortAscending', True)
        self.__sortCaseSensitive = kwargs.pop('sortCaseSensitive', True)
        self.__sortByTaskStatusFirst = kwargs.pop('sortByTaskStatusFirst', True)
        for eventType in ('task.startDate', 'task.completionDate'):
            patterns.Publisher().registerObserver(self.reset, 
                                                  eventType=eventType)
        self.__registerObserverForTaskAttribute('task.%s'%self.__sortKey)
        super(Sorter, self).__init__(*args, **kwargs)
        
    def sortEventType(self):
        return '%s(%s).sorted'%(self.__class__, id(self))

    def extendSelf(self, tasks):
        super(Sorter, self).extendSelf(tasks)
        self.reset()
        
    # We don't need to call self.reset when removing items because removing
    # items does not influence the sort order.
    
    def sortBy(self, sortKey):
        if sortKey == self.__sortKey:
            return # no need to sort
        self.__removeObserverForTaskAttribute('task.%s'%self.__sortKey)
        self.__registerObserverForTaskAttribute('task.%s'%sortKey)
        self.__sortKey = sortKey
        self.reset()
            
    def sortAscending(self, sortAscending):
        self.__sortAscending = sortAscending
        self.reset()
        
    def sortByTaskStatusFirst(self, sortByTaskStatusFirst):
        self.__sortByTaskStatusFirst = sortByTaskStatusFirst
        self.reset()
        
    def sortCaseSensitive(self, sortCaseSensitive):
        self.__sortCaseSensitive = sortCaseSensitive
        self.reset()
        
    def reset(self, event=None):
        ''' reset does the actual sorting. If the order of the list changes, 
            observers are notified by means of the list-sorted event. '''
        oldSelf = self[:]
        self.sort(key=self.__createSortKey(), reverse=not self.__sortAscending)
        if self != oldSelf:
            patterns.Publisher().notifyObservers(patterns.Event(self, 
                self.sortEventType()))
                        
    def rootItems(self):
        return [task for task in self if task.parent() is None]

    def __createSortKey(self):
        ''' __getSortKey returns a list of values to be used for sorting. Which 
            values are returned by this method depend on sort settings such
            as __sortKey (obviously), __sortByStatusFirst and 
            __sortCaseSensitive. __getSortKey result is passed to the builtin 
            list.sort method for efficient sorting. '''
        statusSortKey = self.__createStatusSortKey()
        regularSortKey = self.__createRegularSortKey()
        return lambda task: statusSortKey(task) + regularSortKey(task)

    def __createStatusSortKey(self):
        if self.__sortByTaskStatusFirst:
            if self.__sortAscending:
                return lambda task: [task.completed(), task.inactive()]
            else:
                return lambda task: [not task.completed(), not task.inactive()]
        else:
            return lambda task: []

    def __createRegularSortKey(self):
        sortKeyName = self.__sortKey
        if not self.__sortCaseSensitive and sortKeyName == 'subject':
            prepareSortValue = lambda subject: subject.lower()
        elif sortKeyName == 'categories':
            prepareSortValue = lambda categories: sorted([category.subject() for category in categories])
        elif sortKeyName == 'reminder':
            prepareSortValue = lambda reminder: reminder or date.DateTime.max
        else:
            prepareSortValue = lambda value: value
        kwargs = {}
        if sortKeyName.startswith('total') or (self.__treeMode and sortKeyName != 'priority'):
            kwargs['recursive'] = True
            sortKeyName = sortKeyName.replace('total', '')
        return lambda task: [prepareSortValue(getattr(task, 
            sortKeyName)(**kwargs))]
    
    def __capitalize(self, eventType):
        # eventTypes for task attributes are capitalized if they start with 'total',
        # but sort keys are not (FIXME)
        if eventType.startswith('task.total'):
            return 'task.total' + eventType[len('task.total'):].capitalize()
        else:
            return eventType
        
    def __registerObserverForTaskAttribute(self, eventType):
        # Sorter is always observing completion date and start date because
        # sorting by status depends on those two attributes, hence we don't
        # need to subscribe to these two attributes when they become the sort
        # key.
        if eventType not in ('task.completionDate', 'task.startDate'):
            patterns.Publisher().registerObserver(self.reset, 
                                                  eventType=self.__capitalize(eventType))
            
    def __removeObserverForTaskAttribute(self, eventType):
         # See comment at __registerObserverForTaskAttribute.
        if eventType not in ('task.completionDate', 'task.startDate'):
            patterns.Publisher().removeObserver(self.reset, 
                                                eventType=self.__capitalize(eventType))
         