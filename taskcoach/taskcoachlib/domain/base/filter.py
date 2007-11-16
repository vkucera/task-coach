import patterns, re

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

    def rootItems(self):
        return [item for item in self if item.parent() is None]
        

class SearchFilter(Filter):
    def __init__(self, *args, **kwargs):
        self.__searchString = kwargs.pop('searchString', u'')
        self.__matchCase = kwargs.pop('matchCase', False)
        self.__includeSubItems = kwargs.pop('includeSubItems', False)
        super(SearchFilter, self).__init__(*args, **kwargs)

    def setSearchFilter(self, searchString, matchCase=False, 
                        includeSubItems=False):
        self.__searchString = searchString
        self.__includeSubItems = includeSubItems
        if matchCase:
            self.__matchCase = 0
        else:
            self.__matchCase = re.IGNORECASE
        self.reset()
        
    def filter(self, items):
        regularExpression = re.compile(self.__searchString, self.__matchCase)
        return [item for item in items if \
                regularExpression.search(self.__itemSubject(item))]
        
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
