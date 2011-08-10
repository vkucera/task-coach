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
from taskcoachlib import persistence, config
from taskcoachlib.domain import task, category, date


class TodoTxtReaderTestCase(test.TestCase):
    def setUp(self):
        task.Task.settings = config.Settings(load=False)
        self.tasks = task.TaskList()
        self.categories = category.CategoryList() 
        self.reader = persistence.TodoTxtReader(self.tasks, self.categories)
        
    def testEmptyFile(self):
        self.reader.readFile(StringIO.StringIO())
        self.failIf(self.tasks)
        
    def testReadOneTask(self):
        self.reader.readFile(StringIO.StringIO('Get milk\n'))
        self.assertEqual('Get milk', list(self.tasks)[0].subject())
        
    def testReadTwoTasks(self):
        self.reader.readFile(StringIO.StringIO('Get milk\nDo laundry\n'))
        self.assertEqual(set(['Get milk', 'Do laundry']),
                         set([t.subject() for t in self.tasks]))
        
    def testTaskWithPriority(self):
        self.reader.readFile(StringIO.StringIO('(A) Get milk\n'))
        self.assertEqual(1, list(self.tasks)[0].priority())
        
    def testTaskWithStartDate(self):
        self.reader.readFile(StringIO.StringIO('2011-01-31 Get milk\n'))
        self.assertEqual(date.DateTime(2011, 1, 31, 0, 0, 0), 
                         list(self.tasks)[0].startDateTime())
        
    def testTaskWithPriorityAndStartDate(self):
        self.reader.readFile(StringIO.StringIO('(Z) 2011-01-31 Get milk\n'))
        self.assertEqual(26, list(self.tasks)[0].priority())
        self.assertEqual(date.DateTime(2011, 1, 31, 0, 0, 0), 
                         list(self.tasks)[0].startDateTime())
        
    