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
from taskcoachlib.domain import category, categorizable


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
    foregroundColorChangedEventType = categorizable.CategorizableCompositeObject.foregroundColorChangedEventType()
    backgroundColorChangedEventType = categorizable.CategorizableCompositeObject.backgroundColorChangedEventType()
        
    def testCategorizableDoesNotBelongToAnyCategoryByDefault(self):
        for recursive in False, True:
            self.failIf(self.categorizable.categories(recursive=recursive))

    def testCategorizableHasNoForegroundColorByDefault(self):
        self.assertEqual(None, self.categorizable.foregroundColor())
    
    def testCategorizableHasNoBackgroundColorByDefault(self):
        self.assertEqual(None, self.categorizable.backgroundColor())
    
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

    def testForegroundColor(self):
        self.categorizable.addCategory(self.category)
        self.category.setForegroundColor(wx.RED)
        self.assertEqual(wx.RED, self.categorizable.foregroundColor())

    def testBackgroundColor(self):
        self.categorizable.addCategory(self.category)
        self.category.setBackgroundColor(wx.RED)
        self.assertEqual(wx.RED, self.categorizable.backgroundColor())

    def testCategorizableOwnForegroundColorOverridesCategoryForegroundColor(self):
        self.categorizable.addCategory(self.category)
        self.category.setForegroundColor(wx.RED)
        self.categorizable.setForegroundColor(wx.GREEN)
        self.assertEqual(wx.GREEN, self.categorizable.foregroundColor())

    def testCategorizableOwnBackgroundColorOverridesCategoryBackgroundColor(self):
        self.categorizable.addCategory(self.category)
        self.category.setBackgroundColor(wx.RED)
        self.categorizable.setBackgroundColor(wx.GREEN)
        self.assertEqual(wx.GREEN, self.categorizable.backgroundColor())

    def testForegroundColorWithTupleColor(self):
        self.categorizable.addCategory(self.category)
        self.category.setForegroundColor((255, 0, 0, 255))
        self.assertEqual(wx.RED, self.categorizable.foregroundColor())
        
    def testBackgroundColorWithTupleColor(self):
        self.categorizable.addCategory(self.category)
        self.category.setBackgroundColor((255, 0, 0, 255))
        self.assertEqual(wx.RED, self.categorizable.backgroundColor())

    def testSubItemUsesParentForegroundColor(self):
        self.categorizable.addCategory(self.category)
        child = categorizable.CategorizableCompositeObject()
        self.categorizable.addChild(child)
        child.setParent(self.categorizable)
        self.category.setForegroundColor(wx.RED)
        self.assertEqual(wx.RED, child.foregroundColor())
    
    def testSubItemUsesParentBackgroundColor(self):
        self.categorizable.addCategory(self.category)
        child = categorizable.CategorizableCompositeObject()
        self.categorizable.addChild(child)
        child.setParent(self.categorizable)
        self.category.setBackgroundColor(wx.RED)
        self.assertEqual(wx.RED, child.backgroundColor())

    def testSubItemDoesNotUseParentForegroundColorWhenItHasItsOwnForegroundColor(self):
        child = categorizable.CategorizableCompositeObject()
        self.categorizable.addChild(child)
        child.setParent(self.categorizable)
        child.addCategory(self.category)
        self.categorizable.setForegroundColor(wx.RED)
        self.category.setForegroundColor(wx.BLUE)
        self.assertEqual(wx.BLUE, child.foregroundColor())
        
    def testSubItemDoesNotUseParentBackgroundColorWhenItHasItsOwnBackgroundColor(self):
        child = categorizable.CategorizableCompositeObject()
        self.categorizable.addChild(child)
        child.setParent(self.categorizable)
        child.addCategory(self.category)
        self.categorizable.setBackgroundColor(wx.RED)
        self.category.setBackgroundColor(wx.BLUE)
        self.assertEqual(wx.BLUE, child.backgroundColor())

    def testForegroundColorChanged(self):
        self.categorizable.addCategory(self.category)
        self.category.addCategorizable(self.categorizable)
        self.registerObserver(self.foregroundColorChangedEventType)
        self.category.setForegroundColor(wx.RED)
        self.assertEqual(1, len(self.events))
    
    def testBackgroundColorChanged(self):
        self.categorizable.addCategory(self.category)
        self.category.addCategorizable(self.categorizable)
        self.registerObserver(self.backgroundColorChangedEventType)
        self.category.setBackgroundColor(wx.RED)
        self.assertEqual(1, len(self.events))

    def testForegroundColorChanged_NotifySubItemsToo(self):
        self.registerObserver(self.foregroundColorChangedEventType)
        self.categorizable.addChild(categorizable.CategorizableCompositeObject())
        self.categorizable.addCategory(self.category)
        self.category.addCategorizable(self.categorizable)
        self.category.setForegroundColor(wx.RED)
        self.assertEqual(1, len(self.events))

    def testBackgroundColorChanged_NotifySubItemsToo(self):
        self.registerObserver(self.backgroundColorChangedEventType)
        self.categorizable.addChild(categorizable.CategorizableCompositeObject())
        self.categorizable.addCategory(self.category)
        self.category.addCategorizable(self.categorizable)
        self.category.setBackgroundColor(wx.RED)
        self.assertEqual(1, len(self.events))

    def testCategorizableDoesNotNotifyWhenItHasItsOwnForegroundColor(self):
        self.categorizable.addCategory(self.category)
        self.categorizable.setForegroundColor(wx.RED)
        self.registerObserver(self.categorizable.foregroundColorChangedEventType())
        self.category.setForegroundColor(wx.GREEN)
        self.assertEqual(0, len(self.events))
                
    def testCategorizableDoesNotNotifyWhenItHasItsOwnBackgroundColor(self):
        self.categorizable.addCategory(self.category)
        self.categorizable.setBackgroundColor(wx.RED)
        self.registerObserver(self.categorizable.backgroundColorChangedEventType())
        self.category.setBackgroundColor(wx.GREEN)
        self.assertEqual(0, len(self.events))

    def testParentForegroundColorChanged(self):
        self.registerObserver(self.foregroundColorChangedEventType)
        subCategory = category.Category('Subcategory')
        self.category.addChild(subCategory)
        subCategory.setParent(self.category)
        self.categorizable.addCategory(subCategory)
        subCategory.addCategorizable(self.categorizable)
        self.category.setForegroundColor(wx.RED)
        self.assertEqual(1, len(self.events))
        
    def testParentBackgroundColorChanged(self):
        self.registerObserver(self.backgroundColorChangedEventType)
        subCategory = category.Category('Subcategory')
        self.category.addChild(subCategory)
        subCategory.setParent(self.category)
        self.categorizable.addCategory(subCategory)
        subCategory.addCategorizable(self.categorizable)
        self.category.setBackgroundColor(wx.RED)
        self.assertEqual(1, len(self.events))

    def testAddCategoryWithForegroundColor(self):
        self.registerObserver(self.foregroundColorChangedEventType)
        newCategory = category.Category('New category')
        newCategory.setForegroundColor(wx.RED)
        self.categorizable.addCategory(newCategory)
        self.assertEqual(1, len(self.events))
        
    def testAddCategoryWithBackgroundColor(self):
        self.registerObserver(self.backgroundColorChangedEventType)
        newCategory = category.Category('New category')
        newCategory.setBackgroundColor(wx.RED)
        self.categorizable.addCategory(newCategory)
        self.assertEqual(1, len(self.events))

    def testAddCategoryWithParentWithForegroundColor(self):
        self.registerObserver(self.foregroundColorChangedEventType)
        parentCategory = category.Category('Parent')
        parentCategory.setForegroundColor(wx.RED)
        childCategory = category.Category('Child')
        parentCategory.addChild(childCategory)
        childCategory.setParent(parentCategory)
        self.categorizable.addCategory(childCategory)
        self.assertEqual(1, len(self.events))
        
    def testAddCategoryWithParentWithBackgroundColor(self):
        self.registerObserver(self.backgroundColorChangedEventType)
        parentCategory = category.Category('Parent')
        parentCategory.setBackgroundColor(wx.RED)
        childCategory = category.Category('Child')
        parentCategory.addChild(childCategory)
        childCategory.setParent(parentCategory)
        self.categorizable.addCategory(childCategory)
        self.assertEqual(1, len(self.events))

    def testRemoveCategoryWithForegroundColor(self):
        self.categorizable.addCategory(self.category)
        self.category.setForegroundColor(wx.RED)
        self.registerObserver(self.foregroundColorChangedEventType)
        self.categorizable.removeCategory(self.category)
        self.assertEqual(1, len(self.events))
        
    def testRemoveCategoryWithBackgroundColor(self):
        self.categorizable.addCategory(self.category)
        self.category.setBackgroundColor(wx.RED)
        self.registerObserver(self.backgroundColorChangedEventType)
        self.categorizable.removeCategory(self.category)
        self.assertEqual(1, len(self.events))

    def testForegroundColorWhenOneOutOfTwoCategoriesHasForegroundColor(self):
        self.categorizable.addCategory(self.category)
        self.categorizable.addCategory(category.Category('Another category'))
        self.category.setForegroundColor(wx.RED)
        self.assertEqual(wx.RED, self.categorizable.foregroundColor())
                
    def testBackgroundColorWhenOneOutOfTwoCategoriesHasBackgroundColor(self):
        self.categorizable.addCategory(self.category)
        self.categorizable.addCategory(category.Category('Another category'))
        self.category.setBackgroundColor(wx.RED)
        self.assertEqual(wx.RED, self.categorizable.backgroundColor())

    def testForegroundColorWhenBothCategoriesHaveSameForegroundColor(self):
        self.categorizable.addCategory(self.category)
        anotherCategory = category.Category('Another category')
        self.categorizable.addCategory(anotherCategory)
        for cat in [self.category, anotherCategory]:
            cat.setForegroundColor(wx.RED)
        self.assertEqual(wx.RED, self.categorizable.foregroundColor())
        
    def testBackgroundColorWhenBothCategoriesHaveSameBackgroundColor(self):
        self.categorizable.addCategory(self.category)
        anotherCategory = category.Category('Another category')
        self.categorizable.addCategory(anotherCategory)
        for cat in [self.category, anotherCategory]:
            cat.setBackgroundColor(wx.RED)
        self.assertEqual(wx.RED, self.categorizable.backgroundColor())

    def testForegroundColorWhenBothCategoriesHaveDifferentForegroundColors(self):
        self.categorizable.addCategory(self.category)
        anotherCategory = category.Category('Another category')
        self.categorizable.addCategory(anotherCategory)
        self.category.setForegroundColor(wx.RED)
        anotherCategory.setForegroundColor(wx.BLUE)
        expectedColor = wx.Color(127, 0, 127, 255)
        self.assertEqual(expectedColor, self.categorizable.foregroundColor())
                
    def testBackgroundColorWhenBothCategoriesHaveDifferentBackgroundColors(self):
        self.categorizable.addCategory(self.category)
        anotherCategory = category.Category('Another category')
        self.categorizable.addCategory(anotherCategory)
        self.category.setBackgroundColor(wx.RED)
        anotherCategory.setBackgroundColor(wx.BLUE)
        expectedColor = wx.Color(127, 0, 127, 255)
        self.assertEqual(expectedColor, self.categorizable.backgroundColor())
                
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
