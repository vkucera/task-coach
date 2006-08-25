import test, gui, patterns
import unittests.asserts as asserts
import domain.task as task
import domain.date as date

class ReminderControllerUnderTest(gui.ReminderController):
    def __init__(self, *args, **kwargs):
        self.messages = []
        super(ReminderControllerUnderTest, self).__init__(*args, **kwargs)
        
    def showReminderMessage(self, message):
        self.messages.append(message)


class ReminderControllerTest(test.TestCase):
    def setUp(self):
        self.taskList = task.TaskList()
        self.task = task.Task('Task')
        self.taskList.append(self.task)
        self.reminderController = ReminderControllerUnderTest(self.taskList)
        self.reminderDateTime = date.DateTime.now() + date.TimeDelta(hours=1)
        
    def testSetTaskReminderAddsClockEventToPublisher(self):
        self.task.setReminder(self.reminderDateTime)
        self.assertEqual([self.reminderController.onReminder], 
            patterns.Publisher().observers(eventType=\
                date.Clock.eventType(self.reminderDateTime)))

    def testClockTriggersReminder(self):
        self.task.setReminder(self.reminderDateTime)
        date.Clock().notify(now=self.reminderDateTime)
        self.assertEqual([self.task.subject()], 
                         self.reminderController.messages)
        
    def testAfterReminderClockEventIsRemovedFromPublisher(self):
        self.task.setReminder(self.reminderDateTime)
        date.Clock().notify(now=self.reminderDateTime)
        self.assertEqual([], patterns.Publisher().observers(eventType=\
                date.Clock.eventType(self.reminderDateTime)))
        
    def testAddTaskWithReminderAddsClockEventToPublisher(self):
        taskWithReminder = task.Task('Task with reminder', 
                                     reminder=self.reminderDateTime)
        self.taskList.append(taskWithReminder)
        self.assertEqual([self.reminderController.onReminder], 
            patterns.Publisher().observers(eventType=\
                date.Clock.eventType(self.reminderDateTime)))
                
    def testRemoveTaskWithReminderRemovesClockEventFromPublisher(self):
        self.task.setReminder(self.reminderDateTime)
        self.taskList.remove(self.task)
        self.assertEqual([], patterns.Publisher().observers(eventType=\
                date.Clock.eventType(self.reminderDateTime)))
                
    def testChangeReminderRemovesOldReminder(self):
        self.task.setReminder(self.reminderDateTime)
        self.task.setReminder(self.reminderDateTime + date.TimeDelta(hours=1))
        self.assertEqual([], patterns.Publisher().observers(eventType=\
                date.Clock.eventType(self.reminderDateTime)))


class ReminderControllerTest_TwoTasksWithSameReminderDateTime(test.TestCase,
        asserts.TaskListAsserts):
    def setUp(self):
        self.taskList = task.TaskList()
        self.reminderDateTime = date.DateTime.now() + date.TimeDelta(hours=1)
        self.task1 = task.Task('Task 1', reminder=self.reminderDateTime)
        self.task2 = task.Task('Task 2', reminder=self.reminderDateTime)
        self.taskList.extend([self.task1, self.task2])
        self.reminderController = ReminderControllerUnderTest(self.taskList)

    def testClockNotificationResultsInTwoMessages(self):
        date.Clock().notify(now=self.reminderDateTime)
        self.assertEqualLists([self.task1.subject(), self.task2.subject()], 
            self.reminderController.messages)

    def testChangeOneReminder(self):
        self.task1.setReminder(self.reminderDateTime + date.TimeDelta(hours=1))
        date.Clock().notify(now=self.reminderDateTime + date.TimeDelta(hours=1))
        self.assertEqualLists([task.subject() for task in self.task1, 
            self.task2], self.reminderController.messages)
                         
    def testChangeOneReminderDoesNotAffectTheOther(self):
        self.task1.setReminder(self.reminderDateTime + date.TimeDelta(hours=1))
        date.Clock().notify(now=self.reminderDateTime)
        self.assertEqual([self.task2.subject()], 
                         self.reminderController.messages)
                                                  
    def testRemoveOneTaskDoesNotAffectTheOther(self):
        self.taskList.remove(self.task1)
        date.Clock().notify(now=self.reminderDateTime)
        self.assertEqual([self.task2.subject()], 
                         self.reminderController.messages)
        
