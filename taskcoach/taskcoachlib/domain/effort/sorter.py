import patterns


class EffortSorter(patterns.ListDecorator):
    def __init__(self, *args, **kwargs):
        super(EffortSorter, self).__init__(*args, **kwargs)
        patterns.Publisher().registerObserver(self.reset, 
            eventType='effort.start')
        patterns.Publisher().registerObserver(self.reset,
            eventType='effort.task')
    
    def sortEventType(self):
        return '%s.sorted'%self.__class__
    
    def extendSelf(self, efforts):
        super(EffortSorter, self).extendSelf(efforts)
        self.reset()

    # We don't override removeItemsFromSelf because there is no need to 
    # call self.reset() when items are removed since after removing efforts
    # the remaining efforts are still in the right order.

    def reset(self, event=None):
        oldSelf = self[:]
        self.sort(key=lambda effort: (effort.getStart(), effort.task().subject()),
                  reverse=True)
        if self != oldSelf:
            patterns.Publisher().notifyObservers(patterns.Event(self, 
                self.sortEventType()))


