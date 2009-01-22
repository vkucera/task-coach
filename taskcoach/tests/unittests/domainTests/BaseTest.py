# -*- coding: utf-8 -*-

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

import wx
import test
from taskcoachlib import patterns
from taskcoachlib.domain import base, date


class SynchronizedObjectTest(test.TestCase):
    def setUp(self):
        self.object = base.SynchronizedObject()
        self.events = []
        
    def onEvent(self, event):
        self.events.append(event)
        
    def registerObserver(self, eventType):
        patterns.Publisher().registerObserver(self.onEvent, eventType)
        
    def assertObjectStatus(self, expectedStatus):
        self.assertEqual(expectedStatus, self.object.getStatus())
        
    def assertOneEventReceived(self, eventSource, eventType, *values):
        self.assertEqual([patterns.Event(eventSource, eventType, *values)], 
                         self.events)
    
    def testInitialStatus(self):
        self.assertObjectStatus(base.SynchronizedObject.STATUS_NEW)
                         
    def testMarkDeleted(self):
        self.object.markDeleted()
        self.assertObjectStatus(base.SynchronizedObject.STATUS_DELETED)
                         
    def testMarkDeletedNotification(self):
        self.registerObserver(self.object.markDeletedEventType())
        self.object.markDeleted()
        self.assertOneEventReceived(self.object,
            self.object.markDeletedEventType(), self.object.getStatus())
    
    def testMarkNewObjectAsNotDeleted(self):
        self.object.cleanDirty()
        self.assertObjectStatus(base.SynchronizedObject.STATUS_NONE)
    
    def testMarkDeletedObjectAsUndeleted(self):
        self.object.markDeleted()
        self.object.cleanDirty()
        self.assertObjectStatus(base.SynchronizedObject.STATUS_NONE) 

    def testMarkNotDeletedNotification(self):
        self.object.markDeleted()
        self.registerObserver(self.object.markNotDeletedEventType())
        self.object.cleanDirty()
        self.assertOneEventReceived(self.object, 
            self.object.markNotDeletedEventType(), self.object.getStatus()) 

    def testSetStateToDeletedCausesNotification(self):
        self.object.markDeleted()
        state = self.object.__getstate__()
        self.object.cleanDirty()
        self.registerObserver(self.object.markDeletedEventType())
        self.object.__setstate__(state)                
        self.assertOneEventReceived(self.object, 
            self.object.markDeletedEventType())

    def testSetStateToNotDeletedCausesNotification(self):
        state = self.object.__getstate__()
        self.object.markDeleted()
        self.registerObserver(self.object.markNotDeletedEventType())
        self.object.__setstate__(state)                
        self.assertOneEventReceived(self.object, 
            self.object.markNotDeletedEventType())
                    
                    
class ObjectSubclass(base.Object):
    pass


class ObjectTest(test.TestCase):
    def setUp(self):
        self.object = base.Object()
        self.subclassObject = ObjectSubclass()
        self.eventsReceived = []
        for eventType in (self.object.subjectChangedEventType(), 
                          self.object.descriptionChangedEventType(),
                          self.object.colorChangedEventType()):
            patterns.Publisher().registerObserver(self.onEvent, eventType)

    def onEvent(self, event):
        self.eventsReceived.append(event)

    # Id tests:
        
    def testSetIdOnCreation(self):
        object = base.Object(id='123')
        self.assertEqual('123', object.id())
        
    def testIdIsAString(self):
        self.assertEqual(type(''), type(self.object.id()))
        
    def testDifferentObjectsHaveDifferentIds(self):
        self.assertNotEqual(base.Object().id(), self.object.id())
        
    def testCopyHasDifferentId(self):
        objectId = self.object.id() # Force generation of id
        copy = self.object.copy()
        self.assertNotEqual(copy.id(), objectId)
                
    # Subject tests:
        
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
    
    # Description tests:
    
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
            
    # State tests:
    
    def testGetState(self):
        self.assertEqual(dict(subject='', description='', id=self.object.id(),
                              status=self.object.getStatus(),
                              color=None), 
                         self.object.__getstate__())

    def testSetState(self):
        newState = dict(subject='New', description='New', id=None,
                        status=42,
                        color=wx.RED)
        self.object.__setstate__(newState)
        self.assertEqual(newState, self.object.__getstate__())
    
    # Copy tests:
        
    def testCopy_SubjectIsCopied(self):
        self.object.setSubject('New subject')
        copy = self.object.copy()
        self.assertEqual(copy.subject(), self.object.subject())

    def testCopy_DescriptionIsCopied(self):
        self.object.setDescription('New description')
        copy = self.object.copy()
        self.assertEqual(copy.description(), self.object.description())

    def testCopy_ColorIsCopied(self):
        self.object.setColor(wx.RED)
        copy = self.object.copy()
        self.assertEqual(copy.color(), self.object.color())
        
    def testCopy_ShouldUseSubclassForCopy(self):
        copy = self.subclassObject.copy()
        self.assertEqual(copy.__class__, self.subclassObject.__class__)

    # Color tests
    
    def testDefaultColor(self):
        self.assertEqual(None, self.object.color())
    
    def testSetColor(self):
        self.object.setColor(wx.RED)
        self.assertEqual(wx.RED, self.object.color())

    def testSetColorWithTupleColor(self):
        self.object.setColor((255, 0, 0, 255))
        self.assertEqual(wx.RED, self.object.color())

    def testSetColorOnCreation(self):
        domainObject = base.Object(color=wx.GREEN)
        self.assertEqual(wx.GREEN, domainObject.color())
    
    def testColorChangedNotification(self):
        self.object.setColor(wx.BLACK)
        self.assertEqual(1, len(self.eventsReceived))

    # Event types:
    
    def testModificationEventTypes(self):
        self.assertEqual([self.object.subjectChangedEventType(),
                          self.object.descriptionChangedEventType(),
                          self.object.colorChangedEventType()], 
                         self.object.modificationEventTypes())


class CompositeObjectTest(test.TestCase):
    def setUp(self):
        self.compositeObject = base.CompositeObject()
        self.eventsReceived = []
        
    def onEvent(self, event):
        self.eventsReceived.append(event)
        
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
        compositeObject = base.CompositeObject(expandedContexts=['None'])
        self.failUnless(compositeObject.isExpanded())

    def testSetExpansionStatesViaConstructor(self):
        compositeObject = base.CompositeObject(expandedContexts=['context1',
            'context2'])
        self.assertEqual(['context1', 'context2'],
                         sorted(compositeObject.expandedContexts()))

    def testExpandInContext_DoesNotChangeExpansionStateInDefaultContext(self):
        self.compositeObject.expand(context='some_viewer')
        self.failIf(self.compositeObject.isExpanded())

    def testExpandInContext_DoesChangeExpansionStateInGivenContext(self):
        self.compositeObject.expand(context='some_viewer')
        self.failUnless(self.compositeObject.isExpanded(context='some_viewer'))

    def testIsExpandedInUnknownContext_ReturnsFalse(self):
        self.failIf(self.compositeObject.isExpanded(context='whatever'))

    def testGetContextsWhereExpanded(self):
        self.assertEqual([], self.compositeObject.expandedContexts())
        
    def testRecursiveSubject(self):
        self.compositeObject.setSubject('parent')
        child = base.CompositeObject(subject='child')
        self.compositeObject.addChild(child)
        self.assertEqual(u'parent -> child', child.subject(recursive=True))

    def testSubItemUsesParentColor(self):
        child = base.CompositeObject()
        self.compositeObject.addChild(child)
        child.setParent(self.compositeObject)
        self.compositeObject.setColor(wx.RED)
        self.assertEqual(wx.RED, child.color())

    def testColorChangedNotification(self):
        child = base.CompositeObject()
        self.compositeObject.addChild(child)
        child.setParent(self.compositeObject)
        patterns.Publisher().registerObserver(self.onEvent,
            eventType=base.CompositeObject.colorChangedEventType())
        self.compositeObject.setColor(wx.RED)
        self.assertEqual(2, len(self.eventsReceived))

    def testCopy(self):
        self.compositeObject.expand(context='some_viewer')
        copy = self.compositeObject.copy()
        self.assertEqual(copy.expandedContexts(),
                         self.compositeObject.expandedContexts())
        self.compositeObject.expand(context='another_viewer')
        self.failIf('another_viewer' in copy.expandedContexts())

    def testModificationEventTypes(self):
        self.assertEqual([self.compositeObject.addChildEventType(),
                          self.compositeObject.removeChildEventType(),
                          self.compositeObject.subjectChangedEventType(),
                          self.compositeObject.descriptionChangedEventType(),
                          self.compositeObject.colorChangedEventType(),
                          self.compositeObject.expansionChangedEventType()], 
                         self.compositeObject.modificationEventTypes())


class BaseCollectionTest(test.TestCase):
    def setUp(self):
        self.collection = base.Collection()
        
    def testLookupByIdWhenCollectionIsEmptyRaisesIndexError(self):
        try:
            self.collection.getObjectById('id')
            self.fail()
        except IndexError:
            pass
        
    def testLookupIdWhenObjectIsInCollection(self):
        object = base.CompositeObject()
        self.collection.append(object)
        self.assertEqual(object, self.collection.getObjectById(object.id()))
