import patterns

class Sorter(patterns.ObservableListObserver):
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
        

class DepthFirstSorter(Sorter):
    def notifyAdd(self, items, *args, **kwargs):
        self.sort()
        self._notifyObserversOfNewItems(items)
        
    def notifyRemove(self, items, *args, **kwargs):
        self.sort()
        self._notifyObserversOfRemovedItems(items)
        
    def sort(self):
        self[:] = self.sortDepthFirst(self.original().rootTasks())
        
    def sortDepthFirst(self, tasks):
        result = []
        tasks.sort()
        for task in tasks:
            if task not in self.original():
                continue
            result.append(task)
            children = task.children()[:]
            result.extend(self.sortDepthFirst(children))
        return result
