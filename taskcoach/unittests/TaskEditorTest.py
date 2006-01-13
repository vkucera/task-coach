import test, gui, command, wx, dummy, config
import domain.task as task
import domain.effort as effort
import domain.date as date

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


class TaskEditorTestCase(test.wxTestCase):
    def setUp(self):
        self.taskList = task.TaskList()
        self.effortList = effort.EffortList(self.taskList)
        self.taskList.extend(self.createTasks())
        self.editor = self.createEditor()
        
    def createEditor(self):
        return gui.dialog.editor.TaskEditor(self.frame, self.createCommand(),
            self.taskList, dummy.DummyUICommands(), config.Settings(load=False))

    def tearDown(self):
        # TaskEditor uses CallAfter for setting the focus, make sure those 
        # calls are dealt with, otherwise they'll turn up in other tests
        wx.Yield() 

    def createTasks(self):
        return []

    def setSubject(self, newSubject, index=0):
        self.editor[index][0].setSubject(newSubject)

    def setDescription(self, newDescription, index=0):
        self.editor[index][0].setDescription(newDescription)

    def setReminder(self, newReminderDateTime, index=0):
        self.editor[index][1].setReminder(newReminderDateTime)
        

class NewTaskTest(TaskEditorTestCase):
    def createCommand(self):
        newTaskCommand = command.NewTaskCommand(self.taskList)
        self.task = newTaskCommand.items[0]
        return newTaskCommand

    def testCreate(self):
        self.assertEqual('New task', self.editor[0][0]._subjectEntry.GetValue())
        self.assertEqual(date.Date(), self.editor[0][1]._dueDateEntry.get())

    def testOk(self):
        self.setSubject('Done')
        self.editor.ok()
        self.assertEqual('Done', self.task.subject())

    def testCancel(self):
        self.setSubject('Done')
        self.editor.cancel()
        self.assertEqual('New task', self.task.subject())

    def testDueDate(self):
        self.editor[0][1]._dueDateEntry.set(date.Today())
        self.editor.ok()
        self.assertEqual(date.Today(), self.task.dueDate())

    def testSetCompleted(self):
        self.editor[0][1]._completionDateEntry.set(date.Today())
        self.editor.ok()
        self.assertEqual(date.Today(), self.task.completionDate())

    def testSetUncompleted(self):
        self.editor[0][1]._completionDateEntry.set(date.Today())
        self.editor[0][1]._completionDateEntry.set(date.Date())
        self.editor.ok()
        self.assertEqual(date.Date(), self.task.completionDate())

    def testSetDescription(self):
        self.setDescription('Description')
        self.editor.ok()
        self.assertEqual('Description', self.task.description())

    def testSetReminder(self):
        reminderDateTime = date.DateTime(2005,1,1)
        self.setReminder(reminderDateTime)
        self.editor.ok()
        self.assertEqual(reminderDateTime, self.task.reminder())
        
        
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
        self.editor[0][1]._dueDateEntry.set(date.Tomorrow())
        self.editor.ok()
        self.assertEqual(date.Tomorrow(), self.task.dueDate())

    def testSetStartDate(self):
        self.editor[0][1]._startDateEntry.set(date.Tomorrow())
        self.editor.ok()
        self.assertEqual(date.Tomorrow(), self.task.startDate())
        
    def testSetNegativePriority(self):
        self.editor[0][2]._prioritySpinner.SetValue(-1)
        self.editor.ok()
        self.assertEqual(-1, self.task.priority())
        
    def testSetHourlyFee(self):
        self.editor[0][4]._hourlyFeeEntry.set(100)
        self.editor.ok()
        self.assertEqual(100, self.task.hourlyFee())

    def testSetFixedFee(self):
        self.editor[0][4]._fixedFeeEntry.set(100.5)
        self.editor.ok()
        self.assertEqual(100.5, self.task.fixedFee())

    def testAddCategory(self):
        self.editor[0][2]._textEntry.SetValue('New category')
        self.failUnless(self.editor[0][2]._addButton.IsEnabled())

    def testAddCategory_DontAllowEmptyCategory(self):
        self.editor[0][2]._textEntry.SetValue('')
        self.failIf(self.editor[0][2]._addButton.IsEnabled())


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
        return command.EditTaskCommand(self.taskList, [self.parent, self.child])

    def createTasks(self):
        self.parent = task.Task('Parent')
        self.child = task.Task('Child')
        self.parent.addChild(self.child)
        return [self.parent] # self.child is added to tasklist automatically

    def testOk(self):
        self.editor.ok()
        self.assertEqual('TaskA', self.parent.subject())
        self.assertEqual('TaskB', self.child.subject())

    def testCancel(self):
        self.editor.cancel()
        self.assertEqual('Parent', self.parent.subject())
        self.assertEqual('Child', self.child.subject())

    def testChangeDueDateOfParentHasNoEffectOnChild(self):
        self.editor[0][1]._dueDateEntry.set(date.Yesterday())
        self.editor.ok()
        self.assertEqual(date.Date(), self.child.dueDate())

    def testChangeStartDateOfParentHasNoEffectOnChild(self):
        self.editor[0][1]._startDateEntry.set(date.Tomorrow())
        self.editor.ok()
        self.assertEqual(date.Today(), self.child.startDate())


class EditTaskWithEffortTest(TaskEditorTestCase):    
    def createCommand(self):
        return command.EditTaskCommand(self.taskList, [self.task])

    def createTasks(self):
        self.task = task.Task('task')
        self.task.addEffort(effort.Effort(self.task))
        return [self.task]
        
    def testCancel(self):
        self.editor.cancel()
        self.assertEqual(1, len(self.task.efforts()))
        
        
class FocusTest(TaskEditorTestCase):
    def createCommand(self):
        return command.NewTaskCommand(self.taskList)

    def testFocus(self):
        # Unfortunately, it seems we *have* to show to window on Linux (Ubuntu)
        # in order to get wx.Window_FindFocus to not return None.
        # We move the window outside the visible screen area to make it 
        # less annoying.
        self.editor.SetDimensions(10000, 10000, 0, 0)
        self.editor.Show()
        wx.Yield()
        self.assertEqual(self.editor[0][0]._subjectEntry, wx.Window_FindFocus())


class EffortEditorTest(TaskEditorTestCase):      
    def tearDown(self):
        pass

    def createCommand(self):
        return command.EditEffortCommand(self.effortList, self.effortList)
        
    def createTasks(self):
        self.task1 = task.Task('task1')
        self.effort = effort.Effort(self.task1)
        self.task1.addEffort(self.effort)
        self.task2 = task.Task('task2')
        return [self.task1, self.task2]
    
    def createEditor(self):
        return gui.dialog.editor.EffortEditor(self.frame, self.createCommand(), 
            {}, self.effortList, self.taskList)
    
    def testCreate(self):
        self.assertEqual(self.effortList[0].getStart().date(), 
            self.editor[0]._startEntry.GetValue().date())
        self.assertEqual(self.effortList[0].task().subject(), 
            self.editor[0]._taskEntry.GetValue())

    def testOK(self):
        stop = self.effortList[0].getStop()
        self.editor.ok()
        self.assertEqual(stop, self.effortList[0].getStop())
        
    def testInvalidEffort(self):
        self.effortList[0].setStop(date.DateTime(1900, 1, 1))
        self.editor = self.createEditor()
        self.editor._interior[0].preventNegativeEffortDuration()
        self.failIf(self.editor._buttonBox._buttons['OK'].IsEnabled())
        
    def testChangeTask(self):
        self.editor[0]._taskEntry.SetStringSelection('task2')
        self.editor.ok()
        self.assertEqual(self.task2, self.effortList[0].task())
        self.failIf(self.effort in self.task1.efforts())

