import test, gui, task, wx, date, meta, gui.taskbaricon

class MainWindowMock:
    def restore(self):
        pass

    quit = restore

class TaskBarIconTest(test.TestCase):
    def setUp(self):
        self.taskList = task.TaskList()
        self.icon = gui.taskbaricon.TaskBarIcon(MainWindowMock(), self.taskList)

    def tearDown(self):
        self.icon.Destroy()

    def assertTooltip(self, text):
        self.assertEqual(self.icon.tooltip(), '%s - %s'%(meta.name, text))
   
    def testTooltip_NoTasks(self):
        self.assertTooltip('No tasks due today')
        
    def testTooltip_OneTaskNoDueDate(self):
        self.taskList.append(task.Task())
        self.assertTooltip('No tasks due today')

    def testTooltip_OneTaskDueToday(self):
        self.taskList.append(task.Task(duedate=date.Today()))
        self.assertTooltip('One task due today')
