'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>

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
from taskcoachlib.domain import attachment, task, note, category
from CommandTestCase import CommandTestCase

    
class DeleteCommandTest(CommandTestCase):
    def setUp(self):
        super(DeleteCommandTest, self).setUp()
        self.item = 'Item'
        self.items = patterns.List([self.item])
        
    def deleteItem(self, items=None):
        delete = command.DeleteCommand(self.items, items or [])
        delete.do()
        
    def testDeleteItem_WithoutSelection(self):
        self.deleteItem()
        self.assertDoUndoRedo(lambda: self.assertEqual([self.item], self.items))
        
    def testDeleteItem_WithSelection(self):
        self.deleteItem([self.item])
        self.assertDoUndoRedo(lambda: self.assertEqual([], self.items),
                              lambda: self.assertEqual([self.item], self.items))


class AddAttachmentTests(object):
    def addAttachment(self, selectedItems=None, 
                      attachment=attachment.FileAttachment('attachment')):
        self.attachment = attachment
        addAttachmentCommand = command.AddAttachmentCommand(self.model,
            selectedItems or [], attachments=[attachment])
        addAttachmentCommand.do()

    def testAddOneAttachmentToOneItem(self):
        self.addAttachment([self.item1])
        self.assertDoUndoRedo(lambda: self.assertEqual([self.attachment], 
            self.item1.attachments()), lambda: self.assertEqual([], 
            self.item1.attachments()))
            
    def testAddOneAttachmentToTwoItems(self):
        self.addAttachment([self.item1, self.item2])
        self.assertDoUndoRedo(lambda: self.failUnless([self.attachment] == \
            self.item1.attachments() == self.item2.attachments()), 
            lambda: self.failUnless([] == self.item1.attachments() == \
            self.item2.attachments()))


class AddAttachmentTestCase(CommandTestCase):
    def setUp(self):
        super(AddAttachmentTestCase, self).setUp()
        self.item1 = self.ItemClass('item1')
        self.item2 = self.ItemClass('item2')
        self.model = self.ModelClass([self.item1, self.item2])


class AddAttachmentCommandWithTasksTest(AddAttachmentTestCase, AddAttachmentTests):
    ItemClass = task.Task
    ModelClass = task.TaskList


class AddAttachmentCommandWithNotesTest(AddAttachmentTestCase, AddAttachmentTests):
    ItemClass = note.Note
    ModelClass = note.NoteContainer


class AddAttachmentCommandWithCategoriesTest(AddAttachmentTestCase, AddAttachmentTests):
    ItemClass = category.Category
    ModelClass = category.CategoryList
