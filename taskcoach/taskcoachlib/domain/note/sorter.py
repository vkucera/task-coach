from domain import base


class NoteSorter(base.Sorter):
    EventTypePrefix = 'note'
                        
    def createSortKeyFunction(self):
        sortKeyName = self._sortKey
        if not self._sortCaseSensitive and sortKeyName in ('subject', 'description'):
            prepareSortValue = str.lower
        else:
            prepareSortValue = lambda value: value
        return lambda note: prepareSortValue(getattr(note, sortKeyName)())

    


