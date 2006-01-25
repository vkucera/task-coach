import test, time, os, sys, taskcoach
import domain.task as task

class MockApp(taskcoach.App):
    def __init__(self, filename):
        self._options = None
        self._args = [filename]
        self.init(showSplash=False, loadSettings=False)

class PerformanceTest(test.TestCase):
    def createTestFile(self):
        taskList = task.TaskList([task.Task('test') for i in range(self.nrTasks)])
        taskfile = file(self.taskfilename, 'w')
        taskWriter = task.writer.XMLWriter(taskfile)
        taskWriter.write(taskList)
        taskfile.close()

    def setUp(self):
        self.nrTasks = 100
        self.taskfilename = 'performanceTest.tsk'
        self.createTestFile()

    def tearDown(self):
        self.mockApp.mainwindow.quit()
        os.remove(self.taskfilename)

    def testRead(self):
        start = time.time()
        self.mockApp = MockApp(self.taskfilename)
        end = time.time()
        self.assertEqual(self.nrTasks, len(self.mockApp.taskFile))
        self.failUnless(end-start < self.nrTasks/10)
