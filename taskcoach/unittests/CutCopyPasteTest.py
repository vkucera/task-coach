import test, task, command
from TaskCommandsTest import CommandTestCase, CommandWithChildrenTestCase

class CutCommandTest(CommandTestCase):
    def testCut_WithoutSelection(self):
        command.CutTaskCommand(self.taskList, []).do()
        self.assertDoUndoRedo(lambda: self.assertTaskList([self.task1]))

    def testCut_SpecificTask(self):
        self.taskList.append(self.task2)
        self.cut([self.task1])
        self.assertDoUndoRedo(lambda: (self.assertTaskList([self.task2]),
            self.assertEqual([self.task1], task.Clipboard().get())),
            lambda: (self.assertTaskList([self.task1, self.task2]),
            self.failIf(task.Clipboard())))

    def testCut(self):
        self.cut('all')
        self.assertDoUndoRedo(self.assertEmptyTaskList, 
            lambda: self.assertTaskList(self.originalList))


class CutCommandWithChildrenTest(CommandWithChildrenTestCase):
    def testCutParent(self):
        self.cut([self.parent])
        self.assertDoUndoRedo(lambda: self.assertTaskList([self.task1]),
            lambda: self.assertTaskList(self.originalList))

    def testCutChild(self):
        self.cut([self.child])
        self.assertDoUndoRedo(
            lambda: (self.assertTaskList([self.task1, self.child2, self.parent]),
            self.assertEqual([self.child2], self.parent.children())),
            lambda: (self.assertTaskList(self.originalList),
            self.failUnlessParentAndChild(self.parent, self.child)))

    def testCutParentAndChild(self):
        self.cut([self.child, self.parent])
        self.assertDoUndoRedo(lambda: self.assertTaskList([self.task1]),
            lambda: self.assertTaskList(self.originalList))


class PasteCommandTest(CommandTestCase):
    def testPasteWithoutPreviousCut(self):
        self.paste()
        self.assertDoUndoRedo(lambda: self.assertTaskList(self.originalList))

    def testPaste(self):
        self.cut([self.task1])
        self.paste()
        self.assertDoUndoRedo(lambda: self.assertTaskList(self.originalList),
            self.assertEmptyTaskList)

    def testClipboardIsEmptyAfterPaste(self):
        self.cut([self.task1])
        self.paste()
        self.assertDoUndoRedo(
            lambda: self.assertEqual([], task.Clipboard()._contents), 
            lambda: self.assertEqual([self.task1], task.Clipboard()._contents))


class PasteCommandWithChildrenTest(CommandWithChildrenTestCase):
    def testCutAndPasteChild(self):
        self.cut([self.child])
        self.paste()
        self.assertDoUndoRedo(lambda: (self.assertTaskList(self.originalList),
            self.failIfParentAndChild(self.parent, self.child),
            self.failUnlessParentAndChild(self.child, self.grandchild)),
            lambda: self.assertTaskList([self.task1, self.parent, self.child2]))

    def testCutAndPasteParentAndChild(self):
        self.cut([self.parent, self.child])
        self.paste()
        self.assertDoUndoRedo(lambda: (self.assertTaskList(self.originalList),
            self.failIfParentAndChild(self.parent, self.child)),
            lambda: self.assertTaskList([self.task1]))

    def testCutAndPasteParentAndGrandChild(self):
        self.cut([self.parent, self.grandchild])
        self.paste()
        self.assertDoUndoRedo(lambda: (self.assertTaskList(self.originalList),
            self.failUnlessParentAndChild(self.parent, self.child),
            self.failIfParentAndChild(self.child, self.grandchild)),
            lambda: self.assertTaskList([self.task1]))


class PasteAsSubTaskTest(CommandWithChildrenTestCase):
    def testPasteChild(self):
        self.cut([self.child])
        self.paste([self.task1])
        self.assertDoUndoRedo(
            lambda: (self.assertTaskList(self.originalList),
            self.failUnlessParentAndChild(self.task1, self.child), 
            self.failIfParentAndChild(self.parent, self.child),
            self.failUnlessParentAndChild(self.child, self.grandchild)),
            lambda: (self.assertEqual([self.child2], self.parent.children()),
            self.assertEqual([], self.task1.children())))

    def testPasteExtraChild(self):
        self.cut([self.task1])
        self.paste([self.parent])
        self.assertDoUndoRedo(
            lambda: self.failUnlessParentAndChild(self.parent, self.task1),
            lambda: (self.assertEqual([self.child, self.child2], 
            self.parent.children()), self.assertTaskList([self.parent, 
            self.child, self.child2, self.grandchild])))

    def testPasteChild_MarksNewParentAsNotCompleted(self):
        self.markCompleted([self.parent])
        self.cut([self.task1])
        self.paste([self.parent])
        self.assertDoUndoRedo(
            lambda: self.failIf(self.parent.completed()),
            lambda: self.failUnless(self.parent.completed()))

    def testPasteCompletedChild_DoesNotMarkParentAsNotCompleted(self):
        self.markCompleted([self.task1, self.parent])
        self.cut([self.task1])
        self.paste([self.parent])
        self.assertDoUndoRedo(
            lambda: self.failUnless(self.parent.completed()),
            lambda: self.failUnless(self.parent.completed()))


class CutAndPasteIntegrationTest(CommandTestCase):
    def testUndoCutAndPaste(self):
        self.cut([self.task1])
        self.paste()
        self.undo()
        self.undo()
        self.assertTaskList(self.originalList)

class CutAndPasteWithChildrenIntegrationTest(CommandWithChildrenTestCase):
    def assertTaskListUnchanged(self):
        self.assertTaskList(self.originalList)
        self.failUnlessParentAndChild(self.parent, self.child)
        self.failUnlessParentAndChild(self.child, self.grandchild)

    def testUndoCutAndPaste(self):
        self.cut([self.child])
        self.paste()
        self.undo()
        self.undo()
        self.assertTaskListUnchanged()

    def testUndoCutAndPasteParentAndGrandChild(self):
        self.cut([self.parent, self.grandchild])
        self.paste()
        self.undo()
        self.undo()
        self.assertTaskListUnchanged()

    def testRedoCutAndPasteParentAndGrandChild(self):
        self.cut([self.parent, self.grandchild])
        self.paste()
        self.undo()
        self.undo()
        self.redo()
        self.redo()
        self.assertEqual(None, self.grandchild.parent())
        self.failIf(self.child.children())
        

class CopyCommandTest(CommandTestCase):
    def copy(self, tasks=None):
        tasks = tasks or []
        command.CopyTaskCommand(self.taskList, tasks).do()

    def testCopyWithoutSelection(self):
        command.CopyTaskCommand(self.taskList, []).do()
        self.assertEqual([], task.Clipboard().get())
        self.assertTaskList(self.originalList)

    def testCopy(self):
        self.copy([self.task1])
        copiedTask = task.Clipboard().get()[0]
        self.assertDoUndoRedo(lambda: (self.assertCopy(self.task1, copiedTask),
            self.assertTaskList(self.originalList)),
            lambda: (self.assertTaskList(self.originalList),
            self.failIf(task.Clipboard())))


class CopyCommandWithChildrenTest(CommandWithChildrenTestCase):

    def testCopy(self):
        self.copy([self.parent])
        copiedTask = task.Clipboard().get()[0]
        self.assertDoUndoRedo(
            lambda: self.assertCopy(self.parent, copiedTask),
            lambda: (self.assertTaskList(self.originalList),
            self.failIf(task.Clipboard())))

