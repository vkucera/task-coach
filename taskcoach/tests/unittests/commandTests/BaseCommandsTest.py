import test, command, patterns
from unittests import asserts
from CommandTestCase import CommandTestCase


class DeleteCommandTest(CommandTestCase, asserts.CommandAsserts):
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
