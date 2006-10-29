import test, patterns

class CompositeTest(test.TestCase):
    def setUp(self):
        self.composite = patterns.Composite()
        self.child = patterns.Composite()
        
    def testNoParentByDefault(self):
        self.failIf(self.composite.parent())
        
    def testNoChildrenByDefault(self):
        self.failIf(self.composite.children())
        
    def testNoRecursiveChildrenByDefault(self):
        self.failIf(self.composite.children(recursive=True))
    
    def testNoAncestorsByDefault(self):
        self.assertEqual([], self.composite.ancestors())
        
    def testAddChild(self):
        self.composite.addChild(self.child)
        self.assertEqual([self.child], self.composite.children())
        
    def testAddChild_SetsParentOfChild(self):
        self.composite.addChild(self.child)
        self.assertEqual(self.composite, self.child.parent())
        
    def testRemoveChild(self):
        self.composite.addChild(self.child)
        self.composite.removeChild(self.child)
        self.assertEqual([], self.composite.children())
        
    def testRemoveChild_DoesNotResetParentOfChild(self):
        self.composite.addChild(self.child)
        self.composite.removeChild(self.child)
        self.assertEqual(self.composite, self.child.parent())
    
    def testCreateWithChildren(self):
        objectWithChildren = patterns.Composite(children=[self.child])
        self.assertEqual([self.child], objectWithChildren.children())
        
    def testCreateWithParent(self):
        objectWithParent = patterns.Composite(parent=self.composite)
        self.assertEqual(self.composite, objectWithParent.parent())
        
    def testCreateWithParentDoesNotAddObjectToParent(self):
        objectWithParent = patterns.Composite(parent=self.composite)
        self.failIf(self.composite.children())
        
    def testChildrenRecursive_WithoutGrandChildren(self):
        self.composite.addChild(self.child)
        self.assertEqual([self.child], 
                         self.composite.children(recursive=True))

    def testChildrenRecursive(self):
        self.composite.addChild(self.child)
        grandChild = patterns.Composite()
        self.child.addChild(grandChild)
        self.assertEqual([self.child, grandChild], 
                         self.composite.children(recursive=True))
        
    def testAncestorsWithTwoGenerations(self):
        self.composite.addChild(self.child)
        self.assertEqual([self.composite], self.child.ancestors())
        
    def testAncestorsWithThreeGenerations(self):
        grandChild = patterns.Composite()
        self.composite.addChild(self.child)
        self.child.addChild(grandChild)
        self.assertEqual([self.composite, self.child], grandChild.ancestors())
        
    def testCompositeIsItsOnlyFamilyByDefault(self):
        self.assertEqual([self.composite], self.composite.family())
        
    def testParentIsPartOfFamily(self):
        self.composite.addChild(self.child)
        self.assertEqual([self.composite, self.child], self.child.family())
        
    def testChildIsPartOfFamily(self):
        self.composite.addChild(self.child)
        self.assertEqual([self.composite, self.child], self.composite.family())
        
    def testNewChild_HasCorrectParent(self):
        child = self.composite.newChild()
        self.assertEqual(self.composite, child.parent())
        
    def testNewChild_NotInParentsChildren(self):
        child = self.composite.newChild()
        self.failIf(child in self.composite.children())
        
    def testGetState(self):
        self.assertEqual(dict(children=[], parent=None), 
                         self.composite.__getstate__())
        
    def testGetState_WithChildren(self):
        self.composite.addChild(self.child)
        self.assertEqual(dict(children=[self.child], parent=None), 
                         self.composite.__getstate__())
        
    def testGetState_WithParent(self):
        self.composite.addChild(self.child)
        self.assertEqual(dict(children=[], parent=self.composite),
                         self.child.__getstate__())
                
    def testSetState_Parent(self):
        state = self.composite.__getstate__()
        self.composite.setParent(self.child)
        self.composite.__setstate__(state)
        self.assertEqual(None, self.composite.parent())
        
    def testSetState_Children(self):
        state = self.composite.__getstate__()
        self.composite.addChild(self.child)
        self.composite.__setstate__(state)
        self.assertEqual([], self.composite.children())
        
    def testCopy(self):
        copy = self.composite.copy()
        self.assertEqual(copy.children(), self.composite.children())
        
    def testCopy_AddChildrenAfterCopy(self):
        copy = self.composite.copy()
        self.composite.addChild(self.child)
        self.failIf(self.child in copy.children())
        
    def testCopy_WithChildren(self):
        self.composite.addChild(self.child)
        copy = self.composite.copy()
        self.assertEqual(1, len(copy.children()))
    
    def testCopy_WithChildren_ParentOfCopiedChildrenIsNewComposite(self):
        self.composite.addChild(self.child)
        copy = self.composite.copy()
        self.assertEqual(copy, copy.children()[0].parent())
    
    def testCopy_WithParent(self):
        self.composite.addChild(self.child)
        copy = self.child.copy()
        self.assertEqual(self.child.parent(), copy.parent())
        
    def testCopy_WithChildren_DoesNotCreateExtraChildrenForOriginal(self):
        self.composite.addChild(self.child)
        copy = self.composite.copy()
        self.assertEqual(1, len(self.composite.children()))

        
class ObservableCompositeTest(test.TestCase):
    def setUp(self):
        self.events = []
        self.composite = patterns.ObservableComposite()
        self.child = patterns.ObservableComposite()
        
    def registerObserver(self, eventType):
        patterns.Publisher().registerObserver(self.onEvent, eventType)    
            
    def onEvent(self, event):
        self.events.append(event)
        
    def testAddChild(self):
        eventType = self.composite.addChildEventType()
        self.registerObserver(eventType)    
        self.composite.addChild(self.child)
        self.assertEqual([patterns.Event(self.composite, eventType, 
            self.child)], self.events)
            
    def testRemoveChild(self):
        eventType = self.composite.removeChildEventType()
        self.registerObserver(eventType)    
        self.composite.addChild(self.child)
        self.composite.removeChild(self.child)
        self.assertEqual([patterns.Event(self.composite, eventType, 
            self.child)], self.events)

            
class CompositeCollectionTest(test.TestCase):
    def setUp(self):
        self.composite = patterns.ObservableComposite()
        self.composite2 = patterns.ObservableComposite()
        self.collection = patterns.CompositeList()
        self.events = []
        
    def onEvent(self, event):
        self.events.append(event)
        
    def registerObserver(self, eventType):
        patterns.Publisher().registerObserver(self.onEvent, eventType)
        
    def testInitialSize(self):
        self.assertEqual(0, len(self.collection))
        
    def testCreateWithInitialContent(self):
        collection = patterns.CompositeList([self.composite])
        self.assertEqual([self.composite], collection)

    def testRootItems_NoItems(self):
        self.assertEqual([], self.collection.rootItems())
        
    def testRootItems_OneRootItem(self):
        self.collection.append(self.composite)
        self.assertEqual([self.composite], self.collection.rootItems())
        
    def testRootItems_MultipleRootItems(self):
        self.collection.extend([self.composite, self.composite2])
        self.assertEqualLists([self.composite, self.composite2], 
                         self.collection.rootItems())
        
    def testRootItems_RootAndChildItems(self):
        self.composite.addChild(self.composite2)
        self.collection.extend([self.composite, self.composite2])
        self.assertEqual([self.composite], self.collection.rootItems())
        
    def testAddChild(self):
        self.collection.extend([self.composite, self.composite2])
        self.composite.addChild(self.composite2)
        self.assertEqual([self.composite], self.collection.rootItems())
    
    def testAddRootWithChildItems(self):
        self.composite.addChild(self.composite2)
        self.collection.append(self.composite)
        self.assertEqualLists([self.composite, self.composite2], 
                              self.collection)
        
    def testAddRootWithChildItems_AddAllAtOnce(self):
        self.composite.addChild(self.composite2)
        self.collection.extend([self.composite, self.composite2])
        self.assertEqualLists([self.composite, self.composite2], 
                              self.collection)

    def testAddRootWithChildItems_DoesNotAddChildToParent(self):
        self.composite.addChild(self.composite2)
        self.collection.extend([self.composite, self.composite2])
        self.assertEqual([self.composite2], self.composite.children())
        
    def testAddCompositeWithParentAddsItToParent(self):
        self.collection.append(self.composite)
        self.composite2.setParent(self.composite)
        self.collection.append(self.composite2)
        self.assertEqual([self.composite2], self.composite.children())

    def testAddCompositeWithParentTriggersNotificationByParent(self):
        self.registerObserver(self.composite.addChildEventType())
        self.collection.append(self.composite)
        self.composite2.setParent(self.composite)
        self.collection.append(self.composite2)
        self.assertEqual([patterns.Event(self.composite, 
            self.composite.addChildEventType(), self.composite2)], self.events)
    
    def testRemoveChildFromCollectionRemovesChildFromParent(self):
        self.collection.extend([self.composite, self.composite2])
        self.composite.addChild(self.composite2)
        self.collection.remove(self.composite2)
        self.failIf(self.composite.children())
        
    def testRemoveChildFromCollectionTriggersNotificationByParent(self):
        self.registerObserver(self.composite.removeChildEventType())
        self.collection.extend([self.composite, self.composite2])
        self.composite.addChild(self.composite2)
        self.collection.remove(self.composite2)
        self.assertEqual([patterns.Event(self.composite, 
            self.composite.removeChildEventType(), self.composite2)], 
            self.events)

    def testRemoveCompositeWithChildRemovesChildToo(self):
        self.composite.addChild(self.composite2)
        grandChild = patterns.ObservableComposite()
        self.composite2.addChild(grandChild)
        self.collection.append(self.composite)
        self.collection.remove(self.composite2)
        self.assertEqual([self.composite], self.collection)

    def testRemoveCompositeAndChildRemovesBoth(self):
        self.composite.addChild(self.composite2)
        grandChild = patterns.ObservableComposite()
        self.composite2.addChild(grandChild)
        self.collection.append(self.composite)
        self.collection.removeItems([self.composite2, grandChild])
        self.assertEqual([self.composite], self.collection)
        
    def testRemoveChildWithChildren_CollectionNotificationContainsParentAndChild(self):
        self.registerObserver(self.collection.removeItemEventType())
        self.composite.addChild(self.composite2)
        grandChild = patterns.ObservableComposite()
        self.composite2.addChild(grandChild)
        self.collection.append(self.composite)
        self.collection.remove(self.composite2)
        self.assertEqualLists([self.composite2, grandChild],
                              self.events[0].values())
    
    def testRemoveCompositeWithChildrenDoesNotBreakParentChildRelation(self):
        self.composite.addChild(self.composite2)
        self.collection.append(self.composite)
        self.collection.remove(self.composite)
        self.assertEqual([self.composite2], self.composite.children())
        
    def testRemoveChildAndThenAddingItAddsItToPreviousParentToo(self):
        self.composite.addChild(self.composite2)
        self.collection.append(self.composite)
        self.collection.remove(self.composite2)
        self.collection.append(self.composite2)
        self.assertEqual([self.composite2], self.composite.children())
        
    def testRemoveCompositeNotInCollection(self):
        self.collection.remove(self.composite)
        
        
