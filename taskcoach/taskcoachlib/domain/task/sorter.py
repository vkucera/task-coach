'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2010 Task Coach developers <developers@taskcoach.org>

Task Coach is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Task Coach is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from taskcoachlib import patterns
from taskcoachlib.domain import base, date
import task


class Sorter(base.TreeSorter):
    DomainObjectClass = task.Task # What are we sorting
    EventTypePrefix = 'task'
    TaskStatusAttributes = ('startDateTime', 'completionDateTime',
                            'prerequisite')
    def __init__(self, *args, **kwargs):
        self.__rootItems = None
        self.__treeMode = kwargs.pop('treeMode', False)
        self.__sortByTaskStatusFirst = kwargs.pop('sortByTaskStatusFirst', True)
        super(Sorter, self).__init__(*args, **kwargs)
        for attribute in self.TaskStatusAttributes:
            if attribute == 'prerequisite':
                eventTypes = ['.'.join([self.EventTypePrefix, attribute, delta]) 
                              for delta in ['add', 'remove']]
            else:
                eventTypes = ['.'.join([self.EventTypePrefix, attribute])]
            for eventType in eventTypes:
                patterns.Publisher().registerObserver(self.onAttributeChanged, 
                                                      eventType=eventType)
    
    @patterns.eventSource       
    def setTreeMode(self, treeMode=True, event=None):
        self.__treeMode = treeMode
        try:
            self.observable().setTreeMode(treeMode)
        except AttributeError:
            pass
        self.reset(event=event)
        event.addSource(self, type=self.sortEventType()) # force notification 

    def treeMode(self):
        return self.__treeMode
        
    def reset(self, *args, **kwargs): # pylint: disable-msg=W0221
        self._invalidateRootItemCache()
        return super(Sorter, self).reset(*args, **kwargs)
        
    def extendSelf(self, items, event=None):
        self._invalidateRootItemCache()
        return super(Sorter, self).extendSelf(items, event=event)

    def removeItemsFromSelf(self, itemsToRemove, event=None):
        self._invalidateRootItemCache()
        itemsToRemove = set(itemsToRemove)
        if self.treeMode():
            for item in itemsToRemove.copy():
                itemsToRemove.update(item.children(recursive=True)) 
        itemsToRemove = [item for item in itemsToRemove if item in self]
        return super(Sorter, self).removeItemsFromSelf(itemsToRemove, event=event)

    def rootItems(self):
        if self.__rootItems is None:
            self.__rootItems = super(Sorter, self).rootItems()
        return self.__rootItems

    def _invalidateRootItemCache(self):
        self.__rootItems = None
        
    def sortByTaskStatusFirst(self, sortByTaskStatusFirst):
        self.__sortByTaskStatusFirst = sortByTaskStatusFirst
        # We don't need to invoke self.reset() here since when this property is
        # changed, the sort order also changes which in turn will cause 
        # self.reset() to be called.
                                
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
            prepareSortValue = lambda categories: sorted([category.subject(recursive=True) for category in categories])
        elif sortKeyName == 'prerequisites':
            prepareSortValue = lambda prerequisites: sorted([prerequisite.subject(recursive=True) for prerequisite in prerequisites])
        elif sortKeyName == 'dependencies':
            prepareSortValue = lambda dependencies: sorted([dependency.subject(recursive=True) for dependency in dependencies])    
        elif sortKeyName == 'reminder':
            prepareSortValue = lambda reminder: reminder or date.DateTime.max
        else:
            prepareSortValue = lambda value: value
        kwargs = {}
        if self.__treeMode and sortKeyName != 'priority': # FIXME: what's special about priority?
            kwargs['recursive'] = True
        # pylint: disable-msg=W0142
        return lambda task: [prepareSortValue(getattr(task,  
            sortKeyName)(**kwargs))]
    
    def _registerObserverForAttribute(self, attribute):
        # Sorter is always observing completion date, start date and 
        # prerequisites because sorting by status depends on those attributes. 
        # Hence we don't need to subscribe to these attributes when they become 
        # the sort key.
        if attribute in self.TaskStatusAttributes:
            return
        if attribute == 'dependencies':
            for delta in 'add', 'remove':
                super(Sorter, self)._registerObserverForAttribute('dependency.' + delta)
        else:
            super(Sorter, self)._registerObserverForAttribute(attribute)
            
    def _removeObserverForAttribute(self, attribute):
         # See comment at _registerObserverForAttribute.
        if attribute in self.TaskStatusAttributes:
            return
        if attribute == 'dependencies':
            for delta in 'add', 'remove':
                super(Sorter, self)._removeObserverForAttribute('dependency.' + delta)
        else:
            super(Sorter, self)._removeObserverForAttribute(attribute)
        