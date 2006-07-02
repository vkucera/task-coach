class List(list):    
    def removeItems(self, items):
        ''' List.removeItems is the opposite of list.extend. Useful for 
            ObservableList to be able to generate just one notification 
            when removing multiple items. '''
        for item in items:
            # No super() to prevent overridden remove method from being invoked
            list.remove(self, item) 


class Event(object):
    ''' Event represents notification events. '''
    def __init__(self, source, type, *values):
        self.__source = source
        self.__type = type
        self.__values = values

    def __repr__(self):
        return 'Event(%s, %s, %s)'%(self.__source, self.__type, self.__values)

    def source(self):
        return self.__source

    def type(self):
        return self.__type

    def value(self):
        return self.__values[0]

    def values(self):
        return self.__values

    
class Observable(object):
    ''' Observable objects can be observed by registering (subscribing) a 
        callback method with Observable.registerObserver. The callback is 
        called when the object changes. Subclasses should call 
        Observer.notifyObservers to notify observers. Observers can
        remove themselves (unsubscribe) by calling 
        Observable.removeObserver(s). '''
        
    def __init__(self, *args, **kwargs):
        self.__callbacks = {}
        super(Observable, self).__init__(*args, **kwargs)
        self.__notifyingSemaphore = 0
        
    def stopNotifying(self):
        self.__notifyingSemaphore += 1
        
    def startNotifying(self):
        self.__notifyingSemaphore -= 1

    def isNotifying(self):
        return self.__notifyingSemaphore == 0
        
    def registerObserver(self, callback, *eventTypes):
        ''' Register an observer. The callback should be a callable and 
            accept one argument (an Event), see Observable.notifyObservers. 
            Observers should tell the observable they are interested 
            in a certain type of event (at least one). Event types are
            typically strings, but can be anything as long as its
            hashable. '''
        for eventType in eventTypes:
            self.__callbacks.setdefault(eventType, []).append(callback)
        
    def removeObserver(self, callbackToRemove, *eventTypes):
        ''' Remove a callback that was registered earlier. Use this
            method (as opposed to Observable.removeObservers to remove
            observers for specific event types. '''
        eventTypes = eventTypes or self.__callbacks.keys()
        for eventType in eventTypes:
            if callbackToRemove in self.__callbacks[eventType]:
                self.__callbacks[eventType].remove(callbackToRemove)

    def removeObservers(self, *callbacksRoRemove):
        ''' Remove callbacks that were registered earlier. The callbacks
            are removed for all event types. If you want to remove 
            callbacks for a specific event type only, use 
            Observable.removeObserver. '''
        for callback in callbacksRoRemove:
            self.removeObserver(callback)

    def notifyObservers(self, *events):
        if not self.isNotifying():
            return
        for event in events:
            for callback in self.observers(event.type()):
                callback(event)

    def observers(self, eventType):
        return self.__callbacks.get(eventType, [])


class Observer(object):
    def __init__(self, observable, *args, **kwargs):
        super(Observer, self).__init__(*args, **kwargs)
        self.__observable = observable

    def observable(self):
        return self.__observable 


class ObservableList(Observable, List):
    ''' ObservableList is a list that is observable and notifies observers 
        when items are added to or removed from the list. '''
        
    # FIXME: How about __setitem__ and __setslice__?
    
    def append(self, item):
        super(ObservableList, self).append(item)
        self.notifyObservers(Event(self, 'list.add', item))

    def extend(self, items):
        if items:
            super(ObservableList, self).extend(items)
            self.notifyObservers(Event(self, 'list.add', *items))

    def insert(self, index, item):
        super(ObservableList, self).insert(index, item)
        self.notifyObservers(Event(self, 'list.add', item))

    def remove(self, item):
        super(ObservableList, self).remove(item)
        self.notifyObservers(Event(self, 'list.remove', item))
    
    def removeItems(self, items):
        if items:
            super(ObservableList, self).removeItems(items)
            self.notifyObservers(Event(self, 'list.remove', *items))
            
    def __delitem__(self, index):
        item = self[index]
        super(ObservableList, self).__delitem__(index)
        self.notifyObservers(Event(self, 'list.remove', item))
        
    def __delslice__(self, *slice):
        items = self.__getslice__(*slice)
        if items:
            super(ObservableList, self).__delslice__(*slice)
            self.notifyObservers(Event(self, 'list.remove', *items))


class ListDecorator(Observer, ObservableList):
    ''' ListDecorator observes an ObservableList and is an
        ObservableList itself. Its purpose is to decorate another list
        and add some behaviour, such as sorting or filtering. Users of
        this class shouldn't see a difference between using the original
        list or a decorated version. '''
    
    def __init__(self, observedList, *args, **kwargs):
        super(ListDecorator, self).__init__(observedList, *args, **kwargs)
        self.observable().registerObserver(self.onAddItem, 'list.add')
        self.observable().registerObserver(self.onRemoveItem, 'list.remove')
        self.extendSelf(self.observable())

    def onAddItem(self, event):
        ''' The default behaviour is to simply add the items that are
            added to the original list to this list too. Extend to add
            behaviour. '''
        self.extendSelf(event.values())

    def onRemoveItem(self, event):
        ''' The default behaviour is to simply remove the items that are
            removed from the original list from this list too. Extend to add
            behaviour. '''
        self.removeItemsFromSelf(event.values())

    def extendSelf(self, items):
        ''' Provide a method to extend this list without delegating to
            the observed list. '''
        super(ListDecorator, self).extend(items)
        
    def removeItemsFromSelf(self, items):
        ''' Provide a method to remove items from this list without 
            delegating to the observed list. '''
        super(ListDecorator, self).removeItems(items)

    # delegate changes to the original list

    def append(self, item):
        self.observable().append(item)
            
    def extend(self, items):
        self.observable().extend(items)
        
    def remove(self, item):
        self.observable().remove(item)
    
    def removeItems(self, items):
        self.observable().removeItems(items)
        
    def __delitem__(self, index):
        del self.observable()[index]

    def __delslice__(self, *slice):
        self.observable().__delslice__(*slice)

    def insert(self, index, item):
        self.observable().insert(index, item)

    def __getattr__(self, attribute):
        return getattr(self.observable(), attribute)
    
