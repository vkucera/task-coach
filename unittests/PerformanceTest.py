import test, time, os, sys, task, taskcoach

class MockApp(taskcoach.App):
    def __init__(self):
        self.init(showSplash=False)

class PerformanceTest(test.TestCase):
    def createTestFile(self):
        taskList = [task.Task()]*self.nrTasks
        taskfile = file(self.taskfilename, 'w')
        taskWriter = task.TaskWriter(taskfile)
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
        sys.argv = ['taskcoach.py', self.taskfilename] 
        start = time.time()
        self.mockApp = MockApp()
        end = time.time()
        self.assertEqual(self.nrTasks, len(self.mockApp.taskFile))
        self.failUnless(end-start < self.nrTasks/10)
