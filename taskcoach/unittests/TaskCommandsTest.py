import test, asserts, command, task, patterns, dummy, effort, date

class CommandTestCase(test.wxTestCase, asserts.Mixin):
    def setUp(self):
        self.taskList = task.TaskList()
        self.task1 = task.Task()
        self.task2 = task.Task()
        self.taskList.append(self.task1)
        self.originalList = [self.task1]

    def tearDown(self):
        task.Clipboard().clear()
        patterns.CommandHistory().clear()

    def undo(self):
        patterns.CommandHistory().undo()

    def redo(self):
        patterns.CommandHistory().redo()

    def delete(self, tasks=None):
        if tasks == 'all':
            tasks = self.taskList[:]
        command.DeleteTaskCommand(self.taskList, tasks or []).do()
 
    def cut(self, tasks=None):
        if tasks == 'all':
            tasks = self.taskList[:]
        command.CutTaskCommand(self.taskList, tasks or []).do()

    def paste(self, tasks=None):
        if tasks:
            command.PasteTaskAsSubtaskCommand(self.taskList, tasks).do()
        else:
            command.PasteTaskCommand(self.taskList).do()

    def copy(self, tasks=None):
        command.CopyTaskCommand(self.taskList, tasks or []).do()

    def markCompleted(self, tasks=None):
        command.MarkCompletedCommand(self.taskList, tasks or []).do()

    def newSubTask(self, tasks=None, markCompleted=False):
        tasks = tasks or []
        newSubTask = command.NewSubTaskCommand(self.taskList, tasks)
        if markCompleted:
            for subtask in newSubTask.items:
                subtask.setCompletionDate()
        newSubTask.do()


class CommandWithChildrenTestCase(CommandTestCase):
    def setUp(self):
        super(CommandWithChildrenTestCase, self).setUp()
        self.parent = task.Task()
        self.child = task.Task(parent=self.parent)
        self.child2 = task.Task(parent=self.parent)
        self.grandchild = task.Task(parent=self.child)
        self.originalList.extend([self.parent, self.child, self.child2, self.grandchild])
        self.taskList.extend([self.parent, self.child, self.child2, self.grandchild])


class CommandWithEffortTestCase(CommandTestCase):
    def setUp(self):
        super(CommandWithEffortTestCase, self).setUp()
        self.effortList = effort.EffortList(self.taskList)
        self.task1.addEffort(effort.Effort(self.task1))
        self.task2.addEffort(effort.Effort(self.task2, 
            date.DateTime(2004,1,1), date.DateTime(2004,1,2)))
        self.taskList.append(self.task2)

        
class DeleteCommandTest(CommandTestCase):
    def testDeleteAllTasks(self):
        self.taskList.append(self.task2)
        self.delete('all')
        self.assertDoUndoRedo(self.assertEmptyTaskList, 
            lambda: self.assertTaskList([self.task1, self.task2]))

    def testDeleteOneTask(self):
        self.taskList.append(self.task2)
        self.delete([self.task1])
        self.assertDoUndoRedo(lambda: self.assertTaskList([self.task2]),
            lambda: self.assertTaskList([self.task1, self.task2]))

    def testDeleteEmptyList(self):
        del self.taskList[:]
        self.delete('all')
        self.assertDoUndoRedo(self.assertEmptyTaskList)

    def testDeleteEmptyList_NoCommandHistory(self):
        del self.taskList[:]
        self.delete('all')
        self.assertDoUndoRedo(lambda: self.assertHistoryAndFuture([], []))

    def testDelete(self):
        self.delete('all')
        self.assertDoUndoRedo(self.assertEmptyTaskList,
            lambda: self.assertTaskList(self.originalList))
        

class DeleteCommandWithChildrenTest(CommandWithChildrenTestCase):

    def testDeleteParent(self):
        self.delete([self.parent])
        self.assertDeleteWorks()

    def testDeleteParentAndChild(self):
        self.delete([self.parent, self.child])
        self.assertDeleteWorks()

    def testDeleteParentAndGrandchild(self):
        self.delete([self.parent, self.grandchild])
        self.assertDeleteWorks()

    def testDeleteLastNotCompletedChildMarksParentAsCompleted(self):
        self.markCompleted([self.child2])
        self.delete([self.child])
        self.assertDoUndoRedo(
            lambda: self.failUnless(self.parent.completed()), 
            lambda: self.failIf(self.parent.completed()))

    def assertDeleteWorks(self):
        self.assertDoUndoRedo(self.assertParentAndAllChildrenDeleted,
            self.assertTaskListUnchanged)

    def assertParentAndAllChildrenDeleted(self):
        self.assertTaskList([self.task1])

    def assertTaskListUnchanged(self):
        self.assertTaskList(self.originalList)
        self.failUnlessParentAndChild(self.parent, self.child)
        self.failUnlessParentAndChild(self.child, self.grandchild)


class DeleteCommandWithEffortTest(CommandWithEffortTestCase):
    def testDeleteActiveTask(self):
        self.delete([self.task1])
        self.assertDoUndoRedo(
            lambda: self.assertEqual(1, len(self.effortList)),
            lambda: self.assertEqual(2, len(self.effortList)))


class NewTaskCommandTest(CommandTestCase):
    def new(self):
        command.NewTaskCommand(self.taskList, [task.Task()]).do()
    
    def testNewTask(self):
        self.new()
        newTask = self.taskList[1]
        self.assertDoUndoRedo(
            lambda: self.assertTaskList([self.task1, newTask]),
            lambda: self.assertTaskList(self.originalList))


class NewSubTaskCommandTest(CommandTestCase):

    def testNewSubTask_WithoutSelection(self):
        self.newSubTask()
        self.assertDoUndoRedo(lambda: self.assertTaskList(self.originalList))

    def testNewSubTask(self):
        self.newSubTask([self.task1])
        newSubTask = self.task1.children()[0]
        self.assertDoUndoRedo(lambda: self.assertNewSubTask(newSubTask),
            lambda: self.assertTaskList(self.originalList))

    def assertNewSubTask(self, newSubTask):
        self.assertEqual(len(self.originalList)+1, len(self.taskList))
        self.assertEqualTaskLists([newSubTask], self.task1.children())

    def testNewSubTask_MarksParentAsNotCompleted(self):
        self.markCompleted([self.task1])
        self.newSubTask([self.task1])
        self.assertDoUndoRedo(lambda: self.failIf(self.task1.completed()),
            lambda: self.failUnless(self.task1.completed()))

    def testNewSubTask_MarksGrandParentAsNotCompleted(self):
        self.newSubTask([self.task1])
        self.markCompleted([self.task1])
        self.newSubTask([self.task1.children()[0]])
        self.assertDoUndoRedo(lambda: self.failIf(self.task1.completed()),
            lambda: self.failUnless(self.task1.completed()))

    def testNewCompletedSubTask(self):
        self.newSubTask([self.task1], markCompleted=True)
        self.assertDoUndoRedo(lambda: self.failUnless(self.task1.completed()),
            lambda: self.failIf(self.task1.completed()))


class EditTaskCommandTest(CommandTestCase):
    def edit(self, tasks=None):
        tasks = tasks or []
        editcommand = command.EditTaskCommand(self.taskList, tasks)
        for task in tasks:
            task.setSubject('New subject')
            task.setDescription('New description')
            task.setBudget(date.TimeDelta(hours=1))
            task.setCompletionDate()
        editcommand.do()

    def testEditTask(self):
        self.edit([self.task1])
        self.assertDoUndoRedo(
            lambda: self.assertEqual('New subject', self.task1.subject()),
            lambda: self.assertEqual('', self.task1.subject()))

    def testEditTask_MarkCompleted(self):
        self.edit([self.task1])
        self.assertDoUndoRedo(
            lambda: self.failUnless(self.task1.completed()),
            lambda: self.failIf(self.task1.completed()))

    def testEditTaskWithChildren_MarkCompleted(self):
        self.newSubTask([self.task1])
        self.edit([self.task1])
        self.assertDoUndoRedo(
            lambda: self.failUnless(self.task1.children()[0].completed()),
            lambda: self.failIf(self.task1.children()[0].completed()))

    def testEditDescription(self):
        self.edit([self.task1])
        self.assertDoUndoRedo(
            lambda: self.assertEqual('New description', self.task1.description()),
            lambda: self.assertEqual('', self.task1.description()))

    def testEditBudget(self):
        self.edit([self.task1])
        self.assertDoUndoRedo(
            lambda: self.assertEqual(date.TimeDelta(hours=1), self.task1.budget()),
            lambda: self.assertEqual(date.TimeDelta(), self.task1.budget()))
            
            
class MarkCompletedCommandTest(CommandWithChildrenTestCase):

    def testMarkCompleted(self):
        self.markCompleted([self.task1])
        self.assertDoUndoRedo(
            lambda: self.failUnless(self.task1.completed()),
            lambda: self.failIf(self.task1.completed()))

    def testMarkCompleted_TaskAlreadyCompleted(self):
        self.task1.setCompletionDate()
        self.markCompleted([self.task1])
        self.assertDoUndoRedo(lambda: self.failUnless(self.task1.completed()))

    def testMarkCompletedParent(self):
        self.markCompleted([self.parent])
        self.assertDoUndoRedo(lambda: self.failUnless(self.child.completed()
            and self.child2.completed() and self.grandchild.completed()),
            lambda: self.failIf(self.child.completed() or
            self.child2.completed() or self.grandchild.completed()))

    def testMarkCompletedParent_WhenChildAlreadyCompleted(self):
        self.markCompleted([self.child])
        self.markCompleted([self.parent])
        self.assertDoUndoRedo(lambda: self.failUnless(self.child.completed()))

    def testMarkCompletedGrandChild(self):
        self.markCompleted([self.grandchild])
        self.assertDoUndoRedo(
            lambda: self.failUnless(self.child.completed() and 
                not self.parent.completed()), 
            lambda: self.failIf(self.child.completed() or 
                self.parent.completed()))

    def testMarkCompletedStopsEffortTracking(self):
        self.task1.addEffort(effort.Effort(self.task1))
        self.markCompleted([self.task1])
        self.assertDoUndoRedo(lambda: self.failIf(self.task1.isBeingTracked()), 
            lambda: self.failUnless(self.task1.isBeingTracked()))