import patterns, effortlist

class EffortSorter(patterns.ObservableListObserver, effortlist.EffortListMixin):
    def onNotify(self, notification, *args, **kwargs):
        self._addAndRemoveEfforts(notification.itemsAdded, 
            notification.itemsRemoved, notification.itemsChanged, self.sort)
        