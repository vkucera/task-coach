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

import test
from taskcoachlib import gui, command, config, persistence
from taskcoachlib.domain import task, effort, date


class EffortEditorTest(test.wxTestCase):
    def setUp(self):
        task.Task.settings = self.settings = config.Settings(load=False) 
        self.taskFile = persistence.TaskFile()
        self.task = task.Task('task')
        self.effort = effort.Effort(self.task)
        self.task.addEffort(self.effort)
        self.task2 = task.Task('task2')
        self.taskFile.tasks().extend([self.task, self.task2])
        self.editor = self.createEditor()

    def createEditor(self):
        sortedEfforts = effort.EffortSorter(self.taskFile.efforts())
        editEffortCommand = command.EditEffortCommand(sortedEfforts, sortedEfforts)
        return gui.dialog.editor.EffortEditor(self.frame, editEffortCommand, 
            self.settings, self.taskFile.efforts(), self.taskFile,  
            raiseDialog=False)        

    def testEffortEditorShowsTaskOfEffort(self):
        self.assertEqual(self.task, self.editor._interior._taskEntry.GetSelection())

    def testCreate(self):
        # pylint: disable-msg=W0212
        self.assertEqual(self.effort.getStart().date(), 
            self.editor._interior._startEntry.get().date())
        self.assertEqual(self.effort.task().subject(), 
            self.editor._interior._taskEntry.GetValue())

    def testOK(self):
        stop = self.effort.getStop()
        self.editor.ok()
        self.assertEqual(stop, self.effort.getStop())
        
    def testInvalidEffort(self):
        self.effort.setStop(date.DateTime(1900, 1, 1))
        self.editor = self.createEditor()
        # pylint: disable-msg=W0212
        self.editor._interior.preventNegativeEffortDuration()
        self.failIf(self.editor._buttons.GetAffirmativeButton().IsEnabled())
        
    def testChangeTask(self):
        self.editor._interior._taskEntry.SetStringSelection('task2') # pylint: disable-msg=W0212
        self.editor.ok()
        self.assertEqual(self.task2, self.effort.task())
        self.failIf(self.effort in self.task.efforts())
