from domain import base
import note


class NoteSorter(base.TreeSorter):
    DomainObjectClass = note.Note
    EventTypePrefix = 'note'
                        
    def createSortKeyFunction(self):
        sortKeyName = self._sortKey
        if not self._sortCaseSensitive and sortKeyName in ('subject', 'description'):
            prepareSortValue = str.lower
        elif sortKeyName in ('categories', 'totalCategories'):
            prepareSortValue = lambda categories: sorted([category.subject() for category in categories])
        else:
            prepareSortValue = lambda value: value
        kwargs = {}
        if sortKeyName.startswith('total'):
            kwargs['recursive'] = True
            sortKeyName = sortKeyName.replace('total', '')
            sortKeyName = sortKeyName[0].lower() + sortKeyName[1:]
        return lambda note: [prepareSortValue(getattr(note, 
            sortKeyName)(**kwargs))]
    


