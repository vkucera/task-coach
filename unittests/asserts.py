class TaskListAsserts:
    def assertEqualTaskLists(self, expected, actual):
        self.assertEqual(len(expected), len(actual))
        for task in expected:
            self.failUnless(task in actual)

    def assertTaskList(self, expected):
        self.assertEqualTaskLists(expected, self.taskList)
        self.assertAllChildrenInTaskList()

    def assertAllChildrenInTaskList(self):
        for task in self.taskList:
            for child in task.children():
                self.failUnless(child in self.taskList)

    def assertEmptyTaskList(self):
        self.assertEqual(0, len(self.taskList))


class TaskAsserts:
    def failIfParentAndChild(self, parent, child):
        self.failIf(child in parent.children())
        if child.parent():
            self.failIf(child.parent() == parent)

    def failIfParentHasChild(self, parent, child):
        self.failIf(child in parent.children())

    def failUnlessParentAndChild(self, parent, child):
        self.failUnless(child in parent.children())
        self.failUnless(child.parent() == parent)

    def assertCopy(self, orig, copy):
        self.failIf(orig == copy)
        self.assertEqual(orig.subject(), copy.subject())
        self.assertEqual(orig.dueDate(), copy.dueDate())
        self.assertEqual(orig.startDate(), copy.startDate())
        if orig.parent():
            self.failIf(copy in orig.parent().children()) 
        self.failIf(orig.id() == copy.id())
        self.assertEqual(orig.completionDate(), copy.completionDate())
        self.assertEqual(len(orig.children()), len(copy.children()))
        for origChild, copyChild in zip(orig.children(), copy.children()):
            self.assertCopy(origChild, copyChild)


class CommandAsserts:
    def assertHistoryAndFuture(self, expectedHistory, expectedFuture):
        import patterns
        commands = patterns.CommandHistory()
        self.assertEqual(expectedHistory, commands.history)
        self.assertEqual(expectedFuture, commands.future)

    def assertDoUndoRedo(self, assertDone, assertUndone=None, 
            assertRedone=None):
        if not assertUndone:
            assertUndone = assertDone
        if not assertRedone:
            assertRedone = assertDone
        assertDone()
        self.undo()
        assertUndone()
        self.redo()
        assertRedone()

class Mixin(CommandAsserts, TaskAsserts, TaskListAsserts):
    pass
