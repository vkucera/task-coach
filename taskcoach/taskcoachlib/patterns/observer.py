import patterns


class List(list):
    def __eq__(self, other):
        ''' Subclasses of List are always considered to be unequal, even when
            their contents are the same. This is because List subclasses are
            used as Collections of domain objects. When compared to other types,
            the contents are compared. '''
        if isinstance(other, List):
            return self is other
        else:
            return list(self) == other
    
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

    def __eq__(self, other):
        return self.source() == other.source() and \
               self.type() == other.type() and \
               self.values() == other.values()

    def source(self):
        return self.__source

    def type(self):
        return self.__type

    def value(self):
        return self.__values[0]

    def values(self):
        return self.__values

        
class Publisher(object):
    ''' Publisher is used to register for event notifications. It supports
        the publisher/subscribe pattern, also known as the observer pattern.
        Objects (Observers) interested in change notifications register a 
        callback method via Publisher.registerObserver. The callback should
        expect one argument; an instance of the Event class. Observers can 
        register their interest in specific event types (topics) when 
        registering. 
        
        Implementation note: 
        - Publisher is a Singleton class since all observables and all
        observers have to use exactly one registry to be sure that all
        observables can reach all observers. '''
        
    __metaclass__ = patterns.Singleton
    
    def __init__(self, *args, **kwargs):
        super(Publisher, self).__init__(*args, **kwargs)
        self.clear()
        
    def clear(self):
        ''' Clear the registry of observers. Mainly for testing purposes. '''
        self.__observers = {} # {eventType: [list of callbacks]}
        self.__notifyingSemaphore = 0
    
    def registerObserver(self, observer, eventType):
        ''' Register an observer for an event type. The observer is a callback 
            method that should expect one argument, an instance of Event.
            The eventType can be anything hashable, typically a string. '''
        observerList = self.__observers.setdefault(eventType, [])
        if observer not in observerList:
            observerList.append(observer)
        
    def removeObserver(self, observer, eventType=None):
        ''' Remove an observer. If no event type is specified, the observer
            is removed for all event types. If an event type is specified
            the observer is removed for that event type only. '''
        if eventType:
            observerListsToScan = [self.__observers.get(eventType, [])]
        else:
            observerListsToScan = self.__observers.values()            
        for observerList in observerListsToScan:
            if observer in observerList:
                observerList.remove(observer)
        
    def notifyObservers(self, event):
        ''' Notify observers of the event. The event type is extracted from
            the event. '''
        if self.isNotifying():
            for observer in self.__observers.get(event.type(), []):
                observer(event)
                
    def observers(self, eventType=None):
        ''' Get the currently registered observers. Optionally specify
            a specific event type to get observers for that event type only. '''
        if eventType:
            return self.__observers.get(eventType, [])
        else:
            return [observer for observersForEventType in \
                    self.__observers.values() for observer in \
                    observersForEventType]
    
    def stopNotifying(self):
        ''' Temporarily stop notifying. Calls to stopNotifying and 
            startNotifying can be nested. As soon as startNotifying has been
            called the same number of times as stopNotifying, notifying is 
            resumed again. ''' 
        self.__notifyingSemaphore += 1

    def startNotifying(self):
        self.__notifyingSemaphore -= 1

    def isNotifying(self):
        return self.__notifyingSemaphore == 0
    

class Observer(object):
    def __init__(self, observable, *args, **kwargs):
        super(Observer, self).__init__(*args, **kwargs)
        self.__observable = observable

    def observable(self):
        return self.__observable 

    def __getattr__(self, attribute):
        return getattr(self.observable(), attribute)


class Observable(object):
    def __init__(self, *args, **kwargs):
        self.notifyObservers = patterns.Publisher().notifyObservers
        super(Observable, self).__init__(*args, **kwargs)


class ObservableCollection(Observable):
    def __hash__(self):
        ''' Make ObservableCollections suitable as keys in dictionaries. '''
        return hash(id(self))

    def addItemEventType(self):
        ''' The event type used to notify observers that one or more items
            have been added to the list. '''
        return '%s (%s).add'%(self.__class__, id(self))
    
    def removeItemEventType(self):
        ''' The event type used to notify observers that one or more items
            have been removed from the list. '''
        return '%s (%s).remove'%(self.__class__, id(self))

    def notifyObserversOfItemsAdded(self, *items):
        self.notifyObservers(Event(self, self.addItemEventType(), *items))

    def notifyObserversOfItemsRemoved(self, *items):
        self.notifyObservers(Event(self, self.removeItemEventType(), *items))


class ObservableSet(ObservableCollection, set):
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self is other
        else:
            return list(self) == other

    def append(self, item):
        self.add(item)
        self.notifyObserversOfItemsAdded(item)

    def extend(self, items):
        if items:
            self.update(items)
            self.notifyObserversOfItemsAdded(*items)
        
    def remove(self, item):
        super(ObservableSet, self).remove(item)
        self.notifyObserversOfItemsRemoved(item)
    
    def removeItems(self, items):
        if items:
            self.difference_update(items)
            self.notifyObserversOfItemsRemoved(*items)
    
    def clear(self):
        if self:
            items = tuple(self)
            super(ObservableSet, self).clear()
            self.notifyObserversOfItemsRemoved(*items)
    
class ObservableList(ObservableCollection, List):
    ''' ObservableList is a list that notifies observers 
        when items are added to or removed from the list. '''
        
    def append(self, item):
        super(ObservableList, self).append(item)
        self.notifyObserversOfItemsAdded(item)
        
    def extend(self, items):
        if items:
            super(ObservableList, self).extend(items)
            self.notifyObserversOfItemsAdded(*items)
            
    def remove(self, item):
        super(ObservableList, self).remove(item)
        self.notifyObserversOfItemsRemoved(item)
    
    def removeItems(self, items):
        if items:
            super(ObservableList, self).removeItems(items)
            self.notifyObserversOfItemsRemoved(*items)

    def clear(self):
        if self:
            items = tuple(self)
            del self[:]
            self.notifyObserversOfItemsRemoved(*items) 
               

class CollectionDecorator(Observer, ObservableCollection):
    ''' CollectionDecorator observes an ObservableCollection and is an
        ObservableCollection itself too. Its purpose is to decorate another 
        collection and add some behaviour, such as sorting or filtering. 
        Users of this class shouldn't see a difference between using the 
        original collection or a decorated version. '''

    def __init__(self, observedCollection, *args, **kwargs):
        super(CollectionDecorator, self).__init__(observedCollection, *args, **kwargs)
        patterns.Publisher().registerObserver(self.onAddItem, 
            eventType=self.observable().addItemEventType())
        patterns.Publisher().registerObserver(self.onRemoveItem, 
            eventType=self.observable().removeItemEventType())
        self.extendSelf(self.observable())

    def __repr__(self):
        return '%s(%s)'%(self.__class__, super(CollectionDecorator, self).__repr__())

    def onAddItem(self, event):
        ''' The default behaviour is to simply add the items that are
            added to the original collection to this collection too. 
            Extend to add behaviour. '''
        self.extendSelf(event.values())

    def onRemoveItem(self, event):
        ''' The default behaviour is to simply remove the items that are
            removed from the original collection from this collection too.
            Extend to add behaviour. '''
        self.removeItemsFromSelf(event.values())

    def extendSelf(self, items):
        ''' Provide a method to extend this collection without delegating to
            the observed collection. '''
        super(CollectionDecorator, self).extend(items)
        
    def removeItemsFromSelf(self, items):
        ''' Provide a method to remove items from this collection without 
            delegating to the observed collection. '''
        super(CollectionDecorator, self).removeItems(items)

    # Delegate changes to the observed collection

    def append(self, item):
        self.observable().append(item)
            
    def extend(self, items):
        self.observable().extend(items)
        
    def remove(self, item):
        self.observable().remove(item)
    
    def removeItems(self, items):
        self.observable().removeItems(items)
        

class ListDecorator(CollectionDecorator, ObservableList):
    pass


class SetDecorator(CollectionDecorator, ObservableSet):
    pass