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
        
    def testCompletedTaskWithoutCompletionDate(self):
        now = date.Now()
        self.reader.readFile(StringIO.StringIO('x Do dishes\n'), now=lambda: now)
        self.failUnless(list(self.tasks)[0].completed())
        self.assertEqual(now, list(self.tasks)[0].completionDateTime())
        
    def testCompletedTaskWithCompletionDate(self):
        self.reader.readFile(StringIO.StringIO('X 2011-02-22 Do dishes\n'))
        self.failUnless(list(self.tasks)[0].completed())
        self.assertEqual(date.DateTime(2011, 2, 22, 0, 0, 0), 
                         list(self.tasks)[0].completionDateTime())
        
    def testTaskWithStartAndCompletionDate(self):
        self.reader.readFile(StringIO.StringIO('X 2011-02-22 2011-02-21 Do dishes\n'))
        self.failUnless(list(self.tasks)[0].completed())
        self.assertEqual(date.DateTime(2011, 2, 22, 0, 0, 0), 
                         list(self.tasks)[0].completionDateTime())
        self.assertEqual(date.DateTime(2011, 2, 21, 0, 0, 0), 
                         list(self.tasks)[0].startDateTime())
    
    def testTaskWithSimpleContext(self):
        self.reader.readFile(StringIO.StringIO('Order pizza @phone\n'))
        phone = list(self.categories)[0]
        self.assertEqual('phone', phone.subject())
        pizza = list(self.tasks)[0]
        self.assertEqual(set([pizza]), phone.categorizables())
        self.assertEqual(set([phone]), pizza.categories())

    def testTaskWithSimpleProject(self):
        self.reader.readFile(StringIO.StringIO('Order pizza +phone\n'))
        phone = list(self.categories)[0]
        self.assertEqual('phone', phone.subject())
        pizza = list(self.tasks)[0]
        self.assertEqual(set([pizza]), phone.categorizables())
        self.assertEqual(set([phone]), pizza.categories())
        
    def testTaskWithPlusSign(self):
        self.reader.readFile(StringIO.StringIO('Order pizza + drink\n'))
        pizza = list(self.tasks)[0]
        self.assertEqual('Order pizza + drink', pizza.subject())
        self.assertEqual(0, len(self.categories))
        
    def testTaskWithAtSign(self):
        self.reader.readFile(StringIO.StringIO('Mail frank@niessink.com\n'))
        mail = list(self.tasks)[0]
        self.assertEqual('Mail frank@niessink.com', mail.subject())
        self.assertEqual(0, len(self.categories))
        
    def testTwoTasksWithTheSameContext(self):
        self.reader.readFile(StringIO.StringIO('Order pizza @phone\nCall mom @phone\n'))
        self.assertEqual(1, len(self.categories))
        phone = list(self.categories)[0]
        self.assertEqual(set(self.tasks), phone.categorizables())
        self.assertEqual([set([phone]), set([phone])], 
                         [t.categories() for t in self.tasks])
        
    def testTaskWithSubcategoryAsContext(self):
        self.reader.readFile(StringIO.StringIO('Order pizza @home->phone\n'))
        home = [c for c in self.categories if not c.parent()][0]
        self.assertEqual('home', home.subject())
        phone = home.children()[0]
        self.assertEqual('phone', phone.subject())
        pizza = list(self.tasks)[0]
        self.assertEqual(set([pizza]), phone.categorizables())
        self.assertEqual(set([phone]), pizza.categories())
        
    def testTwoTasksWithTheSameSubcategory(self):
        self.reader.readFile(StringIO.StringIO('Order pizza @home->phone\nOrder flowers @home->phone\n'))
        home = [c for c in self.categories if not c.parent()][0]
        self.assertEqual('home', home.subject())
        phone = home.children()[0]
        self.assertEqual('phone', phone.subject())
        self.assertEqual(set(self.tasks), phone.categorizables())
        for eachTask in self.tasks:
            self.assertEqual(set([phone]), eachTask.categories())
            
    def testTaskWithMultipleContexts(self):
        self.reader.readFile(StringIO.StringIO('Order pizza @phone @food\n'))
        self.assertEqual(2, len(self.categories))
        pizza = list(self.tasks)[0]
        self.assertEqual(set(self.categories), pizza.categories())
        
    def testContextBeforeTask(self):
        self.reader.readFile(StringIO.StringIO('@phone Order pizza\n'))
        self.assertEqual(1, len(self.categories))

    def testProjectBeforeTask(self):
        self.reader.readFile(StringIO.StringIO('+phone Order pizza\n'))
        self.assertEqual(1, len(self.categories))
        
    def testAutomaticallyCreateParentTask(self):
        self.reader.readFile(StringIO.StringIO('Project->Activity'))
        self.assertEqual(2, len(self.tasks))
        parent = [t for t in self.tasks if not t.parent()][0]
        self.assertEqual('Project', parent.subject())
        self.assertEqual('Activity', parent.children()[0].subject())
        
    def testAutomaticallyCreateParentTask_WithSpaces(self):
        self.reader.readFile(StringIO.StringIO('Project -> Activity'))
        self.assertEqual(2, len(self.tasks))
        parent = [t for t in self.tasks if not t.parent()][0]
        self.assertEqual('Project', parent.subject())
        self.assertEqual('Activity', parent.children()[0].subject())