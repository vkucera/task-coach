class List(list):    
    def removeItems(self, items):
        ''' List.removeItems is the opposite of list.extend. Useful for 
            ObservableList to be able to generate just one notification 
            when removing multiple items. '''
        for item in items:
            # Prevent overridden remove method from being invoked
            list.remove(self, item) 
            

class Observable(object):
    ''' Observable objects can be observed by registering (subscribing) a 
        callback method with Observable.registerObserver. The callback is 
        called when the object changes. Subclasses should call 
        Observer._notifyObserversOfChange to notify observers. Observers can
        remove themselves (unsubscribe) by calling Observable.removeObserver. '''
        
    def __init__(self, *args, **kwargs):
        super(Observable, self).__init__(*args, **kwargs)
        self._changeCallbacks = []
        self.startNotifying()
        
    def stopNotifying(self):
        self._notifying = False
        
    def startNotifying(self):
        self._notifying = True

    def registerObserver(self, callback):
        ''' Register an observer. The callback should be a callable and 
            accept one argument (the observable), see Observable._changed. '''
        self._changeCallbacks.append(callback)
        
    def removeObserver(self, callback):
        ''' Remove a callback that was registered earlier. '''
        self._changeCallbacks.remove(callback)

    def _notifyObserversOfChange(self, changedObject=None):
        if not self._notifying:
            return
        changedObject = changedObject or self
        for callback in self._changeCallbacks:
            callback(changedObject)


class ObservablesList(List):
    ''' ObservablesList is a list of observables, i.e. all items that are 
        put in the list should obey the Observable interface as defined by 
        the Observable class. ObservablesList registers itself as observer 
        of all items that are put into the list. Subclasses of ObservablesList 
        should override ObservablesList.notifyChange if they want to react to
        changes of items in the list. '''
    
    def __init__(self, initList=None, *args, **kwargs):
        super(ObservablesList, self).__init__(initList or [], *args, **kwargs)
        self.__subscribe(*(initList or []))
        
    def notifyChange(self, *args, **kwargs):
        ''' This method is called by items in the list when they change. 
            Override to react to those changes. '''
        pass
    
    def __subscribe(self, *observables):
        ''' Private method to subscribe to one or more observables. '''
        for observable in observables:
            observable.registerObserver(self.notifyChange)
            
    def __unsubscribe(self, *observables):
        ''' Private method to unsubcribe to one or more observables. '''
        for observable in observables:
            observable.removeObserver(self.notifyChange)
        
    def append(self, observable):
        super(ObservablesList, self).append(observable)
        self.__subscribe(observable)

    def extend(self, observables):
        super(ObservablesList, self).extend(observables)
        self.__subscribe(*observables)
    
    def insert(self, index, observable):
        super(ObservablesList, self).insert(index, observable)
        self.__subscribe(observable)
        
    def __delitem__(self, index):
        self.__unsubscribe(self[index])
        super(ObservablesList, self).__delitem__(index)
    
    def __delslice__(self, *slice):
        self.__unsubscribe(*self.__getslice__(*slice))
        super(ObservablesList, self).__delslice__(*slice)    

    def remove(self, observable):
        self.__unsubscribe(observable)
        super(ObservablesList, self).remove(observable)
    
    def removeItems(self, observables):
        self.__unsubscribe(*observables)
        super(ObservablesList, self).removeItems(observables)
        
        
class ObservableList(Observable, List):
    ''' ObservableList is a list that is observable and notifies observers 
        when items are added to or removed from the list. '''
        
    # FIXME: How about __setitem__ and __setslice__?
        
    def __init__(self, *args, **kwargs):
        super(ObservableList, self).__init__(*args, **kwargs)
        self._addCallbacks = []
        self._removeCallbacks = []
        
    def registerObserver(self, notifyAdd, notifyRemove, notifyChange=None):
        if notifyChange:
            super(ObservableList, self).registerObserver(notifyChange)
        self._addCallbacks.append(notifyAdd)
        self._removeCallbacks.append(notifyRemove)
        
    def removeObserver(self, notifyAdd, notifyRemove, notifyChange=None):
        if notifyChange:
            super(ObservableList, self).removeObserver(notifyChange)
        self._addCallbacks.remove(notifyAdd)
        self._removeCallbacks.remove(notifyRemove)
    
    def _callback(self, callbackList, items):
        if not self._notifying or not items:
            return
        for callback in callbackList:
            callback(items)
            
    def _notifyObserversOfNewItems(self, items):
        self._callback(self._addCallbacks, items)
            
    def _notifyObserversOfRemovedItems(self, items):
        self._callback(self._removeCallbacks, items)
            
    def append(self, item):
        super(ObservableList, self).append(item)
        self._notifyObserversOfNewItems([item])

    def extend(self, items):
        if items:
            super(ObservableList, self).extend(items)
            self._notifyObserversOfNewItems(items)

    def insert(self, index, item):
        super(ObservableList, self).insert(index, item)
        self._notifyObserversOfNewItems([item])

    def remove(self, item):
        super(ObservableList, self).remove(item)
        self._notifyObserversOfRemovedItems([item])
    
    def removeItems(self, items):
        if items:
            super(ObservableList, self).removeItems(items)
            self._notifyObserversOfRemovedItems(items)
            
    def __delitem__(self, index):
        item = self[index]
        super(ObservableList, self).__delitem__(index)
        self._notifyObserversOfRemovedItems([item])
        
    def __delslice__(self, *slice):
        items = self.__getslice__(*slice)
        if items:
            super(ObservableList, self).__delslice__(*slice)
            self._notifyObserversOfRemovedItems(items)


class ObservableObservablesList(ObservableList, ObservablesList):
    ''' A list of observables that is observable. '''
    
    def notifyChange(self, item):
        self._notifyObserversOfChange([item])


class ObservableListObserver(ObservableList):
    ''' ObservableListObserver observes an ObservableObservablesList. '''
    
    def __init__(self, observedList, *args, **kwargs):
        super(ObservableListObserver, self).__init__(*args, **kwargs)
        self._observedList = observedList
        self._observedList.registerObserver(self.notifyAdd, self.notifyRemove, 
            self.notifyChange)
        self.notifyAdd(self._observedList)

    def notifyChange(self, items):
        ''' This method should be overriden to provide some useful
            behavior, like filtering the original list. '''
        if items:
            self._notifyObserversOfChange(items)
        
    def notifyAdd(self, items):
        ''' This method should be overriden to provide some useful
            behavior, like filtering the original list. '''
        if items:
            self._notifyObserversOfNewItems(items)
        
    def notifyRemove(self, items):
        ''' This method should be overriden to provide some useful
            behavior, like filtering the original list. '''        
        if items:
            self._notifyObserversOfRemovedItems(items)

    def original(self):
        return self._observedList

    # delegate changes to the original list

    def append(self, item):
        self._observedList.append(item)
            
    def extend(self, items):
        self._observedList.extend(items)
        
    def remove(self, item):
        self._observedList.remove(item)
    
    def removeItems(self, items):
        self._observedList.removeItems(items)
        
    def __delitem__(self, index):
        del self._observedList[index]

    def __delslice__(self, *slice):
        self._observedList.__delslice__(*slice)

    def insert(self, index, item):
        self._observedList.insert(index, item)

    def __getattr__(self, attribute):
        return getattr(self._observedList, attribute)
    
    # provide two methods to manipulate the ObservableListObserver itself

    def _extend(self, items):
        super(ObservableListObserver, self).extend(items)
    
    def _removeItems(self, items):
        super(ObservableListObserver, self).removeItems(items)
        
