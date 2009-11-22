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

from taskcoachlib import command
from taskcoachlib.domain import category, categorizable
from CommandTestCase import CommandTestCase


class ToggleCategoryCommandTest(CommandTestCase):
    def setUp(self):
        super(ToggleCategoryCommandTest, self).setUp()
        self.category = category.Category('Cat')
        self.categorizable = categorizable.CategorizableCompositeObject()
        
    def toggleItem(self, items=None, category=None):
        check = command.ToggleCategoryCommand(category=category or self.category, 
                                              items=items or [])
        check.do()

    def testToggleCategory_AffectsCategorizable(self):
        self.toggleItem([self.categorizable])
        self.assertDoUndoRedo(\
            lambda: self.assertEqual(set([self.category]), self.categorizable.categories()),
            lambda: self.assertEqual(set(), self.categorizable.categories()))
        
    def testToggleCategory_AffectsCategory(self):
        self.toggleItem([self.categorizable])
        self.assertDoUndoRedo(\
            lambda: self.assertEqual(set([self.categorizable]), self.category.categorizables()),
            lambda: self.assertEqual(set(), self.category.categorizables()))
                
        
    def testToggleMutualExclusiveSubcategory(self):
        subCategory1 = category.Category('subCategory1')
        subCategory2 = category.Category('subCategory2')
        self.category.addChild(subCategory1)
        self.category.addChild(subCategory2)
        self.category.makeSubcategoriesExclusive()
        self.categorizable.addCategory(subCategory1)
        subCategory1.addCategorizable(self.categorizable)
        self.toggleItem([self.categorizable], subCategory2)
        self.assertDoUndoRedo(
            lambda: self.assertEqual(set([subCategory2]), self.categorizable.categories()),
            lambda: self.assertEqual(set([subCategory1]), self.categorizable.categories()))

    def testToggleMutualExclusiveSubcategoryThatIsAlreadyChecked(self):
        subCategory1 = category.Category('subCategory1')
        subCategory2 = category.Category('subCategory2')
        self.category.addChild(subCategory1)
        self.category.addChild(subCategory2)
        self.category.makeSubcategoriesExclusive()
        self.categorizable.addCategory(subCategory1)
        subCategory1.addCategorizable(self.categorizable)
        self.toggleItem([self.categorizable], subCategory1)
        self.assertDoUndoRedo(
            lambda: self.assertEqual(set(), self.categorizable.categories()),
            lambda: self.assertEqual(set([subCategory1]), self.categorizable.categories()))
