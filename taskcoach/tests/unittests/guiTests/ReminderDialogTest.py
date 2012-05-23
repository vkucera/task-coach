'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2012 Task Coach developers <developers@taskcoach.org>

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
from taskcoachlib.gui import dialog
from taskcoachlib import config
from taskcoachlib.domain import task, effort


class DummyEvent(object):
    def Skip(self):
        pass


class ReminderDialogTest(test.TestCase):
    def setUp(self):
        self.settings = config.Settings(load=False)
        task.Task.settings = self.settings
        self.aTask = task.Task('subject')
        self.taskList = task.TaskList([self.aTask])
        self.effortList = effort.EffortList(self.taskList)
        
    def createReminderDialog(self):
        return dialog.reminder.ReminderDialog(self.aTask, 
            self.taskList, self.effortList, self.settings, None)

    def testRememberZeroSnoozeTime(self):
        self.reminderDialog = self.createReminderDialog()
        self.reminderDialog.snoozeOptions.SetSelection(0)
        self.reminderDialog.onClose(DummyEvent())        
        self.assertEqual(0, self.settings.getint('view', 'defaultsnoozetime'))

    def testRememberSnoozeTime(self):
        self.reminderDialog = self.createReminderDialog()
        self.reminderDialog.snoozeOptions.SetSelection(2)
        self.reminderDialog.onClose(DummyEvent())        
        self.assertEqual(10, self.settings.getint('view', 'defaultsnoozetime'))

    def testUseDefaultSnoozeTime(self):
        self.settings.set('view', 'defaultsnoozetime', '15')
        reminderDialog = self.createReminderDialog()
        self.assertEqual('15 minutes', reminderDialog.snoozeOptions.GetStringSelection())
        
    def testDontUseDefaultSnoozeTimeWhenItsNotInTheListOfOptions(self):
        self.settings.set('view', 'defaultsnoozetime', '17')
        reminderDialog = self.createReminderDialog()
        self.assertEqual('5 minutes', reminderDialog.snoozeOptions.GetStringSelection())
        