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

import test
from taskcoachlib import patterns, command
from taskcoachlib.domain import category
from CommandTestCase import CommandTestCase


class ToggleCategoryCommandTest(CommandTestCase):
    def setUp(self):
        super(ToggleCategoryCommandTest, self).setUp()
        self.category = category.Category('Cat')
        self.categorizable = category.categorizable.CategorizableCompositeObject()
        
    def toggleItem(self, items=None):
        check = command.ToggleCategoryCommand(category=self.category, items=items or [])
        check.do()
        
    def testToggleCategory_AffectsCategorizable(self):
        self.toggleItem([self.categorizable])
        self.assertDoUndoRedo(\
            lambda: self.assertEqual(set([self.category]), self.categorizable.categories()),
            lambda: self.assertEqual(set(), self.categorizable.categories()))
        
    def testToggleCategory_AffectsCategory(self):
        self.toggleItem([self.categorizable])
        self.assertDoUndoRedo(\
            lambda: self.assertEqual([self.categorizable], self.category.categorizables()),
            lambda: self.assertEqual([], self.category.categorizables()))