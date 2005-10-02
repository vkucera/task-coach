import test, taskcoach, os, task


class MockApp(taskcoach.App):
    def __init__(self, filename):
        self._options = self._args = None
        self.init(filename)

    def init(self, filename):
        super(MockApp, self).init(showSplash=False, loadSettings=False)
        self.taskFile.setFilename(filename)
        self.parent = task.Task()
        self.child = task.Task()
        self.parent.addChild(self.child)
        self.taskFile.extend([self.parent])


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
        self.mockApp.io.open(self.filename)
        self.assertEqual(2, len(self.mockApp.taskFile))

    def testSaveSelection_Child(self):
        self.mockApp.io.save()
        self.mockApp.io.saveselection([self.mockApp.child], self.filename2)
        self.mockApp.io.close()
        self.mockApp.io.open(self.filename2)
        self.assertEqual(1, len(self.mockApp.taskFile))

    def testSaveSelection_Parent(self):
        self.mockApp.io.save()
        self.mockApp.io.saveselection([self.mockApp.parent], self.filename2)
        self.mockApp.io.close()
        self.mockApp.io.open(self.filename2)
        self.assertEqual(2, len(self.mockApp.taskFile))
        
    def testSaveAndMerge(self):
        mockApp2 = MockApp(self.filename2)
        mockApp2.io.save()
        self.mockApp.io.merge(self.filename2)
        self.assertEqual(4, len(self.mockApp.taskFile))
        mockApp2.mainwindow.quit()
