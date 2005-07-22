class List(list):    
    def removeItems(self, items):
        ''' List.removeItems is the opposite of list.extend. Useful for 
            ObservableList to be able to generate just one notification 
            when removing multiple items. '''
        for item in items:
            # No super() to prevent overridden remove method from being invoked
            list.remove(self, item) 

    
class Notification(object):
    ''' Notification represents notification events. There is one mandatory 
        attribute: source. Other attributes are set as needed through kwargs. 
        A receiver of a notification can query the attributes. Non-existent
        attributes have a default value of []. '''
        
    def __init__(self, source, *args, **kwargs):
        self.source = source
        self.__dict__.update(kwargs)
        super(Notification, self).__init__(*args, **kwargs)
        
    def __getattr__(self, attr):
        return []
        
    def __str__(self):
        kwargs = self.__dict__.copy()
        del kwargs['source']
        sourceStr = '%s'%self.source
        if len(sourceStr) > 40:
            sourceStr = sourceStr[:40] + '...'
        return 'Notification(source=%s(%s), kwargs=%s)'%(self.source.__class__.__name__, sourceStr, kwargs)

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __nonzero__(self):
        kwargs = self.__dict__.copy()
        del kwargs['source']
        for value in kwargs.values():
            if value:
                return True
        return False

                
class Observable(object):
    ''' Observable objects can be observed by registering (subscribing) a 
        callback method with Observable.registerObserver. The callback is 
        called when the object changes. Subclasses should call 
        Observer._notifyObserversOfChange to notify observers. Observers can
        remove themselves (unsubscribe) by calling Observable.removeObserver. '''
        
    def __init__(self, *args, **kwargs):
        super(Observable, self).__init__(*args, **kwargs)
        self.__callbacks = []
        self.startNotifying()
        
    def stopNotifying(self):
        self.__notifying = False
        
    def startNotifying(self):
        self.__notifying = True

    def isNotifying(self):
        return self.__notifying
        
    def registerObserver(self, callback):
        ''' Register an observer. The callback should be a callable and 
            accept one argument (the observable), see 
            Observable._notifyObserversOfChange. 
            NB: this is in the process of changing: callbacks will need to 
            accept one argument in the future, a Notification instance. '''
        self.__callbacks.append(callback)
        
    def removeObserver(self, callback):
        ''' Remove a callback that was registered earlier. '''
        try:
            self.__callbacks.remove(callback)
        except ValueError:
            pass

    def notifyObservers(self, notification):
        if not self.isNotifying():
            return
        for callback in self.__callbacks:
            callback(notification)

    def observers(self):
        return self.__callbacks



class ObservablesList(List):
    ''' ObservablesList is a list of observables, i.e. all items that are 
        put in the list should obey the Observable interface as defined by 
        the Observable class. ObservablesList registers itself as observer 
        of all items that are put into the list. Subclasses of ObservablesList 
        should override ObservablesList.onNotify if they want to react to
        changes of items in the list. '''
    
    def __init__(self, initList=None, *args, **kwargs):
        super(ObservablesList, self).__init__(initList or [], *args, **kwargs)
        self.__subscribe(*(initList or []))
        
    def onNotify(self, notification, *args, **kwargs):
        ''' This method is called by items in the list when they change. 
            Override to react to those changes. '''
        pass
    
    def __subscribe(self, *observables):
        ''' Private method to subscribe to one or more observables. '''
        for observable in observables:
            observable.registerObserver(self.onNotify)
            
    def __unsubscribe(self, *observables):
        ''' Private method to unsubcribe to one or more observables. '''
        for observable in observables:
            observable.removeObserver(self.onNotify)
        
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
    
    def append(self, item):
        super(ObservableList, self).append(item)
        self.notifyObservers(Notification(self, changeNeedsSave=True, itemsAdded=[item]))

    def extend(self, items):
        if items:
            super(ObservableList, self).extend(items)
            self.notifyObservers(Notification(self, changeNeedsSave=True, itemsAdded=items))

    def insert(self, index, item):
        super(ObservableList, self).insert(index, item)
        self.notifyObservers(Notification(self, changeNeedsSave=True, itemsAdded=[item]))

    def remove(self, item):
        super(ObservableList, self).remove(item)
        self.notifyObservers(Notification(self, changeNeedsSave=True, itemsRemoved=[item]))
    
    def removeItems(self, items):
        if items:
            super(ObservableList, self).removeItems(items)
            self.notifyObservers(Notification(self, changeNeedsSave=True, itemsRemoved=items))
            
    def __delitem__(self, index):
        item = self[index]
        super(ObservableList, self).__delitem__(index)
        self.notifyObservers(Notification(self, changeNeedsSave=True, itemsRemoved=[item]))
        
    def __delslice__(self, *slice):
        items = self.__getslice__(*slice)
        if items:
            super(ObservableList, self).__delslice__(*slice)
            self.notifyObservers(Notification(self, changeNeedsSave=True, itemsRemoved=items))


class ObservableObservablesList(ObservableList, ObservablesList):
    ''' A list of observables that is observable. '''
    
    def onNotify(self, notification, *args, **kwargs):
        myNotification = Notification(self, changeNeedsSave=notification.changeNeedsSave,
            itemsChanged=[notification.source])
        self.notifyObservers(myNotification)


class ObservableListObserver(ObservableList):
    ''' ObservableListObserver observes an ObservableObservablesList. '''
    
    def __init__(self, observedList, *args, **kwargs):
        super(ObservableListObserver, self).__init__(*args, **kwargs)
        self.__observedList = observedList
        self.__observedList.registerObserver(self.onNotify)
        self.onNotify(Notification(self.__observedList, itemsAdded=self.__observedList))

    def onNotify(self, notification, *args, **kwargs):
        ''' By default, we add items that were added to the original list
            and we remove items that we removed from the original list. '''
        if not notification:
            return
        self.stopNotifying()
        notification = self.processChanges(notification)
        notification = self.postProcessChanges(notification)
        self.startNotifying()
        self.notifyObservers(notification, *args, **kwargs)

    def processChanges(self, notification):
        self._extend(notification.itemsAdded)
        self._removeItems(notification.itemsRemoved)
        return notification
        
    def postProcessChanges(self, notification):
        return notification
        
    def original(self):
        return self.__observedList

    def reset(self):
        self.onNotify(Notification(source=self, orderChanged=True))
        
    # delegate changes to the original list

    def append(self, item):
        self.__observedList.append(item)
            
    def extend(self, items):
        self.__observedList.extend(items)
        
    def remove(self, item):
        self.__observedList.remove(item)
    
    def removeItems(self, items):
        self.__observedList.removeItems(items)
        
    def __delitem__(self, index):
        del self.__observedList[index]

    def __delslice__(self, *slice):
        self.__observedList.__delslice__(*slice)

    def insert(self, index, item):
        self.__observedList.insert(index, item)

    def __getattr__(self, attribute):
        return getattr(self.__observedList, attribute)
    
    # provide two methods to manipulate the ObservableListObserver itself

    def _extend(self, items):
        super(ObservableListObserver, self).extend(items)
    
    def _removeItems(self, items):
        super(ObservableListObserver, self).removeItems(items)
        
