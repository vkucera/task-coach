import patterns


class EffortSorter(patterns.ListDecorator):        
    def extendSelf(self, efforts):
        super(EffortSorter, self).extendSelf(efforts)
        for effort in efforts:
            effort.registerObserver(self.reset,
                'effort.start', 'effort.task')
        self.reset()

    def removeItemsFromSelf(self, efforts):
        super(EffortSorter, self).removeItemsFromSelf(efforts)
        for effort in efforts:
            effort.removeObserver(self.reset)
        # No need to call self.reset() because after removing efforts
        # the remaining efforts are still in the right order.

    def reset(self, event=None):
        oldSelf = self[:]
        self.sort()
        if self != oldSelf:
            self.notifyObservers(patterns.Event(self, 'list.sorted'))


