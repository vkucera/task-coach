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
from CommandTestCase import CommandTestCase, TestCommand

    
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


class AggregateCommandTest(CommandTestCase):
    def setUp(self):
        super(AggregateCommandTest, self).setUp()

        self.cmd1 = TestCommand()
        self.cmd2 = TestCommand()
        self.cmd1.do()
        self.cmd2.do()
        self.cmd = patterns.AggregateCommand([self.cmd1, self.cmd2])
        self.cmd.do()

    def test_undo(self):
        self.undo()
        self.failUnless(self.cmd1.undone)
        self.failUnless(self.cmd2.undone)

    def test_redo(self):
        self.undo()
        self.redo()
        self.failUnless(self.cmd1.redone)
        self.failUnless(self.cmd2.redone)


class CommandStackTest(CommandTestCase):
    def test_ok(self):
        command = TestCommand()
        self.push()
        command.do()
        self.pop(True)
        self.failUnless(self.hasHistory())

    def test_cancel(self):
        cmd = TestCommand()
        self.push()
        cmd.do()
        self.pop(False)
        self.failIf(self.hasHistory())
        self.failUnless(cmd.undone)
