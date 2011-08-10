# -*- coding: utf-8 -*-

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

import test, StringIO
from taskcoachlib import persistence, config, gui
from taskcoachlib.domain import task, date


class TodoTxtWriterTestCase(test.wxTestCase):
    def setUp(self):
        self.settings = task.Task.settings = config.Settings(load=False)
        self.file = StringIO.StringIO()
        self.writer = persistence.TodoTxtWriter(self.file, 'whatever.tsk')
        self.settings.set('taskviewer', 'treemode', 'False')
        self.taskFile = persistence.TaskFile()
        self.viewer = gui.viewer.TaskViewer(self.frame, self.taskFile, self.settings)

    def testNoTasksAndCategories(self):
        self.writer.write(self.viewer, self.settings, False)
        self.assertEqual('', self.file.getvalue())
        
    def testOneTask(self):
        self.taskFile.tasks().append(task.Task(subject='Get cheese'))
        self.writer.write(self.viewer, self.settings, False)
        self.assertEqual('Get cheese\n', self.file.getvalue())
        
    def testTwoTasks(self):
        self.taskFile.tasks().append(task.Task(subject='Get cheese'))
        self.taskFile.tasks().append(task.Task(subject='Paint house'))
        self.writer.write(self.viewer, self.settings, False)
        self.assertEqual('Get cheese\nPaint house\n', self.file.getvalue())
        
    def testNonAsciiSubject(self):
        self.taskFile.tasks().append(task.Task(subject='Call Jérôme'))
        self.writer.write(self.viewer, self.settings, False)
        self.assertEqual('Call Jérôme\n', self.file.getvalue())

    def testSorting(self):
        self.taskFile.tasks().append(task.Task(subject='Get cheese'))
        self.taskFile.tasks().append(task.Task(subject='Paint house'))
        self.viewer.sortBy('subject')
        self.viewer.setSortOrderAscending(False)
        self.writer.write(self.viewer, self.settings, False)
        self.assertEqual('Paint house\nGet cheese\n', self.file.getvalue())
        
    def testTaskPriorityIsWrittenAsLetter(self):
        self.taskFile.tasks().append(task.Task(subject='Get cheese', priority=1))
        self.writer.write(self.viewer, self.settings, False)
        self.assertEqual('(A) Get cheese\n', self.file.getvalue())
        
    def testTaskPriorityHigherThanZIsIgnored(self):
        self.taskFile.tasks().append(task.Task(subject='Get cheese', priority=27))
        self.writer.write(self.viewer, self.settings, False)
        self.assertEqual('Get cheese\n', self.file.getvalue())
        
    def testStartDate(self):
        self.taskFile.tasks().append(task.Task(subject='Get cheese', 
                                               startDateTime=date.DateTime(2027,1,23,15,34,12)))
        self.writer.write(self.viewer, self.settings, False)
        self.assertEqual('2027-01-23 Get cheese\n', self.file.getvalue())
        
        