import patterns

class EffortSorter(patterns.ObservableListObserver):
    def notifyChange(self, items, *args, **kwargs):
        self.sort()
        self._notifyObserversOfChange(items)
    
    def notifyAdd(self, items, *args, **kwargs):
        self.stopNotifying()
        self._extend(items)
        self.sort()
        self.startNotifying()
        self._notifyObserversOfNewItems(items)
    
    def notifyRemove(self, items, *args, **kwargs):
        self.stopNotifying()
        self._removeItems(items)
        self.sort()
        self.startNotifying()
        self._notifyObserversOfRemovedItems(items)
