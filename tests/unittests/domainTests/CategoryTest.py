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

import test, wx
from taskcoachlib import patterns
from taskcoachlib.domain import category, categorizable, note


class CategorizableCompositeObjectTest(test.TestCase):
    def setUp(self):
        self.categorizable = categorizable.CategorizableCompositeObject(subject='categorizable')
        self.category = category.Category('category')
        
    categoryAddedEventType = categorizable.CategorizableCompositeObject.categoryAddedEventType()
    categoryRemovedEventType = categorizable.CategorizableCompositeObject.categoryRemovedEventType()
    totalCategoryAddedEventType = categorizable.CategorizableCompositeObject.totalCategoryAddedEventType()
    totalCategoryRemovedEventType = categorizable.CategorizableCompositeObject.totalCategoryRemovedEventType()
    categorySubjectChangedEventType = categorizable.CategorizableCompositeObject.categorySubjectChangedEventType()
    totalCategorySubjectChangedEventType = categorizable.CategorizableCompositeObject.totalCategorySubjectChangedEventType()
    colorChangedEventType = categorizable.CategorizableCompositeObject.colorChangedEventType()
        
    def testCategorizableDoesNotBelongToAnyCategoryByDefault(self):
        for recursive in False, True:
            self.failIf(self.categorizable.categories(recursive=recursive))
    
    def testCategorizableHasNoColorByDefault(self):
        self.assertEqual(None, self.categorizable.color())
    
    def testAddCategory(self):
        self.categorizable.addCategory(self.category)
        self.assertEqual(set([self.category]), self.categorizable.categories())

    def testAddCategoryNotification(self):
        self.registerObserver(self.categoryAddedEventType)
        self.categorizable.addCategory(self.category)
        self.assertEqual([patterns.Event( \
            self.categoryAddedEventType, self.categorizable, self.category)], 
            self.events)    
        
    def testAddSecondCategory(self):
        self.categorizable.addCategory(self.category)
        cat2 = category.Category('category 2')
        self.categorizable.addCategory(cat2)
        self.assertEqual(set([self.category, cat2]), 
            self.categorizable.categories())
        
    def testAddSameCategoryTwice(self):
        self.categorizable.addCategory(self.category)
        self.categorizable.addCategory(self.category)
        self.assertEqual(set([self.category]), self.categorizable.categories())
        
    def testAddSameCategoryTwiceCausesNoNotification(self):
        self.categorizable.addCategory(self.category)
        self.registerObserver(self.categoryAddedEventType)
        self.categorizable.addCategory(self.category)
        self.failIf(self.events)
    
    def testAddCategoryViaConstructor(self):
        categorizableObject = categorizable.CategorizableCompositeObject(categories=[self.category])
        self.assertEqual(set([self.category]), categorizableObject.categories())
        
    def testAddCategoriesViaConstructor(self):
        anotherCategory = category.Category('Another category')
        categories = [self.category, anotherCategory]
        categorizableObject = categorizable.CategorizableCompositeObject(categories= \
            categories)
        self.assertEqual(set(categories), categorizableObject.categories())
        
    def testAddCategoryDoesNotAddCategorizableToCategory(self):
        self.categorizable.addCategory(self.category)
        self.assertEqual(set([]), self.category.categorizables())
        
    def testAddParentToCategory(self):
        self.registerObserver(self.totalCategoryAddedEventType)
        child = categorizable.CategorizableCompositeObject(subject='child')
        self.categorizable.addChild(child)
        child.setParent(self.categorizable)
        cat = category.Category(subject='Parent category')
        self.categorizable.addCategory(cat)
        self.assertEqual([patterns.Event(self.totalCategoryAddedEventType, 
            child, cat)], self.events)
        
    def testRemoveCategory(self):
        self.categorizable.addCategory(self.category)
        self.categorizable.removeCategory(self.category)
        self.assertEqual(set(), self.categorizable.categories())
        
    def testRemoveCategoryNotification(self):
        self.categorizable.addCategory(self.category)
        self.registerObserver(self.categoryRemovedEventType)
        self.categorizable.removeCategory(self.category)
        self.assertEqual(self.category, self.events[0].value())

    def testRemoveCategoryTwice(self):
        self.categorizable.addCategory(self.category)
        self.categorizable.removeCategory(self.category)
        self.categorizable.removeCategory(self.category)
        self.assertEqual(set(), self.categorizable.categories())

    def testRemoveCategoryTwiceNotification(self):
        self.categorizable.addCategory(self.category)
        self.registerObserver(self.categoryRemovedEventType)
        self.categorizable.removeCategory(self.category)
        self.categorizable.removeCategory(self.category)
        self.assertEqual(1, len(self.events))
        
    def testCategorySubjectChanged(self):
        self.registerObserver(self.categorySubjectChangedEventType)
        self.registerObserver(self.totalCategorySubjectChangedEventType)
        self.categorizable.addCategory(self.category)
        self.category.addCategorizable(self.categorizable)
        self.category.setSubject('New subject')
        expectedEvent = patterns.Event()
        expectedEvent.addSource(self.categorizable, 'New subject', type=self.categorySubjectChangedEventType)
        expectedEvent.addSource(self.categorizable, 'New subject', type=self.totalCategorySubjectChangedEventType)
        self.assertEqual([expectedEvent], self.events) 

    def testCategorySubjectChanged_NotifySubItemsToo(self):
        self.registerObserver(self.categorySubjectChangedEventType)
        self.registerObserver(self.totalCategorySubjectChangedEventType)
        childCategorizable = categorizable.CategorizableCompositeObject(subject='Child categorizable')
        self.categorizable.addChild(childCategorizable)
        self.categorizable.addCategory(self.category)
        self.category.addCategorizable(self.categorizable)
        self.category.setSubject('New subject')
        expectedEvent = patterns.Event()
        expectedEvent.addSource(self.categorizable, 'New subject', type=self.categorySubjectChangedEventType)
        expectedEvent.addSource(self.categorizable, 'New subject', type=self.totalCategorySubjectChangedEventType)
        expectedEvent.addSource(childCategorizable, 'New subject', type=self.totalCategorySubjectChangedEventType)
        self.assertEqual([expectedEvent], self.events) 

    def testColor(self):
        self.categorizable.addCategory(self.category)
        self.category.setColor(wx.RED)
        self.assertEqual(wx.RED, self.categorizable.color())

    def testCategorizableOwnColorOverridesCategoryColor(self):
        self.categorizable.addCategory(self.category)
        self.category.setColor(wx.RED)
        self.categorizable.setColor(wx.GREEN)
        self.assertEqual(wx.GREEN, self.categorizable.color())
        
    def testColorWithTupleColor(self):
        self.categorizable.addCategory(self.category)
        self.category.setColor((255, 0, 0, 255))
        self.assertEqual(wx.RED, self.categorizable.color())
    
    def testSubItemUsesParentColor(self):
        self.categorizable.addCategory(self.category)
        child = categorizable.CategorizableCompositeObject()
        self.categorizable.addChild(child)
        child.setParent(self.categorizable)
        self.category.setColor(wx.RED)
        self.assertEqual(wx.RED, child.color())
        
    def testSubItemDoesNotUseParentColorWhenItHasItsOwnColor(self):
        child = categorizable.CategorizableCompositeObject()
        self.categorizable.addChild(child)
        child.setParent(self.categorizable)
        child.addCategory(self.category)
        self.categorizable.setColor(wx.RED)
        self.category.setColor(wx.BLUE)
        self.assertEqual(wx.BLUE, child.color())
    
    def testColorChanged(self):
        self.categorizable.addCategory(self.category)
        self.category.addCategorizable(self.categorizable)
        self.registerObserver(self.colorChangedEventType)
        self.category.setColor(wx.RED)
        self.assertEqual(1, len(self.events))

    def testColorChanged_NotifySubItemsToo(self):
        self.registerObserver(self.colorChangedEventType)
        self.categorizable.addChild(categorizable.CategorizableCompositeObject())
        self.categorizable.addCategory(self.category)
        self.category.addCategorizable(self.categorizable)
        self.category.setColor(wx.RED)
        self.assertEqual(1, len(self.events))
        
    def testCategorizableDoesNotNotifyWhenItHasItsOwnColor(self):
        self.categorizable.addCategory(self.category)
        self.categorizable.setColor(wx.RED)
        self.registerObserver(self.categorizable.colorChangedEventType())
        self.category.setColor(wx.GREEN)
        self.assertEqual(0, len(self.events))
        
    def testParentColorChanged(self):
        self.registerObserver(self.colorChangedEventType)
        subCategory = category.Category('Subcategory')
        self.category.addChild(subCategory)
        subCategory.setParent(self.category)
        self.categorizable.addCategory(subCategory)
        subCategory.addCategorizable(self.categorizable)
        self.category.setColor(wx.RED)
        self.assertEqual(1, len(self.events))
        
    def testAddCategoryWithColor(self):
        self.registerObserver(self.colorChangedEventType)
        newCategory = category.Category('New category')
        newCategory.setColor(wx.RED)
        self.categorizable.addCategory(newCategory)
        self.assertEqual(1, len(self.events))
        
    def testAddCategoryWithParentWithColor(self):
        self.registerObserver(self.colorChangedEventType)
        parentCategory = category.Category('Parent')
        parentCategory.setColor(wx.RED)
        childCategory = category.Category('Child')
        parentCategory.addChild(childCategory)
        childCategory.setParent(parentCategory)
        self.categorizable.addCategory(childCategory)
        self.assertEqual(1, len(self.events))
        
    def testRemoveCategoryWithColor(self):
        self.categorizable.addCategory(self.category)
        self.category.setColor(wx.RED)
        self.registerObserver(self.colorChangedEventType)
        self.categorizable.removeCategory(self.category)
        self.assertEqual(1, len(self.events))
        
    def testColorWhenOneOutOfTwoCategoriesHasColor(self):
        self.categorizable.addCategory(self.category)
        self.categorizable.addCategory(category.Category('Another category'))
        self.category.setColor(wx.RED)
        self.assertEqual(wx.RED, self.categorizable.color())
        
    def testColorWhenBothCategoriesHaveSameColor(self):
        self.categorizable.addCategory(self.category)
        anotherCategory = category.Category('Another category')
        self.categorizable.addCategory(anotherCategory)
        for cat in [self.category, anotherCategory]:
            cat.setColor(wx.RED)
        self.assertEqual(wx.RED, self.categorizable.color())
                
    def testColorWhenBothCategoriesHaveDifferentColors(self):
        self.categorizable.addCategory(self.category)
        anotherCategory = category.Category('Another category')
        self.categorizable.addCategory(anotherCategory)
        self.category.setColor(wx.RED)
        anotherCategory.setColor(wx.BLUE)
        expectedColor = wx.Color(127, 0, 127, 255)
        self.assertEqual(expectedColor, self.categorizable.color())
                
    def testParentCategoryIncludedInChildRecursiveCategories(self):
        self.categorizable.addCategory(self.category)
        child = categorizable.CategorizableCompositeObject()
        self.categorizable.addChild(child)
        self.assertEqual(set([self.category]), child.categories(recursive=True))

    def testParentCategoryNotIncludedInChildCategories(self):
        self.categorizable.addCategory(self.category)
        child = categorizable.CategorizableCompositeObject()
        self.categorizable.addChild(child)
        self.assertEqual(set(), child.categories(recursive=False))
        
    def testGrandParentCategoryIncludedInGrandChildRecursiveCategories(self):
        self.categorizable.addCategory(self.category)
        child = categorizable.CategorizableCompositeObject()
        self.categorizable.addChild(child)
        grandchild = categorizable.CategorizableCompositeObject()
        child.addChild(grandchild)
        self.assertEqual(set([self.category]), 
                         grandchild.categories(recursive=True))
        
    def testGrandParentAndParentCategoriesIncludedInGrandChildRecursiveCategories(self):
        self.categorizable.addCategory(self.category)
        child = categorizable.CategorizableCompositeObject()
        self.categorizable.addChild(child)
        grandchild = categorizable.CategorizableCompositeObject()
        child.addChild(grandchild)
        childCategory = category.Category('Child category')
        child.addCategory(childCategory)
        self.assertEqual(set([self.category, childCategory]), 
            grandchild.categories(recursive=True))
        
    def testRemoveCategoryCausesChildNotification(self):
        self.categorizable.addCategory(self.category)
        child = categorizable.CategorizableCompositeObject()
        self.categorizable.addChild(child)
        self.registerObserver(self.totalCategoryRemovedEventType)
        self.categorizable.removeCategory(self.category)
        self.assertEqual([patterns.Event( \
            self.totalCategoryRemovedEventType, child, self.category)], 
            self.events)

    def testCopy(self):
        self.categorizable.addCategory(self.category)
        copy = self.categorizable.copy()
        self.assertEqual(copy.categories(), self.categorizable.categories()) # pylint: disable-msg=E1101
        
    def testModificationEventTypes(self): # pylint: disable-msg=E1003
        self.assertEqual(super(categorizable.CategorizableCompositeObject,
                               self.categorizable).modificationEventTypes() + \
                         [self.categoryAddedEventType, 
                          self.categoryRemovedEventType],
                         self.categorizable.modificationEventTypes())


class CategoryTest(test.TestCase):
    def setUp(self):
        self.category = category.Category(subject='category')
        self.subCategory = category.Category(subject='subcategory')
        self.categorizable = categorizable.CategorizableCompositeObject(subject='parent')
        self.child = categorizable.CategorizableCompositeObject(subject='child')
        
    def testGetState_Subject(self):
        self.assertEqual('category', self.category.__getstate__()['subject'])
        
    def testGetState_Description(self):
        self.assertEqual('', self.category.__getstate__()['description'])
        
    def testGetState_Color(self):
        self.assertEqual(None, self.category.__getstate__()['color'])
        
    def testSetState_OneNotification(self):
        newState = dict(subject='New subject', description='New description',
                        color=wx.RED, status=self.category.STATUS_DELETED,
                        parent=None, children=[self.subCategory], id=self.category.id(),
                        categorizables=[self.categorizable], notes=[],
                        attachments=[], filtered=True)
        for eventType in self.category.modificationEventTypes():
            self.registerObserver(eventType)
        self.category.__setstate__(newState)
        self.assertEqual(1, len(self.events))
        
    def testCreateWithSubject(self):
        self.assertEqual('category', self.category.subject())
    
    def testSetSubject(self):
        self.category.setSubject('New')
        self.assertEqual('New', self.category.subject())
        
    def testSetSubjectNotification(self):
        eventType = category.Category.subjectChangedEventType()
        self.registerObserver(eventType)
        self.category.setSubject('New')
        self.assertEqual([patterns.Event(eventType, self.category, 'New')], 
            self.events)
        
    def testSetSubjectCausesNoNotificationWhenNewSubjectEqualsOldSubject(self):
        eventType = category.Category.subjectChangedEventType()
        self.registerObserver(eventType)
        self.category.setSubject(self.category.subject())
        self.failIf(self.events)
        
    def testCreateWithDescription(self):
        aCategory = category.Category('subject', description='Description')
        self.assertEqual('Description', aCategory.description())

    def testNoCategorizablesAfterCreation(self):
        self.assertEqual(set(), self.category.categorizables())
      
    def testAddCategorizable(self):
        self.category.addCategorizable(self.categorizable)
        self.assertEqual(set([self.categorizable]), self.category.categorizables())
        
    def testAddCategorizableDoesNotAddCategoryToCategorizable(self):
        self.category.addCategorizable(self.categorizable)
        self.assertEqual(set([]), self.categorizable.categories())
        
    def testAddCategorizableTwice(self):
        self.category.addCategorizable(self.categorizable)
        self.category.addCategorizable(self.categorizable)
        self.assertEqual(set([self.categorizable]), self.category.categorizables())
        
    def testRemoveCategorizable(self):
        self.category.addCategorizable(self.categorizable)
        self.category.removeCategorizable(self.categorizable)
        self.failIf(self.category.categorizables())
        self.failIf(self.categorizable.categories())
        
    def testRemovecategorizableThatsNotInThisCategory(self):
        self.category.removeCategorizable(self.categorizable)
        self.failIf(self.category.categorizables())
        self.failIf(self.categorizable.categories())
    
    def testCreateWithCategorizable(self):
        cat = category.Category('category', [self.categorizable])
        self.assertEqual(set([self.categorizable]), cat.categorizables())
        
    def testCreateWithCategorizableDoesNotSetCategorizableCategories(self):
        category.Category('category', [self.categorizable])
        self.assertEqual(set([]), self.categorizable.categories())
    
    def testAddCategorizableToSubCategory(self):
        self.category.addChild(self.subCategory)
        self.subCategory.addCategorizable(self.categorizable)
        self.assertEqual(set([self.categorizable]), 
                         self.category.categorizables(recursive=True))
     
    def testAddSubCategory(self):
        self.category.addChild(self.subCategory)
        self.assertEqual([self.subCategory], self.category.children())
    
    def testCreateWithSubCategories(self):
        cat = category.Category('category', children=[self.subCategory])
        self.assertEqual([self.subCategory], cat.children())
     
    def testParentOfSubCategory(self):
        self.category.addChild(self.subCategory)
        self.assertEqual(self.category, self.subCategory.parent())
        
    def testParentOfRootCategory(self):
        self.assertEqual(None, self.category.parent())
        
    def testEquality_SameSubjectAndNoParents(self):
        self.assertNotEqual(category.Category(self.category.subject()), 
                            self.category)
        self.assertNotEqual(self.category,
                            category.Category(self.category.subject()))
                     
    def testEquality_SameSubjectDifferentParents(self):
        self.category.addChild(self.subCategory)
        self.assertNotEqual(category.Category(self.subCategory.subject()), 
                            self.subCategory)
   
    def testNotFilteredByDefault(self):
        self.failIf(self.category.isFiltered())
        
    def testSetFilteredOn(self):
        self.category.setFiltered()
        self.failUnless(self.category.isFiltered())
        
    def testSetFilteredOff(self):
        self.category.setFiltered(False)
        self.failIf(self.category.isFiltered())
    
    def testSetFilteredViaConstructor(self):
        filteredCategory = category.Category('test', filtered=True)
        self.failUnless(filteredCategory.isFiltered())
        
    def testSetFilteredOnTurnsOffFilteringForChild(self):
        self.category.addChild(self.subCategory)
        self.subCategory.setFiltered()
        self.category.setFiltered()
        self.failIf(self.subCategory.isFiltered())

    def testSetFilteredOnTurnsOffFilteringForGrandChild(self):
        self.category.addChild(self.subCategory)
        grandChild = category.Category('grand child')
        self.subCategory.addChild(grandChild)
        grandChild.setFiltered()
        self.category.setFiltered()
        self.failIf(grandChild.isFiltered())
        
    def testSetFilteredOnForChildTurnsOffFilteringForParent(self):
        self.category.setFiltered()
        self.category.addChild(self.subCategory)
        self.subCategory.setFiltered()
        self.failIf(self.category.isFiltered())

    def testSetFilteredOnForGrandChildTurnsOffFilteringForGrandParent(self):
        self.category.setFiltered()
        self.category.addChild(self.subCategory)
        grandChild = category.Category('grand child')
        self.subCategory.addChild(grandChild)
        grandChild.setFiltered()
        self.failIf(self.category.isFiltered())
        
    def testContains_NoCategorizables(self):
        self.failIf(self.category.contains(self.categorizable))
        
    def testContains_CategorizablesInCategory(self):
        self.category.addCategorizable(self.categorizable)
        self.failUnless(self.category.contains(self.categorizable))
        
    def testContains_CategorizableInSubCategory(self):
        self.subCategory.addCategorizable(self.categorizable)
        self.category.addChild(self.subCategory)
        self.failUnless(self.category.contains(self.categorizable))
        
    def testContains_ParentInCategory(self):
        self.category.addCategorizable(self.categorizable)
        self.categorizable.addChild(self.child)
        self.failUnless(self.category.contains(self.child))
        
    def testContains_ParentInSubCategory(self):
        self.subCategory.addCategorizable(self.categorizable)
        self.category.addChild(self.subCategory)
        self.categorizable.addChild(self.child)
        self.failUnless(self.category.contains(self.child))
    
    def testContains_ChildInCategory(self):
        self.categorizable.addChild(self.child)
        self.category.addCategorizable(self.child)
        self.failIf(self.category.contains(self.categorizable))
        
    def testContains_ChildInSubCategory(self):
        self.categorizable.addChild(self.child)
        self.subCategory.addCategorizable(self.child)
        self.category.addChild(self.subCategory)
        self.failIf(self.category.contains(self.categorizable))
        
    def testRecursiveContains_ChildInCategory(self):
        self.categorizable.addChild(self.child)
        self.category.addCategorizable(self.child)
        self.failUnless(self.category.contains(self.categorizable, treeMode=True))
        
    def testRecursiveContains_ChildInSubcategory(self):
        self.categorizable.addChild(self.child)
        self.subCategory.addCategorizable(self.child)
        self.category.addChild(self.subCategory)
        self.failUnless(self.category.contains(self.categorizable, treeMode=True))
        
    def testCopy_SubjectIsCopied(self):
        self.category.setSubject('New subject')
        copy = self.category.copy()
        self.assertEqual(copy.subject(), self.category.subject())
    
    # pylint: disable-msg=E1101
        
    def testCopy_SubjectIsDifferentFromOriginalSubject(self):
        self.subCategory.setSubject('New subject')
        self.category.addChild(self.subCategory)
        copy = self.category.copy()
        self.subCategory.setSubject('Other subject')
        self.assertEqual('New subject', copy.children()[0].subject())
        
    def testCopy_FilteredStatusIsCopied(self):
        self.category.setFiltered()
        copy = self.category.copy()
        self.assertEqual(copy.isFiltered(), self.category.isFiltered())
        
    def testCopy_CategorizablesAreCopied(self):
        self.category.addCategorizable(self.categorizable)
        copy = self.category.copy()
        self.assertEqual(copy.categorizables(), self.category.categorizables())
        
    def testCopy_CategorizablesAreCopiedIntoADifferentList(self):
        copy = self.category.copy()
        self.category.addCategorizable(self.categorizable)
        self.failIf(self.categorizable in copy.categorizables())

    def testCopy_ChildrenAreCopied(self):
        self.category.addChild(self.subCategory)
        copy = self.category.copy()
        self.assertEqual(self.subCategory.subject(), copy.children()[0].subject())

    def testAddTaskNotification(self):
        eventType = category.Category.categorizableAddedEventType()
        self.registerObserver(eventType)
        self.category.addCategorizable(self.categorizable)
        self.assertEqual(1, len(self.events))
        
    def testRemoveTaskNotification(self):
        eventType = category.Category.categorizableRemovedEventType()
        self.registerObserver(eventType)
        self.category.addCategorizable(self.categorizable)
        self.category.removeCategorizable(self.categorizable)
        self.assertEqual(1, len(self.events))
        
    def testGetDefaultColor(self):
        self.assertEqual(None, self.category.color())
        
    def testSetColor(self):
        self.category.setColor(wx.RED)
        self.assertEqual(wx.RED, self.category.color())
        
    def testCopy_ColorIsCopied(self):
        self.category.setColor(wx.RED)
        copy = self.category.copy()
        self.assertEqual(wx.RED, copy.color())
        
    def testColorChangeNotification(self):
        eventType = category.Category.colorChangedEventType()
        self.registerObserver(eventType)
        self.category.setColor(wx.RED)
        self.assertEqual(1, len(self.events))
        
    def testSubCategoryWithoutColorHasParentColor(self):
        self.category.addChild(self.subCategory)
        self.category.setColor(wx.RED)
        self.assertEqual(wx.RED, self.subCategory.color())
        
    def testSubCategoryWithoutColorHasNoOwnColor(self):
        self.category.addChild(self.subCategory)
        self.category.setColor(wx.RED)
        self.assertEqual(None, self.subCategory.color(recursive=False))
                
    def testParentColorChangeNotification(self):
        eventType = category.Category.colorChangedEventType()
        self.registerObserver(eventType)
        self.category.addChild(self.subCategory)
        self.category.setColor(wx.RED)
        self.assertEqual(1, len(self.events))
        
    def testAddNote(self):
        aNote = note.Note(subject='Note')
        self.category.addNote(aNote)
        self.assertEqual([aNote], self.category.notes())
        
    def testModificationEventTypes(self): # pylint: disable-msg=E1003
        self.assertEqual(super(category.Category,
                               self.category).modificationEventTypes() + \
                         [self.category.filterChangedEventType(), 
                          self.category.categorizableAddedEventType(),
                          self.category.categorizableRemovedEventType()], 
                         self.category.modificationEventTypes())

