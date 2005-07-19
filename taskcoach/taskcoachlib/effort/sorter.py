import patterns


class EffortSorter(patterns.ObservableListObserver):        
    def postProcessChanges(self, notification):
        self.sort()
        notification['orderChanged'] = True
        return notification