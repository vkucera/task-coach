class ListAsserts(object):
    def assertEqualLists(self, expected, actual):
        self.assertEqual(len(expected), len(actual))
        for item in expected:
            self.failUnless(item in actual)

    def assertEmptyList(self, list):
        self.assertEqual(0, len(list))
        
        
class TaskListAsserts(ListAsserts):
    def assertTaskList(self, expected):
        self.assertEqualLists(expected, self.taskList)
        self.assertAllChildrenInTaskList()

    def assertAllChildrenInTaskList(self):
        for task in self.taskList:
            for child in task.children():
                self.failUnless(child in self.taskList)

    def assertEmptyTaskList(self):
        self.assertEmptyList(self.taskList)


class EffortListAsserts(ListAsserts):
    def assertEffortList(self, expected):
        self.assertEqualLists(expected, self.effortList)
        

class TaskAsserts(object):
    def failIfParentAndChild(self, parent, child):
        self.failIf(child in parent.children())
        if child.parent():
            self.failIf(child.parent() == parent)

    def failIfParentHasChild(self, parent, child):
        self.failIf(child in parent.children())

    def failUnlessParentAndChild(self, parent, child):
        self.failUnless(child in parent.children())
        self.failUnless(child.parent() == parent)

    def assertTaskCopy(self, orig, copy):
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
            self.assertTaskCopy(origChild, copyChild)
      

class CommandAsserts(object):
    def assertHistoryAndFuture(self, expectedHistory, expectedFuture):
        import patterns
        commands = patterns.CommandHistory()
        self.assertEqual(expectedHistory, commands.getHistory())
        self.assertEqual(expectedFuture, commands.getFuture())

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

class Mixin(CommandAsserts, TaskAsserts, TaskListAsserts, EffortListAsserts):
    pass
