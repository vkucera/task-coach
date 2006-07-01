import test, gui
import domain.task as task

class ReminderControllerTest(test.TestCase):
    def setUp(self):
        self.taskList = task.TaskList()
        self.task = task.Task()
        self.taskList.append(self.task)
        self.reminderController = gui.ReminderController(self.taskList)

    def testNoReminders(self):
        self.assertEqual([], self.reminderController.reminders())
