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

import test, time, os, persistence, mock
from domain import task, category, note


class PerformanceTest(test.TestCase):
    def createTestFile(self):
        taskList = task.TaskList([task.Task('test') for i in range(self.nrTasks)])
        taskfile = file(self.taskfilename, 'w')
        taskWriter = persistence.XMLWriter(taskfile)
        taskWriter.write(taskList, category.CategoryList(), note.NoteContainer())
        taskfile.close()

    def setUp(self):
        self.nrTasks = 100
        self.taskfilename = 'performanceTest.tsk'
        self.createTestFile()

    def tearDown(self):
        self.mockApp.mainwindow.quit()
        os.remove(self.taskfilename)
        super(PerformanceTest, self).tearDown()

    def testRead(self):
        start = time.time()
        self.mockApp = mock.App()
        self.mockApp.io.open(self.taskfilename)
        end = time.time()
        self.assertEqual(self.nrTasks, len(self.mockApp.taskFile.tasks()))
        self.failUnless(end-start < self.nrTasks/10)
