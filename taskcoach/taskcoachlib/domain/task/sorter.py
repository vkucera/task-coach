import patterns
from domain import base, date


class Sorter(base.Sorter):
    EventTypePrefix = 'task'
    
    def __init__(self, *args, **kwargs):
        self.__rootItems = None
        self.__treeMode = kwargs.pop('treeMode', False)
        self.__sortByTaskStatusFirst = kwargs.pop('sortByTaskStatusFirst', True)
        super(Sorter, self).__init__(*args, **kwargs)
        for eventType in ('task.startDate', 'task.completionDate'):
            patterns.Publisher().registerObserver(self.reset, 
                                                  eventType=eventType)
                            
    def reset(self, *args, **kwargs):
        self.__rootItems = None     # Invalidate the root items cache
        super(Sorter, self).reset(*args, **kwargs)
        
    def extendSelf(self, *args, **kwargs):
        self.__rootItems = None     # Invalidate the root items cache
        super(Sorter, self).extendSelf(*args, **kwargs)

    def removeItemsFromSelf(self, *args, **kwargs):
        self.__rootItems = None     # Invalidate the root items cache
        super(Sorter, self).removeItemsFromSelf(*args, **kwargs)

    def rootItems(self):
        if self.__rootItems is None:
            self.__rootItems = [item for item in self if item.parent() is None]
        return self.__rootItems

    def sortByTaskStatusFirst(self, sortByTaskStatusFirst):
        self.__sortByTaskStatusFirst = sortByTaskStatusFirst
        self.reset()
                                
    def createSortKeyFunction(self):
        statusSortKey = self.__createStatusSortKey()
        regularSortKey = self.__createRegularSortKey()
        return lambda task: statusSortKey(task) + regularSortKey(task)

    def __createStatusSortKey(self):
        if self.__sortByTaskStatusFirst:
            if self._sortAscending:
                return lambda task: [task.completed(), task.inactive()]
            else:
                return lambda task: [not task.completed(), not task.inactive()]
        else:
            return lambda task: []

    def __createRegularSortKey(self):
        sortKeyName = self._sortKey
        if not self._sortCaseSensitive and sortKeyName == 'subject':
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
            sortKeyName = sortKeyName[0].lower() + sortKeyName[1:]
        return lambda task: [prepareSortValue(getattr(task, 
            sortKeyName)(**kwargs))]
    
    def _registerObserverForAttribute(self, attribute):
        # Sorter is always observing completion date and start date because
        # sorting by status depends on those two attributes, hence we don't
        # need to subscribe to these two attributes when they become the sort
        # key.
        if attribute not in ('completionDate', 'startDate'):
            super(Sorter, self)._registerObserverForAttribute(attribute)
            
    def _removeObserverForAttribute(self, attribute):
         # See comment at _registerObserverForAttribute.
        if attribute not in ('completionDate', 'startDate'):
            super(Sorter, self)._removeObserverForAttribute(attribute)
        
    def _createEventTypeFromAttribute(self, attribute):
        attribute = self.__capitalize(attribute)
        return super(Sorter, self)._createEventTypeFromAttribute(attribute)

    def __capitalize(self, attribute):
        # eventTypes for task attributes are capitalized if they start with
        # 'total', but sort keys are not (FIXME)
        if attribute.startswith('total'):
            return 'total' + attribute[len('total'):].capitalize()
        else:
            return attribute
        
