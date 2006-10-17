import test, patterns

class CommandTestCase(test.wxTestCase):
    def tearDown(self):
        super(CommandTestCase, self).tearDown()
        patterns.CommandHistory().clear()

    def undo(self):
        patterns.CommandHistory().undo()

    def redo(self):
        patterns.CommandHistory().redo()
