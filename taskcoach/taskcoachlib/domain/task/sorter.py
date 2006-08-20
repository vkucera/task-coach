import patterns

class SortOrderReverser(object):
    ''' This class is responsible for reversing the sort order from ascending
        to descending or vice versa when the sort key setting is set to the 
        same sort key twice in a row. In other words, this class will flip the 
        sort order when a user clicks on the same column in a list view twice
        in a row. '''

    # SortOrderReverser is a singleton so it can be used by multiple 
    # (Task)Sorter's.
    __metaclass__ = patterns.Singleton 
    
    def __init__(self, previousSortKey, *args, **kwargs):
        self.__previousSortKey = previousSortKey
        super(SortOrderReverser, self).__init__(*args, **kwargs)    
        patterns.Publisher().registerObserver(self.onSortKeyChanged, 
            eventType='view.sortby')
            
    def onSortKeyChanged(self, event):
        settings, newSortKey = event.source(), event.value()
        if newSortKey == self.__previousSortKey:
            newSortOrder = not settings.getboolean('view', 'sortascending')
            settings.set('view', 'sortascending', str(newSortOrder))
        else:        
            self.__previousSortKey = newSortKey


class Sorter(patterns.ListDecorator):
    def __init__(self, *args, **kwargs):
        self.__settings = kwargs.pop('settings')
        self.__treeMode = kwargs.pop('treeMode', False)
        self.__previousSortKey = self.__settings.get('view', 'sortby')
        patterns.Publisher().registerObserver(self.onSortKeyChanged, 
            eventType='view.sortby')
        for eventType in ('view.sortascending', 'view.sortbystatusfirst', 
            'view.sortcasesensitive', 'task.startDate', 'task.completionDate'):
            patterns.Publisher().registerObserver(self.reset, 
                                                  eventType=eventType)
        self.__registerObserverForTaskAttribute('task.%s'%self.__previousSortKey)
        SortOrderReverser(self.__previousSortKey)
        super(Sorter, self).__init__(*args, **kwargs)
        
    def sortEventType(self):
        return '%s.sorted'%self.__class__

    def extendSelf(self, tasks):
        super(Sorter, self).extendSelf(tasks)
        self.reset()
        
    # We don't need to call self.reset when removing items because removing
    # items does not influence the sort order.
    
    def onSortKeyChanged(self, event):
        newSortKey, previousSortKey = event.value(), self.__previousSortKey
        if newSortKey == previousSortKey:
            # We don't call self.reset() because the sort order will be changed
            # by the SortOrderReverser, which will trigger another event
            pass
        else:
            self.__removeObserverForTaskAttribute('task.%s'%previousSortKey)
            self.__registerObserverForTaskAttribute('task.%s'%newSortKey)
            self.__previousSortKey = newSortKey
            self.reset()
     
    def reset(self, event=None):
        ''' reset does the actual sorting. If the order of the list changes, 
            observers are notified by means of the list-sorted event. '''
        oldSelf = self[:]
        self.sort(key=self.__createSortKey(), 
            reverse=not self.__settings.getboolean('view', 'sortascending'))
        if self != oldSelf:
            patterns.Publisher().notifyObservers(patterns.Event(self, 
                self.sortEventType()))
                        
    def rootTasks(self):
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
        if self.__settings.getboolean('view', 'sortbystatusfirst'):
            if self.__settings.getboolean('view', 'sortascending'):
                return lambda task: [task.completed(), task.inactive()]
            else:
                return lambda task: [not task.completed(), not task.inactive()]
        else:
            return lambda task: []

    def __createRegularSortKey(self):
        sortKeyName = self.__settings.get('view', 'sortby')
        if not self.__settings.getboolean('view', 'sortcasesensitive') \
            and sortKeyName == 'subject':
            prepareSortValue = lambda subject: subject.lower()
        else:
            prepareSortValue = lambda value: value
        kwargs = {}
        if sortKeyName.startswith('total') or self.__treeMode:
            kwargs['recursive'] = True
            sortKeyName = sortKeyName.replace('total', '')
        return lambda task: [prepareSortValue(getattr(task, 
            sortKeyName)(**kwargs))]
        
    def __registerObserverForTaskAttribute(self, eventType):
        # Sorter is always observing completion date and start date because
        # sorting by status depends on those two attributes, hence we don't
        # need to subscribe to these two attributes when they become the sort
        # key.
        if eventType not in ('task.completionDate', 'task.startDate'):
            patterns.Publisher().registerObserver(self.reset, 
                                                  eventType=eventType)
            
    def __removeObserverForTaskAttribute(self, eventType):
         # See comment at __registerObserverForTaskAttribute.
        if eventType not in ('task.completionDate', 'task.startDate'):
            patterns.Publisher().removeObserver(self.reset, eventType=eventType)
         