import test, patterns, command

class CommandTestCase(test.wxTestCase):
    def tearDown(self):
        super(CommandTestCase, self).tearDown()
        patterns.CommandHistory().clear()

    def undo(self):
        patterns.CommandHistory().undo()

    def redo(self):
        patterns.CommandHistory().redo()

    def cut(self, items=None):
        if items == 'all':
            items = list(self.list)
        command.CutCommand(self.list, items or []).do()

    def paste(self):        
        command.PasteCommand(self.list).do()
