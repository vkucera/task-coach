import patterns


class EffortSorter(patterns.ObservableListObserver):        
    def postProcessChanges(self, notification):
        oldSelf = self[:]
        self.sort()
        if self != oldSelf:
            notification['orderChanged'] = True
        return notification