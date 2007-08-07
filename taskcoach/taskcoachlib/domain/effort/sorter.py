from domain import base
import patterns


class EffortSorter(base.Sorter):
    EventTypePrefix = 'effort'
    def __init__(self, *args, **kwargs):
        kwargs['sortAscending'] = False
        super(EffortSorter, self).__init__(*args, **kwargs)
        patterns.Publisher().registerObserver(self.reset, 
            eventType='effort.start')
        patterns.Publisher().registerObserver(self.reset,
            eventType='effort.task')
    
    def createSortKeyFunction(self):
        # Sort by start of effort first, then by task subject
        return lambda effort: (effort.getStart(), effort.task().subject())
