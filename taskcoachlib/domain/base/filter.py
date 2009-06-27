'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2009 Frank Niessink <frank@niessink.com>
Copyright (C) 2008 Jerome Laheurte <fraca7@free.fr>

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

import re, sre_constants
from taskcoachlib import patterns
from taskcoachlib.domain.base import object


class Filter(patterns.SetDecorator):
    def __init__(self, *args, **kwargs):
        self.__treeMode = kwargs.pop('treeMode', False)        
        super(Filter, self).__init__(*args, **kwargs)
        
    def setTreeMode(self, treeMode):
        self.__treeMode = treeMode
        try:
            self.observable().setTreeMode(treeMode)
        except AttributeError:
            pass
        self.reset()
        
    def treeMode(self):
        return self.__treeMode

    def extendSelf(self, items):
        super(Filter, self).extendSelf(self.filter(items))

    def removeItemsFromSelf(self, items):
        itemsToRemove = set(items)
        if self.treeMode():
            for item in itemsToRemove.copy():
                itemsToRemove.update(item.children(recursive=True))
        itemsToRemove = [item for item in itemsToRemove if item in self]
        super(Filter, self).removeItemsFromSelf(itemsToRemove)
        
    def reset(self):
        filteredItems = self.filter(self.observable())
        itemsToAdd = [item for item in filteredItems if item not in self]
        itemsToRemove = [item for item in self if item not in filteredItems]
        self.removeItemsFromSelf(itemsToRemove)
        self.extendSelf(itemsToAdd)
            
    def filter(self, items):
        ''' filter returns the items that pass the filter. '''
        raise NotImplementedError # pragma: no cover

    def rootItems(self):
        return [item for item in self if item.parent() is None]


class SelectedItemsFilter(Filter):
    def __init__(self, *args, **kwargs):
        self.__selectedItems = set(kwargs.pop('selectedItems' , []))
        self.__includeSubItems = kwargs.pop('includeSubItems', True)
        super(SelectedItemsFilter, self).__init__(*args, **kwargs)

    def removeItemsFromSelf(self, items):
        super(SelectedItemsFilter, self).removeItemsFromSelf(items)
        self.__selectedItems.difference_update(set(items))
        if not self.__selectedItems:
            self.extendSelf(self.observable())
               
    def filter(self, items):
        if self.__selectedItems:
            result = [item for item in items if self.itemOrAncestorInSelectedItems(item)]
            if self.__includeSubItems:
                for item in result[:]:
                    result.extend(item.children(recursive=True))
            return result
        else:
            return items
     
    def itemOrAncestorInSelectedItems(self, item):
        if item in self.__selectedItems:
            return True
        elif item.parent():
            return self.itemOrAncestorInSelectedItems(item.parent())
        else:
            return False
    

class SearchFilter(Filter):
    def __init__(self, *args, **kwargs):
        searchString = kwargs.pop('searchString', u'')
        matchCase = kwargs.pop('matchCase', False)
        includeSubItems = kwargs.pop('includeSubItems', False)
        searchDescription = kwargs.pop('searchDescription', False)

        self.setSearchFilter(searchString, matchCase=matchCase, 
                             includeSubItems=includeSubItems, 
                             searchDescription=searchDescription, doReset=False)

        super(SearchFilter, self).__init__(*args, **kwargs)

    def setSearchFilter(self, searchString, matchCase=False, 
                        includeSubItems=False, searchDescription=False, 
                        doReset=True):
        self.__includeSubItems = includeSubItems
        self.__searchDescription = searchDescription

        try:
            if matchCase:
                rx = re.compile(searchString)
            else:
                rx = re.compile(searchString, re.IGNORECASE)
        except sre_constants.error:
            if matchCase:
                self.__searchPredicate = lambda x: x.find(searchString) != -1
            else:
                self.__searchPredicate = lambda x: x.lower().find(searchString.lower()) != -1
        else:
            self.__searchPredicate = lambda x: bool(rx.search(x))

        if doReset:
            self.reset()

    def filter(self, items):
        return [item for item in items if \
                self.__searchPredicate(self.__itemText(item))]
        
    def __itemText(self, item):
        text = self.__itemOwnText(item)
        if self.__includeSubItems:
            parent = item.parent()
            while parent:
                text += self.__itemOwnText(parent)
                parent = parent.parent()
        if self.treeMode():
            text += ' '.join([self.__itemOwnText(child) for child in \
                item.children(recursive=True) if child in self.observable()])
        return text

    def __itemOwnText(self, item):
        text = item.subject()
        if self.__searchDescription:
            text += item.description()
        return text 


class DeletedFilter(Filter):
    def __init__(self, *args, **kwargs):
        super(DeletedFilter, self).__init__(*args, **kwargs)

        for eventType in [object.Object.markDeletedEventType(),
                          object.Object.markNotDeletedEventType()]:
            patterns.Publisher().registerObserver(self.onObjectMarkedDeletedOrNot,
                          eventType=eventType)

    def onObjectMarkedDeletedOrNot(self, event):
        obj = event.source()

        if obj.isDeleted():
            self.removeItemsFromSelf([obj])
        else:
            if obj in self.observable() and not obj in self:
                self.extendSelf([obj])

    def filter(self, items):
        return [item for item in items if not item.isDeleted()]
