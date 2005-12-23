import test, patterns

    
class ObservableTestCase(test.TestCase):
    def setUp(self):
        super(ObservableTestCase, self).setUp()
        self.addNotifications = self.removeNotifications = self.changeNotifications = 0
        self.addedItems = self.removedItems = self.changedItems = None
        self.observable = self.getObservable()
        self.observable.registerObserver(self.onNotify)
        
    def onNotify(self, notification, *args, **kwargs):
        if notification.itemsAdded:
            self.addNotifications += 1
            self.addedItems = notification.itemsAdded
        elif notification.itemsRemoved:
            self.removeNotifications += 1
            self.removedItems = notification.itemsRemoved
        elif notification.itemsChanged:
            self.changeNotifications += 1
            self.changedItems = notification.itemsChanged        
        else:
            self.changeNotifications += 1
            self.changedItems = notification.source
            
            
class ObservableTest(ObservableTestCase):
    def getObservable(self):
        return patterns.Observable()

    def check(self, notifications):
        self.assertEqual(notifications, self.changeNotifications)
        
    def testNoNotificationOnRegistration(self):
        self.check(notifications=0)

    def testNotificationOnChange(self):
        self.observable.notifyObservers(patterns.observer.Notification(self.observable))
        self.check(notifications=1)

    def testRemoveObserver(self):
        self.observable.removeObserver(self.onNotify)
        self.observable.notifyObservers(patterns.observer.Notification(self.observable))
        self.check(notifications=0)

    def testRemoveObserverTwice(self):
        self.observable.removeObserver(self.onNotify)
        self.observable.removeObserver(self.onNotify)


class ObservableWithEventTypeTest(test.TestCase):
    def setUp(self):
        self.observable = patterns.Observable()
        self.observable.registerObserver(self.onNotify, 'OnlyInterestedInThis')
        self.notifications = 0

    def onNotify(self, *args, **kwargs):
        self.notifications += 1
        
    def testInterestedInNotification(self):
        self.observable.notifyObservers(patterns.Notification(self.observable), 'OnlyInterestedInThis')
        self.assertEqual(1, self.notifications)
        
    def testNotInterestedInNotification(self):
        self.observable.notifyObservers(patterns.Notification(self.observable), 'SomethingElseHappened')
        self.assertEqual(0, self.notifications)
        
    def testNotificationWithoutEventType(self):
        self.observable.notifyObservers(patterns.Notification(self.observable))
        self.assertEqual(0, self.notifications)

    def testRegisterForMultipleEventTypes(self):
        self.observable.registerObserver(self.onNotify, 'AnotherEventType')
        self.observable.notifyObservers(patterns.Notification(self.observable), 'AnotherEventType')
        self.assertEqual(1, self.notifications)

    def testRegisterForMultipleEventTypesAtOnce(self):
        self.observable.registerObserver(self.onNotify, 'AnotherEventType', 'AndAnother')
        self.observable.notifyObservers(patterns.Notification(self.observable), 'AnotherEventType')
        self.observable.notifyObservers(patterns.Notification(self.observable), 'AndAnother')
        self.assertEqual(2, self.notifications)
        
        
class MockObservablesList(patterns.ObservablesList):
    def __init__(self, *args, **kwargs):
        super(MockObservablesList, self).__init__(*args, **kwargs)
        self.notifications = 0
        
    def onNotify(self, *args):
        self.notifications += 1
        super(MockObservablesList, self).onNotify(*args)

        
class ObservablesListTest(test.TestCase):
    def setUp(self):
        self.list = MockObservablesList()
        self.observable = patterns.Observable()
    
    def assertNotificationsAfterChange(self, notifications):
        self.observable.notifyObservers(patterns.observer.Notification(self.observable))
        self.assertEqual(notifications, self.list.notifications)
            
    def testCreate(self):
        self.assertEqual(0, len(self.list))
        
    def testCreateWithInitList(self):
        self.list = MockObservablesList([self.observable])
        self.assertNotificationsAfterChange(1)
        
    def testAppend(self):
        self.list.append(self.observable)
        self.assertNotificationsAfterChange(1)
        
    def testExtend(self):
        self.list.extend([self.observable])
        self.assertNotificationsAfterChange(1)
        
    def testDeleteItem(self):
        self.list.append(self.observable)
        del self.list[0]
        self.assertNotificationsAfterChange(0)
    
    def testDeleteSlice(self):    
        self.list.append(self.observable)
        del self.list[:]
        self.assertNotificationsAfterChange(0)

    def testRemove(self):
        self.list.append(self.observable)
        self.list.remove(self.observable)
        self.assertNotificationsAfterChange(0)
    
    def testInsert(self):
        self.list.insert(0, self.observable)    
        self.assertNotificationsAfterChange(1)
        

class ObservableObservablesListTest(ObservableTestCase):        
    def getObservable(self):
        return patterns.ObservableObservablesList()
        
    def setUp(self):
        super(ObservableObservablesListTest, self).setUp()
        self.observableItem = patterns.Observable()
        self.observable.append(self.observableItem)
        
    def check(self, addNotifications=0, removeNotifications=0, changeNotifications=0,
            lenObservable=0, addedItems=None, removedItems=None, changedItems=None):
        self.assertEqual(lenObservable, len(self.observable))
        self.assertEqual(addNotifications, self.addNotifications)
        self.assertEqual(removeNotifications, self.removeNotifications)
        self.assertEqual(changeNotifications, self.changeNotifications)
        self.assertEqual(addedItems, self.addedItems)
        self.assertEqual(removedItems, self.removedItems)
        self.assertEqual(changedItems, self.changedItems)
        
    def testAppend(self):
        self.check(addNotifications=1, lenObservable=1, addedItems=[self.observableItem])
        
    def testRemove(self):
        self.observable.remove(self.observableItem)
        self.check(addNotifications=1, removeNotifications=1, lenObservable=0, 
            addedItems=[self.observableItem], removedItems=[self.observableItem])
        
    def testChangeObservableItem(self):
        self.observableItem.notifyObservers(patterns.observer.Notification(self.observableItem))
        self.check(addNotifications=1, changeNotifications=1, lenObservable=1, 
            addedItems=[self.observableItem], changedItems=[self.observableItem])
        

class ObservableListTest(ObservableTestCase):
    def getObservable(self):
        return patterns.ObservableList([0])
        
    def check(self, addNotifications=0, removeNotifications=0, lenObservable=0, 
            addedItems=None, removedItems=None):
        self.assertEqual(lenObservable, len(self.observable))
        self.assertEqual(addNotifications, self.addNotifications)
        self.assertEqual(removeNotifications, self.removeNotifications)
        self.assertEqual(addedItems, self.addedItems)
        self.assertEqual(removedItems, self.removedItems)
                
    def testAppend(self):
        self.observable.append(1)
        self.check(addNotifications=1, lenObservable=2, addedItems=[1])
        
    def testExtend(self):
        self.observable.extend([1,2,3])
        self.check(addNotifications=1, lenObservable=4, addedItems=[1,2,3])
        
    def testExtend_WithEmptyList(self):
        self.observable.extend([])
        self.check(lenObservable=1)

    def testInsert(self):
        self.observable.insert(0, 1)
        self.check(addNotifications=1, lenObservable=2, addedItems=[1])        

    def testDeleteItem(self):
        del self.observable[0]
        self.check(removeNotifications=1, lenObservable=0, removedItems=[0])
 
    def testDeleteSlice(self):
        del self.observable[:]
        self.check(removeNotifications=1, lenObservable=0, removedItems=[0])
        
    def testRemove(self):
        self.observable.remove(0)
        self.check(removeNotifications=1, lenObservable=0, removedItems=[0])
    
    def testRemoveObserver(self):
        self.observable.removeObserver(self.onNotify)
        self.observable.remove(0)
        self.check(lenObservable=0)

    
class ObservableListObserverTest(ObservableTestCase):
    def getObservable(self):
        return patterns.ObservableListObserver(patterns.ObservableObservablesList([patterns.Observable()]))

    def setUp(self):
        super(ObservableListObserverTest, self).setUp()
        self.observableItem = patterns.Observable()
        
    def check(self, addNotifications=0, removeNotifications=0, lenOriginal=0):
        self.assertEqual(lenOriginal, len(self.observable.original()))
        self.assertEqual(lenOriginal, len(self.observable))
        self.assertEqual(addNotifications, self.addNotifications)
        self.assertEqual(removeNotifications, self.removeNotifications)

    def testAppend(self):
        self.observable.append(self.observableItem)
        self.check(addNotifications=1, lenOriginal=2)
        
    def testExtend(self):
        self.observable.extend([self.observableItem, patterns.Observable()])
        self.check(addNotifications=1, lenOriginal=3)

    def testExtend_WithEmptyList(self):
        self.observable.extend([])
        self.check(lenOriginal=1)

    def testDeleteItem(self):
        del self.observable[0]
        self.check(removeNotifications=1, lenOriginal=0)

    def testDeleteSlice(self):
        del self.observable[:]
        self.check(removeNotifications=1, lenOriginal=0)

    def testRemove(self):
        self.observable.append(self.observableItem)
        self.observable.remove(self.observableItem)
        self.check(removeNotifications=1, addNotifications=1, lenOriginal=1)

    def testInsert(self):
        self.observable.insert(0, self.observableItem)
        self.check(addNotifications=1, lenOriginal=2)
        
    def testRemoveItems(self):
        self.observable.append(self.observableItem)
        self.observable.removeItems([self.observableItem])
        self.check(addNotifications=1, removeNotifications=1, lenOriginal=1)


class NotificationTest(test.TestCase):
    def setUp(self):
        self.notification = patterns.observer.Notification(self)
        
    def testSource(self):
        self.assertEqual(self, self.notification.source)
        
    def testSetItem(self):
        self.notification['test'] = 'Test'
        self.assertEqual('Test', self.notification.test)
        
    def testStr(self):
        self.failUnless(str(self.notification).startswith('Notification'))
        
    def testSetAttribute(self):
        self.notification.source = 'Test'
        self.assertEqual('Test', self.notification.source)
        
