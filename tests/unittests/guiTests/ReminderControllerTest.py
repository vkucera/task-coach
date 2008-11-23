'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>

Task Coach is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Task Coach is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import test
from taskcoachlib import gui, patterns, config
from taskcoachlib.domain import task, date


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
        self.reminderController = ReminderControllerUnderTest(self.taskList,
            config.Settings(load=False))
        self.nowDateTime = date.DateTime.now()
        self.reminderDateTime = self.nowDateTime + date.TimeDelta(hours=1)
        
    def testSetTaskReminderAddsClockEventToPublisher(self):
        self.task.setReminder(self.reminderDateTime)
        self.assertEqual([self.reminderController.onReminder], 
            patterns.Publisher().observers(eventType=\
                date.Clock.eventType(self.reminderDateTime)))

    def testClockTriggersReminder(self):
        self.task.setReminder(self.reminderDateTime)
        date.Clock().notify(now=self.reminderDateTime)
        self.assertEqual([self.task], 
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
        
    def testMarkTaskCompletedRemovesReminder(self):
        self.task.setReminder(self.reminderDateTime)
        self.task.setCompletionDate(date.Today())
        self.assertEqual([], patterns.Publisher().observers(eventType=\
                date.Clock.eventType(self.reminderDateTime)))
        
    def dummyCloseEvent(self, snoozeTimeDelta=None):
        class DummySnoozeOptions(object):
            Selection = 0
            def GetClientData(self, *args):
                return snoozeTimeDelta
        class DummyDialog(object):
            task = self.task
            openTaskAfterClose = False
            snoozeOptions = DummySnoozeOptions()
            def Destroy(self):
                pass
        class DummyEvent(object):
            EventObject = DummyDialog()
        return DummyEvent()
    
    def testOnCloseReminderResetsReminder(self):
        self.task.setReminder(self.reminderDateTime)
        self.reminderController.onCloseReminderDialog(self.dummyCloseEvent())
        self.assertEqual(None, self.task.reminder())

    def testOnCloseReminderSetsReminder(self):
        self.task.setReminder(self.reminderDateTime)
        oneHour = date.TimeDelta(hours=1)
        self.reminderController.onCloseReminderDialog(self.dummyCloseEvent(oneHour))
        self.failUnless(abs(self.nowDateTime + oneHour - self.task.reminder()) < date.TimeDelta(seconds=5))
               

class ReminderControllerTest_TwoTasksWithSameReminderDateTime(test.TestCase):
    def setUp(self):
        self.taskList = task.TaskList()
        self.reminderDateTime = date.DateTime.now() + date.TimeDelta(hours=1)
        self.task1 = task.Task('Task 1', reminder=self.reminderDateTime)
        self.task2 = task.Task('Task 2', reminder=self.reminderDateTime)
        self.taskList.extend([self.task1, self.task2])
        self.reminderController = ReminderControllerUnderTest(self.taskList,
            config.Settings(load=False))

    def testClockNotificationResultsInTwoMessages(self):
        date.Clock().notify(now=self.reminderDateTime)
        self.assertEqualLists([self.task1, self.task2], 
            self.reminderController.messages)

    def testChangeOneReminder(self):
        self.task1.setReminder(self.reminderDateTime + date.TimeDelta(hours=1))
        date.Clock().notify(now=self.reminderDateTime + date.TimeDelta(hours=1))
        self.assertEqualLists([self.task1, self.task2], 
                              self.reminderController.messages)
                         
    def testChangeOneReminderDoesNotAffectTheOther(self):
        self.task1.setReminder(self.reminderDateTime + date.TimeDelta(hours=1))
        date.Clock().notify(now=self.reminderDateTime)
        self.assertEqual([self.task2], self.reminderController.messages)
                                                  
    def testRemoveOneTaskDoesNotAffectTheOther(self):
        self.taskList.remove(self.task1)
        date.Clock().notify(now=self.reminderDateTime)
        self.assertEqual([self.task2], self.reminderController.messages)
        
