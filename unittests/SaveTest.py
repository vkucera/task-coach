import test, taskcoach, os, task


class MockApp(taskcoach.App):
    def __init__(self, filename):
        self.init(filename)

    def init(self, filename):
        super(MockApp, self).init(showSplash=False, load=False)
        self.taskFile.setFilename(filename)
        parent = task.Task()
        child = task.Task()
        parent.addChild(child)
        self.taskFile.extend([parent, child])
        self.mainwindow.viewer.select([parent])
        self.parent = parent
        self.child = child


class SaveTest(test.TestCase):
    def setUp(self):
        self.filename = 'SaveTest.tsk'
        self.filename2 = 'SaveTest2.tsk'
        self.mockApp = MockApp(self.filename)

    def tearDown(self):
        self.mockApp.io.save()
        self.mockApp.mainwindow.quit()
        for filename in [self.filename, self.filename2]:
            if os.path.isfile(filename):
                os.remove(filename)

    def testSave(self):
        self.mockApp.io.save()
        lines = file(self.filename, 'r').readlines()
        self.assertEqual(3, len(lines)) # 1 version line + 2 tasks

    def testSaveSelection_Child(self):
        self.mockApp.io.saveselection([self.mockApp.child], self.filename)
        lines = file(self.filename, 'r').readlines()
        self.assertEqual(2, len(lines)) # 1 version line + 1 task

    def testSaveSelection_Parent(self):
        self.mockApp.io.saveselection([self.mockApp.parent], self.filename)
        lines = file(self.filename, 'r').readlines()
        self.assertEqual(3, len(lines)) # 1 version line + 2 tasks

    def testSaveAndMerge(self):
        mockApp2 = MockApp(self.filename2)
        mockApp2.io.save()
        self.mockApp.io.merge(self.filename2)
        self.assertEqual(4, len(self.mockApp.taskFile))
        mockApp2.mainwindow.quit()
