import patterns

class SortOrderReverser(object):
    ''' This class is responsible for reversing the sort order from ascending
        to descending or vice versa when the sort key setting is set to the 
        same sort key twice in a row. In other words, this class will flip the 
        sort order when a user clicks on the same column in a list view twice
        in a row. '''
    
    __metaclass__ = patterns.Singleton
    
    def __init__(self, *args, **kwargs):
        self.init(kwargs.pop('settings'))
        super(SortOrderReverser, self).__init__(*args, **kwargs)    
    
    def init(self, settings):
        try:
            self.__settings.removeObserver(self.onSortKeyChanged)
        except AttributeError:
            pass
        self.__settings = settings
        self.__settings.registerObserver(self.onSortKeyChanged, ('view', 'sortby'))
        self.__previousSortKey = self.__settings.get('view', 'sortby')
        
    def onSortKeyChanged(self, notification):
        if notification.value == self.__previousSortKey:
            newSortOrder = not self.__settings.getboolean('view', 'sortascending')
            self.__settings.set('view', 'sortascending', str(newSortOrder))
        else:        
            self.__previousSortKey = notification.value


class Sorter(patterns.ObservableListObserver):
    def __init__(self, *args, **kwargs):
        self.__settings = kwargs.pop('settings')
        self.__treeMode = kwargs.pop('treeMode', False)
        self.__settings.registerObserver(self.onSortKeyChanged, ('view', 'sortby'))
        self.__settings.registerObserver(self.onSortSettingChanged, ('view', 'sortascending'), 
            ('view', 'sortbystatusfirst'), ('view', 'sortcasesensitive'))
        self.__previousSortKey = self.__settings.get('view', 'sortby')
        SortOrderReverser(settings=self.__settings)
        super(Sorter, self).__init__(*args, **kwargs)
                
    def onSortKeyChanged(self, notification):
        if notification.value == self.__previousSortKey:
            # We don't call self.reset() because the sort order will be changed
            # by the SortOrderReverser, which will trigger another notification
            pass
        else:        
            self.__previousSortKey = notification.value
            self.reset()
     
    def onSortSettingChanged(self, *args, **kwargs):
        self.reset()
        
    def postProcessChanges(self, notification):
        ''' postProcessChanges does the actual sorting. If the order of the list 
            changes, an 'orderChanged' flag is added to the notification to reflect this. '''
        oldSelf = self[:]
        self.sort(key=self.__createSortKey(), reverse=not self.__settings.getboolean('view', 'sortascending'))
        if self != oldSelf:
            notification['orderChanged'] = True
        return notification
                        
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
        if not self.__settings.getboolean('view', 'sortcasesensitive') and sortKeyName == 'subject':
            prepareSortValue = lambda subject: subject.lower()
        else:
            prepareSortValue = lambda value: value
        kwargs = {}
        if sortKeyName.startswith('total') or self.__treeMode:
            kwargs['recursive'] = True
            sortKeyName = sortKeyName.replace('total', '')
        return lambda task: [prepareSortValue(getattr(task, sortKeyName)(**kwargs))]
        
 