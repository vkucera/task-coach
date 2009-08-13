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

import wx
import test
from taskcoachlib import gui, config
from taskcoachlib.domain import task, date


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
        overdue = task.Task(dueDate=date.Yesterday())
        self.assertColor(overdue, wx.RED)

    def testDueTodayTask(self):
        duetoday = task.Task(dueDate=date.Today())
        self.assertColor(duetoday, wx.Colour(255, 128, 0))

    def testDueTomorrow(self):
        duetomorrow = task.Task(dueDate=date.Tomorrow())
        self.assertColor(duetomorrow, wx.NamedColour('BLACK'))

    def testInactive(self):
        inactive = task.Task(startDate=date.Tomorrow())
        self.assertColor(inactive, 
            wx.Colour(*eval(self.settings.get('color', 'inactivetasks'))))

