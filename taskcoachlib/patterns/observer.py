'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2009 Frank Niessink <frank@niessink.com>

Task Coach is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Task Coach is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import singleton


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


class Set(set):
    ''' The builtin set type does not like keyword arguments, so to keep
        it happy we don't pass these on. '''
    def __new__(class_, iterable=None, *args, **kwargs):
        return set.__new__(class_, iterable)

    def __cmp__(self, other):
        # If set.__cmp__ is called we get a TypeError in Python 2.5, so
        # call set.__eq__ instead
        if self == other:
            return 0
        else:
            return -1


class Event(object):
    ''' Event represents notification events. Events can notify about a single
        event type for a single source or for multiple event types and multiple
        sources at the same time. The Event methods try to make both uses easy.
        
        This creates an event for one type, one source and one value
        >>> event = Event('event type', 'event source', 'new value') 
        
        To add more event sources with their own value:
        >>> event.addSource('another source', 'another value')
        
        To add a source with a different event type:
        >>> event.addSource('yet another source', 'its value', type='another type')
        '''
        
    def __init__(self, type=None, source=None, *values):
        self.__sourcesAndValuesByType = {} if type is None else \
            {type: {} if source is None else {source: values}}

    def __repr__(self): # pragma: no cover
        return 'Event(%s)'%(self.__sourcesAndValuesByType)

    def __eq__(self, other):
        ''' Events compare equal when all their data is equal. '''
        return self.sourcesAndValuesByType() == other.sourcesAndValuesByType()

    def addSource(self, source, *values, **kwargs):
        ''' Add a source with optional values to the event. Optionally specify
            the type as keyword argument. If the source was added previously for 
            the specified type, its previous values *for the specified type* 
            are overwritten by the passed values. If no type is specified,
            the source and values are added for a random type, i.e. only omit 
            the type if the event has is only one type. '''
        type = kwargs.pop('type', self.type())
        self.__sourcesAndValuesByType.setdefault(type, {})[source] = values

    def type(self):
        ''' Return the event type. If there are multiple event types, this
            method returns an arbitrary event type. This method is useful if
            the caller is sure this event instance has exactly one event 
            type. '''
        return list(self.types())[0] if self.types() else None
    
    def types(self):
        ''' Return the set of event types that this event is notifying. '''
        return set(self.__sourcesAndValuesByType.keys())
    
    def sources(self, *types):
        ''' Return the set of all sources of this event instance, or the 
            sources for specific event types. '''
        types = types or self.types()
        sources = set()
        for type in types:
            sources |= set(self.__sourcesAndValuesByType.get(type, dict()).keys())
        return sources
    
    def sourcesAndValuesByType(self):
        ''' Return all data {type: {source: values}}. '''
        return self.__sourcesAndValuesByType

    def value(self, source=None, type=None):
        ''' Return the value that belongs to source. If there are multiple
            values, this method returns only the first one. So this method is 
            useful if the caller is sure there is only one value associated
            with source. If source is None return the value of an arbitrary 
            source. This latter option is useful if the caller is sure there 
            is only one source. '''
        return self.values(source, type)[0]

    def values(self, source=None, type=None):
        ''' Return the values that belong to source. If source is None return
            the values of an arbitrary source. This latter option is useful if
            the caller is sure there is only one source. '''
        type = type or self.type()
        source = source or self.__sourcesAndValuesByType[type].keys()[0]
        return self.__sourcesAndValuesByType[type][source]
    
    def subEvent(self, *typesAndSources):
        ''' Create a new event that contains a subset of the data of this 
            event. '''
        subEvent = self.__class__()
        for type, source in typesAndSources:
            sourcesToAdd = self.sources(type)
            if source is not None:
                # Make sure source is actually in self.sources(type):
                sourcesToAdd &= set([source])
            kwargs = dict(type=type) # Python doesn't allow type=type after *values 
            for eachSource in sourcesToAdd:
                subEvent.addSource(eachSource, *self.values(eachSource, type), **kwargs)
        return subEvent
    

class MethodProxy(object):
    ''' Wrap methods in a class that allows for comparing methods. Comparison
        if instance methods was changed in python 2.5. In python 2.5, instance
        methods are equal when their instances compare equal, which is not
        the behaviour we need for callbacks. So we wrap callbacks in this class
        to get back the old (correct, imho) behaviour. '''
        
    def __init__(self, method):
        self.method = method
        
    def __repr__(self):
        return 'MethodProxy(%s)'%self.method
        
    def __call__(self, *args, **kwargs):
        return self.method(*args, **kwargs)
        
    def __eq__(self, other):
        return self.method.im_class is other.method.im_class and \
               self.method.im_self is other.method.im_self and \
               self.method.im_func is other.method.im_func
               
    def __ne__(self, other):
        return not (self == other)
    
    def __hash__(self):
        # Can't use self.method.im_self for the hash, it might be mutable
        return hash((self.method.im_class, id(self.method.im_self), 
                     self.method.im_func))
                   
    def get_im_self(self):
        return self.method.im_self
    
    im_self = property(get_im_self)


def wrapObserver(decoratedMethod):
    ''' Wrap the observer argument (assumed to be the first after self) in
        a MethodProxy class. ''' 
    def decorator(self, observer, *args, **kwargs):
        assert hasattr(observer, 'im_self')
        observer = MethodProxy(observer)
        return decoratedMethod(self, observer, *args, **kwargs)
    return decorator


def unwrapObservers(decoratedMethod):
    ''' Unwrap the returned observers from their MethodProxy class. '''
    def decorator(*args, **kwargs):
        observers = decoratedMethod(*args, **kwargs)
        return [proxy.method for proxy in observers]
    return decorator


class Publisher(object):
    ''' Publisher is used to register for event notifications. It supports
        the publisher/subscribe pattern, also known as the observer pattern.
        Objects (Observers) interested in change notifications register a 
        callback method via Publisher.registerObserver. The callback should
        expect one argument; an instance of the Event class. Observers can 
        register their interest in specific event types (topics), and 
        optionally specific event sources, when registering. 
        
        Implementation note: 
        - Publisher is a Singleton class since all observables and all
        observers have to use exactly one registry to be sure that all
        observables can reach all observers. '''
        
    __metaclass__ = singleton.Singleton
    
    def __init__(self, *args, **kwargs):
        super(Publisher, self).__init__(*args, **kwargs)
        self.clear()
        
    def clear(self):
        ''' Clear the registry of observers. Mainly for testing purposes. '''
        self.__observers = {} # {(eventType, eventSource): set(callbacks)}
        self.__notifyingSemaphore = 0
    
    @wrapObserver
    def registerObserver(self, observer, eventType, eventSource=None):
        ''' Register an observer for an event type. The observer is a callback 
            method that should expect one argument, an instance of Event.
            The eventType can be anything hashable, typically a string. When 
            passing a specific eventSource, the observer is only called when the
            event originates from the specified eventSource. '''
            
        observers = self.__observers.setdefault((eventType, eventSource), set())
        if observers:
            observers.add(observer)
        else:
            observers.add(observer)
            self.notifyObserversOfFirstObserverRegistered(eventType)
    
    @wrapObserver    
    def removeObserver(self, observer, eventType=None, eventSource=None):
        ''' Remove an observer. If no event type is specified, the observer
            is removed for all event types. If an event type is specified
            the observer is removed for that event type only. If no event
            source is specified, the observer is removed for all event sources.
            If an event source is specified, the observer is removed for that
            event source only. If both an event type and an event source are
            specified, the observer is removed for the combination of that
            specific event type and event source only. '''
            
        # First, create a match function that will select the combination of
        # event source and event type we're looking for:
        if eventType and eventSource:
            def match(type, source):
                return type == eventType and source == eventSource
        elif eventType:
            def match(type, source): return type == eventType
        elif eventSource:
            def match(type, source): return source == eventSource
        else:
            def match(type, source): return True

        # Next, remove observers that are registered for the event source and
        # event type we're looking for, i.e. that match:    
        matchingKeys = [key for key in self.__observers if match(*key)] 
        for key in matchingKeys:
            self.__observers[key].discard(observer)
        self.notifyObserversOfLastObserverRemoved()
                
    def removeInstance(self, instance):
        ''' Remove all observers that are methods of instance. '''
        for observers in self.__observers.itervalues():
            for observer in observers.copy():
                if observer.im_self is instance:
                    observers.discard(observer)
        self.notifyObserversOfLastObserverRemoved()
        
    def notifyObserversOfFirstObserverRegistered(self, eventType):
        event = Event('publisher.firstObserverRegisteredFor', self, eventType)
        event.addSource(self, eventType, 
                        type='publisher.firstObserverRegisteredFor.%s'%eventType)
        self.notifyObservers(event)
                    
    def notifyObserversOfLastObserverRemoved(self):
        for eventType, eventSource in self.__observers.keys():
            if self.__observers[(eventType, eventSource)]:
                continue
            del self.__observers[(eventType, eventSource)]
            self.notifyObservers(Event( 
                'publisher.lastObserverRemovedFor.%s'%eventType, self, 
                eventType))
        
    def notifyObservers(self, event):
        ''' Notify observers of the event. The event type and sources are 
            extracted from the event. '''
        if not self.isNotifying() or not event.sources():
            return
        # Collect observers *and* the types and sources they are registered for
        observers = dict() # {observer: set([(type, source), ...])} 
        types = event.types()
        # Include observers not registered for a specific event source:
        sources = event.sources() | set([None])
        eventTypesAndSources = [(type, source) for source in sources for type in types]
        for eventTypeAndSource in eventTypesAndSources:
            for observer in self.__observers.get(eventTypeAndSource, set()):
                observers.setdefault(observer, set()).add(eventTypeAndSource)
        for observer, eventTypesAndSources in observers.iteritems():
            observer(event.subEvent(*eventTypesAndSources))
     
    @unwrapObservers           
    def observers(self, eventType=None):
        ''' Get the currently registered observers. Optionally specify
            a specific event type to get observers for that event type only. '''
        if eventType:
            return self.__observers.get((eventType, None), set())
        else:
            result = set()
            for observers in self.__observers.values():
                result |= observers
            return result
    
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
    def registerObserver(self, *args, **kwargs):
        Publisher().registerObserver(*args, **kwargs)
        
    def removeObserver(self, *args, **kwargs):
        Publisher().removeObserver(*args, **kwargs)


class Decorator(Observer):
    def __init__(self, observable, *args, **kwargs):
        self.__observable = observable
        super(Decorator, self).__init__(*args, **kwargs)

    def observable(self):
        return self.__observable 

    def __getattr__(self, attribute):
        return getattr(self.observable(), attribute)


class Observable(object):
    def notifyObservers(self, *args, **kwargs):
        Publisher().notifyObservers(*args, **kwargs)
        
    def startNotifying(self, *args, **kwargs):
        Publisher().startNotifying(*args, **kwargs)
        
    def stopNotifying(self, *args, **kwargs):
        Publisher().stopNotifying(*args, **kwargs)

    @classmethod
    def modificationEventTypes(class_):
        return []        


class ObservableCollection(Observable):
    def __hash__(self):
        ''' Make ObservableCollections suitable as keys in dictionaries. '''
        return hash(id(self))

    @classmethod
    def addItemEventType(class_):
        ''' The event type used to notify observers that one or more items
            have been added to the collection. '''
        return '%s.add'%class_
    
    @classmethod
    def removeItemEventType(class_):
        ''' The event type used to notify observers that one or more items
            have been removed from the collection. '''
        return '%s.remove'%class_

    def notifyObserversOfItemsAdded(self, *items):
        self.notifyObservers(Event(self.addItemEventType(), self, *items))

    def notifyObserversOfItemsRemoved(self, *items):
        self.notifyObservers(Event(self.removeItemEventType(), self, *items))

    @classmethod
    def modificationEventTypes(class_):
        eventTypes = super(ObservableCollection, class_).modificationEventTypes()
        return eventTypes + [class_.addItemEventType(), 
                             class_.removeItemEventType()]


class ObservableSet(ObservableCollection, Set):
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            result = self is other
        else:
            result = list(self) == other
        return result

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
               

class CollectionDecorator(Decorator, ObservableCollection):
    ''' CollectionDecorator observes an ObservableCollection and is an
        ObservableCollection itself too. Its purpose is to decorate another 
        collection and add some behaviour, such as sorting or filtering. 
        Users of this class shouldn't see a difference between using the 
        original collection or a decorated version. '''

    def __init__(self, observedCollection, *args, **kwargs):
        super(CollectionDecorator, self).__init__(observedCollection, *args, **kwargs)
        observable = self.observable()
        self.registerObserver(self.onAddItem, 
            eventType=observable.addItemEventType(), eventSource=observable)
        self.registerObserver(self.onRemoveItem, 
            eventType=observable.removeItemEventType(), eventSource=observable)
        self.extendSelf(observable)

    def __repr__(self): # pragma: no cover
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

