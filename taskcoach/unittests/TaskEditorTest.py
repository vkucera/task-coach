import test, gui, task, date, command, wx, effort, dummy

class DummyViewer:
    def __init__(self):
        self.taskList = task.TaskList()

    def extend(self, *args):
        self.taskList.extend(*args)

    def select(self, *args):
        pass

    def curselection(self, *args, **kwargs):
        return self.taskList

    def __getitem__(self, index):
        return self.taskList[index]


class DummyEvent:
    def __init__(self, checked):
        self._checked = checked

    def IsChecked(self):
        return self._checked


class TaskEditorTestCase(test.TestCase):
    def setUp(self):
        self.taskList = task.TaskList()
        self.taskList.extend(self.createTasks())
        self.effortList = effort.EffortList(self.taskList)
        self.editor = self.createEditor()
        
    def createEditor(self):
        return gui.editor.TaskEditor(wx.Frame(None), self.createCommand(),
            {}, dummy.Settings())

    def tearDown(self):
        self.editor.Destroy()
        # TaskEditor uses CallAfter for setting the focus, make sure those 
        # calls are dealt with, otherwise they'll turn up in other tests
        wx.Yield() 

    def createTasks(self):
        return []

    def setSubject(self, newSubject, index=0):
        self.editor[index].setSubject(newSubject)

    def setDescription(self, newDescription, index=0):
        self.editor[index].setDescription(newDescription)


class NewTaskTest(TaskEditorTestCase):
    def createCommand(self):
        newTaskCommand = command.NewTaskCommand(self.taskList)
        self.task = newTaskCommand.items[0]
        return newTaskCommand

    def testCreate(self):
        self.assertEqual('New task', self.editor[0]._subjectEntry.GetValue())
        self.assertEqual(date.Date(), self.editor[0]._dueDateEntry.get())

    def testOk(self):
        self.setSubject('Done')
        self.editor.ok()
        self.assertEqual('Done', self.task.subject())

    def testCancel(self):
        self.setSubject('Done')
        self.editor.cancel()
        self.assertEqual('New task', self.task.subject())

    def testDueDate(self):
        self.editor[0]._dueDateEntry.set(date.Today())
        self.editor.ok()
        self.assertEqual(date.Today(), self.task.dueDate())

    def testSetCompleted(self):
        self.editor[0]._completionDateEntry.set(date.Today())
        self.editor.ok()
        self.assertEqual(date.Today(), self.task.completionDate())

    def testSetUncompleted(self):
        self.editor[0]._completionDateEntry.set(date.Today())
        self.editor[0]._completionDateEntry.set(date.Date())
        self.editor.ok()
        self.assertEqual(date.Date(), self.task.completionDate())

    def testSetDescription(self):
        self.setDescription('Description')
        self.editor.ok()
        self.assertEqual('Description', self.task.description())


class NewSubTaskTest(TaskEditorTestCase):
    def createCommand(self):
        newSubTaskCommand = command.NewSubTaskCommand(self.taskList, [self.task])
        self.subtask = newSubTaskCommand.items[0]
        return newSubTaskCommand

    def createTasks(self):
        self.task = task.Task()
        return [self.task]

    def testOk(self):
        self.editor.ok()
        self.assertEqual([self.subtask], self.task.children())

    def testCancel(self):
        self.editor.cancel()
        self.assertEqual([], self.task.children())


class EditTaskTest(TaskEditorTestCase):
    def setUp(self):
        super(EditTaskTest, self).setUp()
        self.setSubject('Done')

    def createCommand(self):
        return command.EditTaskCommand(self.taskList, [self.task])

    def createTasks(self):
        self.task = task.Task('Task to edit')
        return [self.task]

    def testOk(self):
        self.editor.ok()
        self.assertEqual('Done', self.task.subject())

    def testCancel(self):
        self.editor.cancel()
        self.assertEqual('Task to edit', self.task.subject())

    def testSetDueDate(self):
        self.editor[0]._dueDateEntry.set(date.Tomorrow())
        self.editor.ok()
        self.assertEqual(date.Tomorrow(), self.task.dueDate())

    def testSetStartDate(self):
        self.editor[0]._startDateEntry.set(date.Tomorrow())
        self.editor.ok()
        self.assertEqual(date.Tomorrow(), self.task.startDate())


class EditMultipleTasksTest(TaskEditorTestCase):
    def setUp(self):
        super(EditMultipleTasksTest, self).setUp()
        self.setSubject('TaskA', 0)
        self.setSubject('TaskB', 1)

    def createCommand(self):
        return command.EditTaskCommand(self.taskList, [self.task1, self.task2])

    def createTasks(self):
        self.task1 = task.Task('Task1')
        self.task2 = task.Task('Task2')
        return [self.task1, self.task2]

    def testOk(self):
        self.editor.ok()
        self.assertEqual('TaskA', self.task1.subject())
        self.assertEqual('TaskB', self.task2.subject())

    def testCancel(self):
        self.editor.cancel()
        self.assertEqual('Task1', self.task1.subject())
        self.assertEqual('Task2', self.task2.subject())


class EditTaskWithChildrenTest(TaskEditorTestCase):
    def setUp(self):
        super(EditTaskWithChildrenTest, self).setUp()
        self.setSubject('TaskA', 0)
        self.setSubject('TaskB', 1)

    def createCommand(self):
        return command.EditTaskCommand(self.taskList, [self.task1, self.task2])

    def createTasks(self):
        self.task1 = task.Task('Task1')
        self.task2 = task.Task('Task2')
        self.task1.addChild(self.task2)
        return [self.task1] # self.task2 is added to tasklist automatically

    def testOk(self):
        self.editor.ok()
        self.assertEqual('TaskA', self.task1.subject())
        self.assertEqual('TaskB', self.task2.subject())

    def testCancel(self):
        self.editor.cancel()
        self.assertEqual('Task1', self.task1.subject())
        self.assertEqual('Task2', self.task2.subject())

    def testCannotChangeDueDate(self):
        self.editor[0]._dueDateEntry.set(date.Tomorrow())
        self.editor.ok()
        self.assertNotEqual(date.Tomorrow(), self.task1.dueDate())

    def testCannotChangeStartDate(self):
        self.editor[0]._startDateEntry.set(date.Tomorrow())
        self.editor.ok()
        self.assertNotEqual(date.Tomorrow(), self.task1.startDate())


class FocusTest(TaskEditorTestCase, test.wxTestCase):
    def createCommand(self):
        return command.NewTaskCommand(self.taskList)

    def testFocus(self):
        wx.Yield()
        self.assertEqual(self.editor[0]._subjectEntry, self.editor.FindFocus())
        

class EffortEditorTest(TaskEditorTestCase):      
    def createCommand(self):
        return command.EditEffortCommand(self.effortList, self.effortList)
        
    def createTasks(self):
        theTask = task.Task()
        theTask.addEffort(effort.Effort(theTask))
        return [theTask]
    
    def createEditor(self):
        return gui.editor.EffortEditor(wx.Frame(None), self.createCommand(), {}, self.effortList)
    
    def testCreate(self):
        self.assertEqual(self.effortList[0].getStart().date(), 
            self.editor[0]._startEntry.GetValue().date())

    def testOK(self):
        stop = self.effortList[0].getStop()
        self.editor.ok()
        self.assertEqual(stop, self.effortList[0].getStop())
        
    def testInvalidEffort(self):
        self.effortList[0].setStop(date.DateTime(1900, 1, 1))
        self.editor = self.createEditor()
        self.editor._book[0].preventNegativeEffortDuration()
        self.failIf(self.editor._buttonBox._buttons['OK'].IsEnabled())