import patterns

class Sorter(patterns.ObservableListObserver):
    def onNotify(self, notification, *args, **kwargs):
        self.stopNotifying()
        self._extend(notification.itemsAdded)
        self._removeItems(notification.itemsRemoved)
        self.sort()
        self.startNotifying()
        myNotification = patterns.observer.Notification(self, notification)
        self.notifyObservers(myNotification)
    

class DepthFirstSorter(Sorter):        
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
