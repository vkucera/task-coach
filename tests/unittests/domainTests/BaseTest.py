import test, patterns
from domain import base

class ObjectSubclass(base.Object):
    pass


class ObjectTest(test.TestCase):
    def setUp(self):
        self.object = base.Object()
        self.subclassObject = ObjectSubclass()
        self.eventsReceived = []
        for eventType in (self.object.subjectChangedEventType(), 
                          self.object.descriptionChangedEventType()):
            patterns.Publisher().registerObserver(self.onEvent, eventType)

    def onEvent(self, event):
        self.eventsReceived.append(event)
        
    def testSubjectIsEmptyByDefault(self):
        self.assertEqual('', self.object.subject())
        
    def testSetSubjectOnCreation(self):
        domainObject = base.Object(subject='Hi')
        self.assertEqual('Hi', domainObject.subject())
        
    def testSetSubject(self):
        self.object.setSubject('New subject')
        self.assertEqual('New subject', self.object.subject())
        
    def testSetSubjectCausesNotification(self):
        self.object.setSubject('New subject')
        self.assertEqual(patterns.Event(self.object, 
            self.object.subjectChangedEventType(), 'New subject'), 
            self.eventsReceived[0])
        
    def testSetSubjectUnchangedDoesNotCauseNotification(self):
        self.object.setSubject('')
        self.failIf(self.eventsReceived)
        
    def testSubjectChangedNotificationIsDifferentForSubclass(self):
        self.subclassObject.setSubject('New')
        self.failIf(self.eventsReceived)
        
    def testDescriptionIsEmptyByDefault(self):
        self.failIf(self.object.description())
        
    def testSetDescriptionOnCreation(self):
        domainObject = base.Object(description='Hi')
        self.assertEqual('Hi', domainObject.description())
        
    def testSetDescription(self):
        self.object.setDescription('New description')
        self.assertEqual('New description', self.object.description())
        
    def testSetDescriptionCausesNotification(self):
        self.object.setDescription('New description')
        self.assertEqual(patterns.Event(self.object, 
            self.object.descriptionChangedEventType(), 'New description'), 
            self.eventsReceived[0])

    def testSetDescriptionUnchangedDoesNotCauseNotification(self):
        self.object.setDescription('')
        self.failIf(self.eventsReceived)

    def testDescriptionChangedNotificationIsDifferentForSubclass(self):
        self.subclassObject.setDescription('New')
        self.failIf(self.eventsReceived)
        
    def testGetState(self):
        self.assertEqual(dict(subject='', description=''), 
                         self.object.__getstate__())

    def testSetState(self):
        newState = dict(subject='New', description='New')
        self.object.__setstate__(newState)
        self.assertEqual(newState, self.object.__getstate__())
        
    def testCopy_SubjectIsCopied(self):
        self.object.setSubject('New subject')
        copy = self.object.copy()
        self.assertEqual(copy.subject(), self.object.subject())

    def testCopy_DescriptionIsCopied(self):
        self.object.setDescription('New description')
        copy = self.object.copy()
        self.assertEqual(copy.description(), self.object.description())
        
    def testCopy_ShouldUseSubclassForCopy(self):
        copy = self.subclassObject.copy()
        self.assertEqual(copy.__class__, self.subclassObject.__class__)
        
        
class CompositeObjectTest(test.TestCase):
    def setUp(self):
        self.compositeObject = base.CompositeObject()
        
    def testIsExpanded(self):
        self.failIf(self.compositeObject.isExpanded())
        
    def testExpand(self):
        self.compositeObject.expand()
        self.failUnless(self.compositeObject.isExpanded())
        
    def testCollapse(self):
        self.compositeObject.expand()
        self.compositeObject.expand(False)
        self.failIf(self.compositeObject.isExpanded())
        
    def testSetExpansionStateViaConstructor(self):
        compositeObject = base.CompositeObject(expand=True)
        self.failUnless(compositeObject.isExpanded())
        
