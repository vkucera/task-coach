import patterns

# FIXME: exactly the same as task.Sorter
class EffortSorter(patterns.ObservableListObserver):        
    def postProcessChanges(self):
        self.sort()