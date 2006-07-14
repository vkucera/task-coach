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
        self.observable = patterns.Observable()
        self.observable.registerObserver(self.onEvent, 'eventtype')
        self.event = patterns.Event(self, 'eventtype', 'some value')
        self.eventsReceived = []

    def onEvent(self, event):
        self.eventsReceived.append(event)

    def testRegisterObserver(self):
        self.assertEqual([self.onEvent],
            self.observable.observers('eventtype'))

    def testNotifyObservers(self):
        self.observable.notifyObservers(self.event)
        self.assertEqual(self.event, self.eventsReceived[0])
        
    def testRemoveObserver(self):
        self.observable.removeObserver(self.onEvent)
        self.assertEqual([], self.observable.observers('eventtype'))
        self.observable.notifyObservers(self.event)
        self.failIf(self.eventsReceived)

    def testRemoveObserverTwice(self):
        self.observable.removeObserver(self.onEvent)
        self.observable.removeObserver(self.onEvent)

    def testNotifyObserverWithAnotherEventType(self):
        event = patterns.Event(self, 'eventtype2', 'some value')
        self.observable.notifyObservers(event)
        self.failIf(self.eventsReceived)

    def testMultipleObservers(self):
        self.observable.registerObserver(self.onEvent, 'eventtype')
        self.observable.notifyObservers(self.event)
        self.assertEqual([self.event]*2, self.eventsReceived)

    # Semaphore tests:

    def testStopNotifying(self):
        self.observable.stopNotifying()
        self.observable.notifyObservers(self.event)
        self.failIf(self.eventsReceived)

    def testStartNotifying(self):
        self.observable.stopNotifying()
        self.observable.startNotifying()
        self.observable.notifyObservers(self.event)
        self.assertEqual(self.event, self.eventsReceived[0])

    def testStopNotifyingTwice(self):
        self.observable.stopNotifying()
        self.observable.stopNotifying()
        self.observable.notifyObservers(self.event)
        self.failIf(self.eventsReceived)

    def testStopNotifyingTwiceAndStartNotifyingOnce(self):
        self.observable.stopNotifying()
        self.observable.stopNotifying()
        self.observable.startNotifying()
        self.observable.notifyObservers(self.event)
        self.failIf(self.eventsReceived)

    def testStopNotifyingTwiceAndStartNotifyingTwice(self):
        self.observable.stopNotifying()
        self.observable.stopNotifying()
        self.observable.startNotifying()
        self.observable.startNotifying()
        self.observable.notifyObservers(self.event)
        self.assertEqual(self.event, self.eventsReceived[0])


class ObserverTest(test.TestCase):
    def setUp(self):
        self.observable = patterns.Observable()
        self.observer = patterns.Observer(self.observable)

    def testObservable(self):
        self.assertEqual(self.observable, self.observer.observable())


class ObservableListTest(test.TestCase):
    def setUp(self):
        self.list = patterns.ObservableList()
        self.list.registerObserver(self.onAdd, 'list.add')
        self.list.registerObserver(self.onRemove, 'list.remove')
        self.receivedAddEvents = []
        self.receivedRemoveEvents = []

    def onAdd(self, event):
        self.receivedAddEvents.append(event)

    def onRemove(self, event):
        self.receivedRemoveEvents.append(event)

    def testAppend(self):
        self.list.append(1)
        self.assertEqual(1, self.receivedAddEvents[0].value())

    def testExtend(self):
        self.list.extend([1, 2, 3])
        self.assertEqual((1, 2, 3), self.receivedAddEvents[0].values())

    def testExtend_NoItems(self):
        self.list.extend([])
        self.failIf(self.receivedAddEvents)

    def testInsert(self):
        self.list.insert(0, 'abc')
        self.assertEqual('abc', self.receivedAddEvents[0].value())

    def testRemove(self):
        self.list.append(1)
        self.list.remove(1)
        self.assertEqual(1, self.receivedRemoveEvents[0].value())

    def testRemoveItems(self):
        self.list.extend([1, 2, 3])
        self.list.removeItems([1, 2])
        self.assertEqual((1, 2), self.receivedRemoveEvents[0].values())

    def testRemoveItems_NoItems(self):
        self.list.extend([1, 2, 3])
        self.list.removeItems([])
        self.failIf(self.receivedRemoveEvents)

    def testDeleteItem(self):
        self.list.extend([1, 2, 3])
        del self.list[0]
        self.assertEqual(1, self.receivedRemoveEvents[0].value())

    def testDeleteSlice(self):
        self.list.extend([1, 2, 3])
        del self.list[0:2]
        self.assertEqual((1, 2), self.receivedRemoveEvents[0].values())

    def testOriginalNotEmpty(self):
        list = patterns.ObservableList([1, 2, 3])
        observer = patterns.ListDecorator(list)
        self.assertEqual([1, 2, 3], observer)


class ListDecoratorTest_AddItems(test.TestCase):
    def setUp(self):
        self.list = patterns.ObservableList()
        self.observer = patterns.ListDecorator(self.list)

    def testAppendToOriginal(self):
        self.list.append(1)
        self.assertEqual(1, self.observer[0])

    def testAppendToObserver(self):
        self.observer.append(1)
        self.failUnless(1 == self.list[0] == self.observer[0])

    def testExtendOriginal(self):
        self.list.extend([1, 2, 3])
        self.assertEqual([1, 2, 3], self.observer)

    def testExtendObserver(self):
        self.observer.extend([1, 2, 3])
        self.failUnless([1, 2, 3] == self.list == self.observer)

    def testInsertOriginal(self):
        self.list.insert(0, 'abc')
        self.assertEqual('abc', self.observer[0])

    def testInsertObserver(self):
        self.observer.insert(0, 'abc')
        self.failUnless('abc' == self.list[0] == self.observer[0])


class ListDecoratorTest_RemoveItems(test.TestCase):
    def setUp(self):
        self.list = patterns.ObservableList()
        self.observer = patterns.ListDecorator(self.list)
        self.list.extend([1, 2, 3])

    def testRemoveFromOriginal(self):
        self.list.remove(1)
        self.failUnless([2, 3] == self.list == self.observer)

    def testRemoveFromObserver(self):
        self.observer.remove(1)
        self.failUnless([2, 3] == self.list == self.observer)

    def testRemoveItemsFromOriginal(self):
        self.list.removeItems([1, 2])
        self.failUnless([3] == self.list == self.observer)

    def testRemoveItemsFromObserver(self):
        self.observer.removeItems([1, 2])
        self.failUnless([3] == self.list == self.observer)

    def testDeleteFromOriginal(self):
        del self.list[1]
        self.failUnless([1, 3] == self.list == self.observer)

    def testDeleteFromObserver(self):
        del self.observer[1]
        self.failUnless([1, 3] == self.list == self.observer)

    def testDeleteSliceFromOriginal(self):
        del self.list[0:2]
        self.failUnless([3] == self.list == self.observer)

    def testDeleteSliceFromObserver(self):
        del self.observer[0:2]
        self.failUnless([3] == self.list == self.observer)


class ListDecoratorTest_ObserveTheObserver(test.TestCase):
    def setUp(self):
        self.list = patterns.ObservableList()
        self.observer = patterns.ListDecorator(self.list)
        self.observer.registerObserver(self.onAdd, 'list.add')
        self.observer.registerObserver(self.onRemove, 'list.remove')
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
