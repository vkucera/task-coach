import test, patterns

class ObservableTestCase(test.TestCase):
    def setUp(self):
        super(ObservableTestCase, self).setUp()
        self.addNotifications = self.removeNotifications = self.changeNotifications = 0
        self.addedItems = self.removedItems = self.changedItems = None
        self.observable = self.getObservable()

    def notifyAdd(self, items, *args, **kwargs):
        self.addNotifications += 1
        self.addedItems = items
        
    def notifyRemove(self, items, *args, **kwargs):
        self.removeNotifications += 1
        self.removedItems = items

    def notifyChange(self, items, *args, **kwargs):
        self.changeNotifications += 1
        self.changedItems = items
        

class ObservableTest(ObservableTestCase):
    def getObservable(self):
        return patterns.Observable()

    def setUp(self):
        super(ObservableTest, self).setUp()
        self.observable.registerObserver(self.notifyChange)

    def check(self, notifications):
        self.assertEqual(notifications, self.changeNotifications)
        
    def testNoNotificationOnRegistration(self):
        self.check(notifications=0)

    def testNotificationOnChange(self):
        self.observable._notifyObserversOfChange()
        self.check(notifications=1)

    def testRemoveObserver(self):
        self.observable.removeObserver(self.notifyChange)
        self.observable._notifyObserversOfChange()
        self.check(notifications=0)


class MockObservablesList(patterns.ObservablesList):
    def __init__(self, *args, **kwargs):
        super(MockObservablesList, self).__init__(*args, **kwargs)
        self.notifications = 0
        
    def notifyChange(self, *args):
        self.notifications += 1

        
class ObservablesListTest(test.TestCase):
    def setUp(self):
        self.list = MockObservablesList()
        self.observable = patterns.Observable()
    
    def assertNotificationsAfterChange(self, notifications):
        self.observable._notifyObserversOfChange()
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
        self.observable.registerObserver(self.notifyAdd, self.notifyRemove, self.notifyChange)

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
        self.observable.append(self.observableItem)
        self.check(addNotifications=1, lenObservable=1, addedItems=[self.observableItem])
        
    def testRemove(self):
        self.observable.append(self.observableItem)
        self.observable.remove(self.observableItem)
        self.check(addNotifications=1, removeNotifications=1, lenObservable=0, 
            addedItems=[self.observableItem], removedItems=[self.observableItem])
        
    def testChangeObservableItem(self):
        self.observable.append(self.observableItem)
        self.observableItem._notifyObserversOfChange()
        self.check(addNotifications=1, changeNotifications=1, lenObservable=1, 
            addedItems=[self.observableItem], changedItems=[self.observableItem])
        

class ObservableListTest(ObservableTestCase):
    def getObservable(self):
        return patterns.ObservableList([0])
        
    def setUp(self):
        super(ObservableListTest, self).setUp()
        self.observable.registerObserver(self.notifyAdd, self.notifyRemove)
        
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
        self.observable.removeObserver(self.notifyAdd, self.notifyRemove)
        self.observable.remove(0)
        self.check(lenObservable=0)

    
class ObservableListObserverTest(ObservableTestCase):
    def getObservable(self):
        return patterns.ObservableListObserver(patterns.ObservableObservablesList([patterns.Observable()]))

    def setUp(self):
        super(ObservableListObserverTest, self).setUp()
        self.observableItem = patterns.Observable()
        self.observable.registerObserver(self.notifyAdd, self.notifyRemove, self.notifyChange)
        
    def check(self, addNotifications=0, removeNotifications=0, lenOriginal=0):
        self.assertEqual(lenOriginal, len(self.observable.original()))
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
    def testSource(self):
        notification = patterns.observer.Notification(self)
        self.assertEqual(self, notification.source)