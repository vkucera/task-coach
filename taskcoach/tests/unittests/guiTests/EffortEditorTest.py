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
from taskcoachlib import gui, config, persistence
from taskcoachlib.domain import task, effort, date
from unittests import dummy


class EffortEditorTest(test.wxTestCase):      
    def setUp(self):
        super(EffortEditorTest, self).setUp()
        task.Task.settings = self.settings = config.Settings(load=False)
        self.taskFile = persistence.TaskFile()
        self.taskList = self.taskFile.tasks()
        self.effortList = self.taskFile.efforts()
        self.taskList.extend(self.createTasks())
        self.editor = gui.dialog.editor.EffortEditor(self.frame, 
            list(self.effortList), self.settings, self.taskFile.efforts(), 
            self.taskFile, raiseDialog=False)
        
    # pylint: disable-msg=W0201,W0212
    
    def createTasks(self):
        self.task1 = task.Task('task1')
        self.effort = effort.Effort(self.task1)
        self.task1.addEffort(self.effort)
        self.task2 = task.Task('task2')
        return [self.task1, self.task2]
        
    def testCreate(self):
        self.assertEqual(self.effort.getStart().date(), 
            self.editor._interior._startDateTimeEntry.GetValue().date())
        self.assertEqual(self.effort.task(), 
            self.editor._interior._taskEntry.GetValue())    
        
    def testInvalidEffort(self):    
        self.editor._interior._stopDateTimeEntry.SetValue(date.DateTime(1900, 1, 1))
        self.editor._interior.onDateTimeEdited(dummy.Event())
        self.failUnless(self.editor._interior._invalidPeriodMessage.GetLabel())
        
    def testChangeTask(self):
        self.editor._interior._taskEntry.SetValue(self.task2)
        self.editor._interior._taskSync.onAttributeEdited(dummy.Event())
        self.assertEqual(self.task2, self.effort.task())
        self.failIf(self.effort in self.task1.efforts())
