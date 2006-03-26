import test, taskcoach, os, sys, mock
import domain.task as task


class LoadTest(test.TestCase):
    def setUp(self):
        self.filename = 'LoadTest.tsk'
        taskfile = file(self.filename, 'w')
        taskfile.writelines(['Line 1\n', 'Line 2\n'])
        taskfile.close()
        self.errorDialogCalled = False
        self.mockApp = mock.App()

    def tearDown(self):
        self.mockApp.mainwindow.quit()
        if os.path.isfile(self.filename):
            os.remove(self.filename)

    def mockErrorDialog(self, *args, **kwargs):
        self.errorDialogCalled = True

    def testLoadInvalidFileDoesNotAffectFile(self):
        self.mockApp.io.open(self.filename, showerror=self.mockErrorDialog)
        lines = file(self.filename, 'r').readlines()
        self.failUnless(self.errorDialogCalled)
        self.assertEqual(2, len(lines)) 
        self.assertEqual('Line 1\n', lines[0])
        self.assertEqual('Line 2\n', lines[1])


