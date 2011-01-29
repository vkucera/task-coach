'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2011 Task Coach developers <developers@taskcoach.org>

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
from taskcoachlib import gui, command, config, persistence
from taskcoachlib.domain import task, effort


class EffortEditorTest(test.wxTestCase):
    def setUp(self):
        task.Task.settings = settings = config.Settings(load=False) 
        self.taskFile = persistence.TaskFile()
        self.task = task.Task('task')
        self.effort = effort.Effort(self.task)
        self.task.addEffort(self.effort)
        self.taskFile.tasks().append(self.task)
        efforts = self.taskFile.efforts()
        self.editor = gui.dialog.editor.EffortEditor(self.frame, 
            command.EditEffortCommand(efforts, efforts), settings, efforts, self.taskFile)
        
    def testEffortEditorShowsTaskOfEffort(self):
        self.assertEqual(self.task, self.editor._interior._taskEntry.GetSelection())
