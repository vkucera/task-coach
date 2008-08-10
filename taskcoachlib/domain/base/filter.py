'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>

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

    def rootItems(self):
        return [item for item in self if item.parent() is None]
        

class SearchFilter(Filter):
    def __init__(self, *args, **kwargs):
        searchString = kwargs.pop('searchString', u'')
        matchCase = kwargs.pop('matchCase', False)
        includeSubItems = kwargs.pop('includeSubItems', False)

        self.setSearchFilter(searchString, matchCase, includeSubItems, False)

        super(SearchFilter, self).__init__(*args, **kwargs)

    def setSearchFilter(self, searchString, matchCase=False, 
                        includeSubItems=False, doReset=True):
        self.__includeSubItems = includeSubItems

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
                self.__searchPredicate(self.__itemSubject(item))]
        
    def __itemSubject(self, item):
        subject = item.subject()
        if self.__includeSubItems:
            parent = item.parent()
            while parent:
                subject += parent.subject()
                parent = parent.parent()
        if self.treeMode():
            subject += ' '.join([child.subject() for child in \
                item.children(recursive=True) if child in self.observable()])
        return subject
