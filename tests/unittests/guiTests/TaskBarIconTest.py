import test, gui, wx, meta, gui.taskbaricon, config
import domain.task as task
import domain.effort as effort
import domain.date as date

class MainWindowMock:
    def restore(self):
        pass

    quit = restore

class TaskBarIconTest(test.TestCase):
    def setUp(self):
        self.taskList = task.TaskList()
        self.settings = config.Settings(load=False)
        self.icon = gui.taskbaricon.TaskBarIcon(MainWindowMock(), self.taskList,
            self.settings)

    def tearDown(self):
        if '__WXMAC__' in wx.PlatformInfo:
            self.icon.RemoveIcon()
        else:
            self.icon.Destroy()

    def assertTooltip(self, text):
        self.assertEqual(self.icon.tooltip(), '%s - %s'%(meta.name, text))
   
    def testTooltip_NoTasks(self):
        self.assertTooltip('No tasks due today')
        
    def testIcon_NoTasks(self):
        self.failUnless(self.icon.IsIconInstalled())

    def testTooltip_OneTaskNoDueDate(self):
        self.taskList.append(task.Task())
        self.assertTooltip('No tasks due today')

    def testTooltip_OneTaskDueToday(self):
        self.taskList.append(task.Task(dueDate=date.Today()))
        self.assertTooltip('One task due today')
        
    def testTooltip_MultipleTasksDueToday(self):
        self.taskList.append(task.Task(dueDate=date.Today()))
        self.taskList.append(task.Task(dueDate=date.Today()))
        self.assertTooltip('2 tasks due today')

    def testStartTracking(self):
        activeTask = task.Task()
        self.taskList.append(activeTask)
        activeTask.addEffort(effort.Effort(activeTask))
        self.assertEqual('tick', self.icon.bitmap())

    def testStopTracking(self):
        activeTask = task.Task()
        self.taskList.append(activeTask)
        activeEffort = effort.Effort(activeTask)
        activeTask.addEffort(activeEffort)
        activeTask.removeEffort(activeEffort)
        self.assertEqual(self.icon.defaultBitmap(), self.icon.bitmap())

    def testRemoveTask(self):
        newTask = task.Task()
        self.taskList.append(newTask)
        self.taskList.remove(newTask)
        self.assertTooltip('No tasks due today')