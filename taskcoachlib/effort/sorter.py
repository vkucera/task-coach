import patterns

class EffortSorter(patterns.ObservableListObserver):
    def onNotify(self, notification, *args, **kwargs):
        self.stopNotifying()
        self._extend(notification.effortsAdded)
        self._removeItems(notification.effortsRemoved)
        self.sort()
        self.startNotifying()
        myNotification = patterns.observer.Notification(self, notification)
        self.notifyObservers(myNotification)
