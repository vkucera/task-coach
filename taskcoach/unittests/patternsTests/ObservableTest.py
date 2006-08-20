import test, patterns

class EventTest(test.TestCase):
    def testEqualWhenAllValuesAreEqual(self):
        self.assertEqual(patterns.Event(self, 'eventtype', 'some value'), 
                         patterns.Event(self, 'eventtype', 'some value'))

    def testUnequalWhenValuesAreDifferent(self):
        self.assertNotEqual(patterns.Event(self, 'eventtype', 'some value'), 
                            patterns.Event(self, 'eventtype', 'other value'))
    
    def testUnequalWhenTypesAreDifferent(self):
        self.assertNotEqual(patterns.Event(self, 'eventtype', 'some value'), 
                            patterns.Event(self, 'other type', 'some value'))

    def testUnequalWhenSourcesAreDifferent(self):
        self.assertNotEqual(patterns.Event(self, 'eventtype', 'some value'), 
                            patterns.Event(None, 'eventtype', 'some value'))


class ObservableTest(test.TestCase):
    def setUp(self):
        self.events = []
        
    def onEvent(self, event):
        self.events.append(event)
        
    def testNotifyObservers(self):
        patterns.Publisher().registerObserver(self.onEvent, 'eventType')
        observable = patterns.Observable()
        event = patterns.Event(observable, 'eventType')
        observable.notifyObservers(event)
        self.assertEqual([event], self.events)
        

class ObservableCollectionFixture(test.TestCase):
    def setUp(self):
        self.collection = self.createObservableCollection()
        patterns.Publisher().registerObserver(self.onAdd, 
            eventType=self.collection.addItemEventType())
        patterns.Publisher().registerObserver(self.onRemove,
            eventType=self.collection.removeItemEventType())
        self.receivedAddEvents = []
        self.receivedRemoveEvents = []

    def onAdd(self, event):
        self.receivedAddEvents.append(event)

    def onRemove(self, event):
        self.receivedRemoveEvents.append(event)


class ObservableCollectionTests(object):
    def testAppend(self):
        self.collection.append(1)
        self.failUnless(1 in self.collection)
        
    def testAppend_Notification(self):
        self.collection.append(1)
        self.assertEqual(1, self.receivedAddEvents[0].value())

    def testExtend(self):
        self.collection.extend([1, 2])
        self.failUnless(1 in self.collection and 2 in self.collection)
        
    def testExtend_Notification(self):
        self.collection.extend([1, 2, 3])
        self.assertEqual((1, 2, 3), self.receivedAddEvents[0].values())

    def testExtend_NoNotificationWhenNoItems(self):
        self.collection.extend([])
        self.failIf(self.receivedAddEvents)

    def testRemove(self):
        self.collection.append(1)
        self.collection.remove(1)
        self.failIf(self.collection)

    def testRemove_Notification(self):
        self.collection.append(1)
        self.collection.remove(1)
        self.assertEqual(1, self.receivedRemoveEvents[0].value())
    
    def testRemovingAnItemNotInCollection_CausesException(self):
        try:
            self.collection.remove(1)
            self.fail('Expected ValueError or KeyError')
        except (ValueError, KeyError):
            pass

    def testRemovingAnItemNotInCollection_CausesNoNotification(self):
        try:
            self.collection.remove(1)
        except (ValueError, KeyError):
            pass
        self.failIf(self.receivedRemoveEvents)

    def testRemoveItems(self):
        self.collection.extend([1, 2, 3])
        self.collection.removeItems([1, 2])
        self.failIf(1 in self.collection or 2 in self.collection)

    def testRemoveItems_Notification(self):
        self.collection.extend([1, 2, 3])
        self.collection.removeItems([1, 2])
        self.assertEqual((1, 2), self.receivedRemoveEvents[0].values())

    def testRemoveItems_NoNotificationWhenNoItems(self):
        self.collection.extend([1, 2, 3])
        self.collection.removeItems([])
        self.failIf(self.receivedRemoveEvents)
        
    def testClear(self):
        self.collection.extend([1, 2, 3])
        self.collection.clear()
        self.failIf(self.collection)
        
    def testClear_Notification(self):
        self.collection.extend([1, 2, 3])
        self.collection.clear()
        self.assertEqual((1, 2, 3), self.receivedRemoveEvents[0].values())
        
    def testClear_NoNotificationWhenNoItems(self):
        self.collection.clear()
        self.failIf(self.receivedRemoveEvents)
        
        
class ObservableListTest(ObservableCollectionFixture, ObservableCollectionTests):
    def createObservableCollection(self):
        return patterns.ObservableList()
    

class ObservableSetTest(ObservableCollectionFixture, ObservableCollectionTests):
    def createObservableCollection(self):
        return patterns.ObservableSet()
        

class ListDecoratorTest_Constructor(test.TestCase):
    def testOriginalNotEmpty(self):
        observable = patterns.ObservableList([1, 2, 3])
        observer = patterns.ListDecorator(observable)
        self.assertEqual([1, 2, 3], observer)


class SetDecoratorTest_Constructor(test.TestCase):
    def testOriginalNotEmpty(self):
        observable = patterns.ObservableSet([1, 2, 3])
        observer = patterns.SetDecorator(observable)
        self.assertEqual([1, 2, 3], observer)


class ListDecoratorTest_AddItems(test.TestCase):
    def setUp(self):
        self.observable = patterns.ObservableList()
        self.observer = patterns.ListDecorator(self.observable)

    def testAppendToObservable(self):
        self.observable.append(1)
        self.assertEqual([1], self.observer)

    def testAppendToObserver(self):
        self.observer.append(1)
        self.assertEqual([1], self.observable)
        
    def testExtendObservable(self):
        self.observable.extend([1, 2, 3])
        self.assertEqual([1, 2, 3], self.observer)

    def testExtendObserver(self):
        self.observer.extend([1, 2, 3])
        self.assertEqual([1, 2, 3], self.observable)


class SetDecoratorTest_AddItems(test.TestCase):
    def setUp(self):
        self.observable = patterns.ObservableList()
        self.observer = patterns.SetDecorator(self.observable)

    def testAppendToObservable(self):
        self.observable.append(1)
        self.assertEqual([1], self.observer)

    def testAppendToObserver(self):
        self.observer.append(1)
        self.assertEqual([1], self.observable)
        
    def testExtendObservable(self):
        self.observable.extend([1, 2, 3])
        self.assertEqual([1, 2, 3], self.observer)

    def testExtendObserver(self):
        self.observer.extend([1, 2, 3])
        self.assertEqual([1, 2, 3], self.observable)


class ListDecoratorTest_RemoveItems(test.TestCase):
    def setUp(self):
        self.observable = patterns.ObservableList()
        self.observer = patterns.ListDecorator(self.observable)
        self.observable.extend([1, 2, 3])

    def testRemoveFromOriginal(self):
        self.observable.remove(1)
        self.assertEqual([2, 3], self.observer)

    def testRemoveFromObserver(self):
        self.observer.remove(1)
        self.assertEqual([2, 3], self.observable)

    def testRemoveItemsFromOriginal(self):
        self.observable.removeItems([1, 2])
        self.assertEqual([3], self.observer)

    def testRemoveItemsFromObserver(self):
        self.observer.removeItems([1, 2])
        self.assertEqual([3], self.observable)


class SetDecoratorTest_RemoveItems(test.TestCase):
    def setUp(self):
        self.observable = patterns.ObservableList()
        self.observer = patterns.SetDecorator(self.observable)
        self.observable.extend([1, 2, 3])

    def testRemoveFromOriginal(self):
        self.observable.remove(1)
        self.assertEqual([2, 3], self.observer)

    def testRemoveFromObserver(self):
        self.observer.remove(1)
        self.assertEqual([2, 3], self.observable)

    def testRemoveItemsFromOriginal(self):
        self.observable.removeItems([1, 2])
        self.assertEqual([3], self.observer)

    def testRemoveItemsFromObserver(self):
        self.observer.removeItems([1, 2])
        self.assertEqual([3], self.observable)
    

class ListDecoratorTest_ObserveTheObserver(test.TestCase):
    def setUp(self):
        self.list = patterns.ObservableList()
        self.observer = patterns.ListDecorator(self.list)
        patterns.Publisher().registerObserver(self.onAdd, 
            eventType=self.observer.addItemEventType())
        patterns.Publisher().registerObserver(self.onRemove,
            eventType=self.observer.removeItemEventType())
        self.receivedAddEvents = []
        self.receivedRemoveEvents = []

    def onAdd(self, event):
        self.receivedAddEvents.append(event)

    def onRemove(self, event):
        self.receivedRemoveEvents.append(event)

    def testExtendOriginal(self):
        self.list.extend([1, 2, 3])
        self.assertEqual((1, 2, 3), self.receivedAddEvents[0].values())

    def testExtendObserver(self):
        self.observer.extend([1, 2, 3])
        self.assertEqual((1, 2, 3), self.receivedAddEvents[0].values())

    def testRemoveItemsFromOriginal(self):
        self.list.extend([1, 2, 3])
        self.list.removeItems([1, 3])
        self.assertEqual((1, 3), self.receivedRemoveEvents[0].values())

    def testRemoveItemsFromOriginal(self):
        self.list.extend([1, 2, 3])
        self.observer.removeItems([1, 3])
        self.assertEqual((1, 3), self.receivedRemoveEvents[0].values())
        

class PublisherTest(test.TestCase):
    def setUp(self):
        self.publisher = patterns.Publisher()
        self.events = []
        
    def onEvent(self, event):
        self.events.append(event)
                
    def testPublisherIsSingleton(self):
        anotherPublisher = patterns.Publisher()
        self.failUnless(self.publisher is anotherPublisher)
        
    def testRegisterObserver(self):
        self.publisher.registerObserver(self.onEvent, eventType='eventType')
        self.assertEqual([self.onEvent], self.publisher.observers())

    def testRegisterObserver_Twice(self):
        self.publisher.registerObserver(self.onEvent, eventType='eventType')
        self.publisher.registerObserver(self.onEvent, eventType='eventType')
        self.assertEqual([self.onEvent], self.publisher.observers())
        
    def testRegisterObserver_ForTwoDifferentTypes(self):
        self.publisher.registerObserver(self.onEvent, eventType='eventType1')
        self.publisher.registerObserver(self.onEvent, eventType='eventType2')
        self.assertEqual([self.onEvent, self.onEvent],
            self.publisher.observers())
        
    def testRegisterObserver_ListMethod(self):
        ''' A previous implementation of Publisher used sets. This caused a 
            "TypeError: list objects are unhashable" whenever one tried to use
            an instance method of a list (sub)class as callback. '''
        class List(list):
            def onEvent(self, *args):
                pass
        self.publisher.registerObserver(List().onEvent, eventType='eventType')    

    def testGetObservers_WithoutObservers(self):
        self.assertEqual([], self.publisher.observers())
        
    def testGetObserversForSpecificEventType_WithoutObservers(self):
        self.assertEqual([], self.publisher.observers(eventType='eventType'))

    def testGetObserversForSpecificEventType_WithObserver(self):
        self.publisher.registerObserver(self.onEvent, eventType='eventType')
        self.assertEqual([self.onEvent], 
            self.publisher.observers(eventType='eventType'))
            
    def testGetObserversForSpecificEventType_WhenDifferentTypesRegistered(self):
        self.publisher.registerObserver(self.onEvent, eventType='eventType1')
        self.publisher.registerObserver(self.onEvent, eventType='eventType2')
        self.assertEqual([self.onEvent], 
            self.publisher.observers(eventType='eventType1'))

    def testGetAllObservers_WhenDifferentTypesRegistered(self):
        self.publisher.registerObserver(self.onEvent, eventType='eventType1')
        self.publisher.registerObserver(self.onEvent, eventType='eventType2')
        self.assertEqual([self.onEvent, self.onEvent], 
            self.publisher.observers())            
            
    def testNotifyObservers_WithoutObservers(self):
        self.publisher.notifyObservers(patterns.Event(self, 'eventType'))
        self.failIf(self.events)

    def testNotifyObservers_WithObserverForDifferentEventType(self):
        self.publisher.registerObserver(self.onEvent, eventType='eventType1')
        self.publisher.notifyObservers(patterns.Event(self, 'eventType2'))
        self.failIf(self.events)
        
    def testNotifyObservers_WithObserverForRightEventType(self):
        self.publisher.registerObserver(self.onEvent, eventType='eventType')
        self.publisher.notifyObservers(patterns.Event(self, 'eventType'))
        self.assertEqual([patterns.Event(self, 'eventType')], self.events)
        
    def testNotifyObservers_WithObserversForSameAndDifferentEventTypes(self):
        self.publisher.registerObserver(self.onEvent, eventType='eventType1')
        self.publisher.registerObserver(self.onEvent, eventType='eventType2')
        self.publisher.notifyObservers(patterns.Event(self, 'eventType1'))
        self.assertEqual([patterns.Event(self, 'eventType1')], self.events)
        
    def testRemoveObserverForAnyEventType_NotRegisteredBefore(self):
        self.publisher.removeObserver(self.onEvent)
        self.assertEqual([], self.publisher.observers())
        
    def testRemoveObserverForAnyEventType_RegisteredBefore(self):
        self.publisher.registerObserver(self.onEvent, eventType='eventType')
        self.publisher.removeObserver(self.onEvent)
        self.assertEqual([], self.publisher.observers())

    def testRemoveObserverForSpecificType_RegisteredForSameType(self):
        self.publisher.registerObserver(self.onEvent, eventType='eventType')
        self.publisher.removeObserver(self.onEvent, eventType='eventType')
        self.assertEqual([], self.publisher.observers())

    def testRemoveObserverForSpecificType_RegisteredForDifferentType(self):
        self.publisher.registerObserver(self.onEvent, eventType='eventType')
        self.publisher.removeObserver(self.onEvent, eventType='otherType')
        self.assertEqual([self.onEvent], self.publisher.observers())

    def testClear(self):
        self.publisher.registerObserver(self.onEvent, eventType='eventType')
        self.publisher.clear()
        self.assertEqual([], self.publisher.observers())
        
    def testStopNotifying(self):
        self.publisher.registerObserver(self.onEvent, eventType='eventType')
        self.publisher.stopNotifying()
        self.publisher.notifyObservers(patterns.Event(self, 'eventType'))
        self.failIf(self.events)
        
    def testStartNotifying(self):
        self.publisher.registerObserver(self.onEvent, eventType='eventType')
        self.publisher.stopNotifying()
        self.publisher.startNotifying()
        self.publisher.notifyObservers(patterns.Event(self, 'eventType'))
        self.assertEqual([patterns.Event(self, 'eventType')], self.events)

    def testNestedStopNotifying(self):
        self.publisher.registerObserver(self.onEvent, eventType='eventType')
        self.publisher.stopNotifying()
        self.publisher.stopNotifying()
        self.publisher.startNotifying()
        self.publisher.notifyObservers(patterns.Event(self, 'eventType'))
        self.failIf(self.events)
        
    def testNestedStartNotifying(self):
        self.publisher.registerObserver(self.onEvent, eventType='eventType')
        self.publisher.stopNotifying()
        self.publisher.stopNotifying()
        self.publisher.startNotifying()
        self.publisher.startNotifying()
        self.publisher.notifyObservers(patterns.Event(self, 'eventType'))
        self.assertEqual([patterns.Event(self, 'eventType')], self.events)

        