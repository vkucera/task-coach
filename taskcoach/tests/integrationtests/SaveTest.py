import test, taskcoach, os, mock
from domain import task


class SaveTest(test.TestCase):
    def setUp(self):
        self.filename = 'SaveTest.tsk'
        self.filename2 = 'SaveTest2.tsk'
        self.mockApp = mock.App()
        self.mockApp.addTasks()

    def tearDown(self):
        self.mockApp.io.save()
        self.mockApp.mainwindow.quit()
        for filename in [self.filename, self.filename2]:
            if os.path.isfile(filename):
                os.remove(filename)
        super(SaveTest, self).tearDown()

    def testSave(self):
        self.mockApp.io.saveas(self.filename)
        self.mockApp.io.open(self.filename)
        self.assertEqual(2, len(self.mockApp.taskFile))

    def testSaveSelection_Child(self):
        self.mockApp.io.saveas(self.filename)
        self.mockApp.io.saveselection([self.mockApp.child], self.filename2)
        self.mockApp.io.close()
        self.mockApp.io.open(self.filename2)
        self.assertEqual(1, len(self.mockApp.taskFile))

    def testSaveSelection_Parent(self):
        self.mockApp.io.saveas(self.filename)
        self.mockApp.io.saveselection([self.mockApp.parent], self.filename2)
        self.mockApp.io.close()
        self.mockApp.io.open(self.filename2)
        self.assertEqual(2, len(self.mockApp.taskFile))
        
    def testSaveAndMerge(self):
        mockApp2 = mock.App()
        mockApp2.addTasks()
        mockApp2.io.saveas(self.filename2)
        self.mockApp.io.merge(self.filename2)
        self.assertEqual(4, len(self.mockApp.taskFile))
        self.mockApp.io.saveas(self.filename)
        mockApp2.mainwindow.quit()
