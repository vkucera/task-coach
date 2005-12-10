import test, gui, date, wx, config
import domain.task as task

class TaskColorTest(test.TestCase):
    def setUp(self):
        self.settings = config.Settings(load=False)
        
    def assertColor(self, task, color):
        self.assertEqual(color, gui.color.taskColor(task, self.settings))

    def testDefaultTask(self):
        self.assertColor(task.Task(), wx.BLACK)

    def testCompletedTask(self):
        completed = task.Task()
        completed.setCompletionDate()
        self.assertColor(completed, wx.GREEN)

    def testOverDueTask(self):
        overdue = task.Task(duedate=date.Yesterday())
        self.assertColor(overdue, wx.RED)

    def testDueTodayTask(self):
        duetoday = task.Task(duedate=date.Today())
        self.assertColor(duetoday, wx.Colour(255, 128, 0))

    def testDueTomorrow(self):
        duetoday = task.Task(duedate=date.Tomorrow())
        self.assertColor(duetoday, wx.NamedColour('BLACK'))

    def testInactive(self):
        inactive = task.Task(startdate=date.Tomorrow())
        self.assertColor(inactive, wx.NamedColour('LIGHT GREY'))

