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

import test, wx, meta, gui.taskbaricon, config
from domain import task, effort, date


class MainWindowMock:
    def restore(self):
        pass

    quit = restore
    

class TaskBarIconTestCase(test.TestCase):
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
            
            
class TaskBarIconTest(TaskBarIconTestCase):
    def testIcon_NoTasks(self):
        self.failUnless(self.icon.IsIconInstalled())
        
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
        
        
class TaskBarIconTooltipTest(TaskBarIconTestCase):
    def assertTooltip(self, text):
        expectedTooltip = meta.name
        if text:
            expectedTooltip += ' - %s'%text
        self.assertEqual(expectedTooltip, self.icon.tooltip())
   
    def testNoTasks(self):
        self.assertTooltip('')
        
    def testOneTaskNoDueDate(self):
        self.taskList.append(task.Task())
        self.assertTooltip('')

    def testOneTaskDueToday(self):
        self.taskList.append(task.Task(dueDate=date.Today()))
        self.assertTooltip('one task due today')
        
    def testTwoTasksDueToday(self):
        self.taskList.append(task.Task(dueDate=date.Today()))
        self.taskList.append(task.Task(dueDate=date.Today()))
        self.assertTooltip('2 tasks due today')
        
    def testOneTasksOverdue(self):
        self.taskList.append(task.Task(dueDate=date.Yesterday()))
        self.assertTooltip('one task overdue')
        
    def testTwoTasksOverdue(self):
        self.taskList.append(task.Task(dueDate=date.Yesterday()))
        self.taskList.append(task.Task(dueDate=date.Yesterday()))
        self.assertTooltip('2 tasks overdue')
        
    def testOneTaskDueTodayAndOneTaskOverdue(self):
        self.taskList.append(task.Task(dueDate=date.Yesterday()))
        self.taskList.append(task.Task(dueDate=date.Today()))
        self.assertTooltip('one task overdue, one task due today')
        
    def testStartTracking(self):
        activeTask = task.Task()
        self.taskList.append(activeTask)
        activeTask.addEffort(effort.Effort(activeTask))
        self.assertTooltip('tracking effort for one task')

    def testStopTracking(self):
        activeTask = task.Task()
        self.taskList.append(activeTask)
        activeEffort = effort.Effort(activeTask)
        activeTask.addEffort(activeEffort)
        activeTask.removeEffort(activeEffort)
        self.assertTooltip('')
        
    def testTrackingTwoTasks(self):
        for i in range(2):
            activeTask = task.Task()
            self.taskList.append(activeTask)
            activeTask.addEffort(effort.Effort(activeTask))
        self.assertTooltip('tracking effort for 2 tasks')

    def testRemoveTask(self):
        newTask = task.Task()
        self.taskList.append(newTask)
        self.taskList.remove(newTask)
        self.assertTooltip('')
