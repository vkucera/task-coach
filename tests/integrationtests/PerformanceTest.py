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
        self.mockApp = mock.App(args=[self.taskfilename])
        end = time.time()
        self.assertEqual(self.nrTasks, len(self.mockApp.taskFile))
        self.failUnless(end-start < self.nrTasks/10)
