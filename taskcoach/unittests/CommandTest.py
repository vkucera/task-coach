import test, asserts, patterns

class HistoryTest(test.TestCase, asserts.CommandAsserts):
    def setUp(self):
        self.commands = patterns.CommandHistory()
        self.command = patterns.Command()

    def tearDown(self):
        self.commands.clear()

    def testSingleton(self):
        another = patterns.CommandHistory()
        self.failUnless(self.commands is another)

    def testClear(self):
        self.command.do()
        self.commands.clear()
        self.assertHistoryAndFuture([], [])

    def testDo(self):
        self.command.do()
        self.assertHistoryAndFuture([self.command], [])

    def testUndo(self):
        self.command.do()
        self.commands.undo()
        self.assertHistoryAndFuture([], [self.command])

    def testRedo(self):
        self.command.do()
        self.commands.undo()
        self.commands.redo()
        self.assertHistoryAndFuture([self.command], [])

    def testUndoStr_EmptyHistory(self):
        self.assertEqual('Undo', self.commands.undostr())

    def testUndoStr(self):
        self.command.do()
        self.assertEqual('Undo %s'%self.command, self.commands.undostr())

    def testRedoStr_EmptyFuture(self):
        self.assertEqual('Redo', self.commands.redostr())

    def testRedoStr(self):
        self.command.do()
        self.commands.undo()
        self.assertEqual('Redo %s'%self.command, self.commands.redostr())

    def testHasHistory(self):
        self.failIf(self.commands.hasHistory())
        self.command.do()
        self.failUnless(self.commands.hasHistory())
        self.commands.undo()
        self.failIf(self.commands.hasHistory())

    def testHasFuture(self):
        self.command.do()
        self.failIf(self.commands.hasFuture())
        self.commands.undo()
        self.failUnless(self.commands.hasFuture())
        self.commands.redo()
        self.failIf(self.commands.hasFuture())
