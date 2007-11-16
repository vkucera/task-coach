from domain import base
import note


class NoteSorter(base.TreeSorter):
    DomainObjectClass = note.Note
                        
    def createSortKeyFunction(self):
        sortKeyName = self._sortKey
        if not self._sortCaseSensitive and sortKeyName in ('subject', 'description'):
            prepareSortValue = str.lower
        else:
            prepareSortValue = lambda value: value
        return lambda note: prepareSortValue(getattr(note, sortKeyName)())

    


