import patterns

class EffortSorter(patterns.ObservableListObserver):        
    def postProcessChanges(self):
        self.sort()