import test, taskcoach, os, sys, mock, wx
from domain import task


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
        super(LoadTest, self).tearDown()

    def mockErrorDialog(self, *args, **kwargs):
        self.errorDialogCalled = True

    def testLoadInvalidFileDoesNotAffectFile(self):
        self.mockApp.io.open(self.filename, showerror=self.mockErrorDialog)
        lines = file(self.filename, 'r').readlines()
        self.failUnless(self.errorDialogCalled)
        self.assertEqual(2, len(lines)) 
        self.assertEqual('Line 1\n', lines[0])
        self.assertEqual('Line 2\n', lines[1])

    def testLoadNonExistingFileGivesErrorMessage(self):
        self.mockApp.io.open("I don't exist.tsk", 
                             showerror=self.mockErrorDialog,
                             fileExists=lambda filename: False)
        wx.Yield() # io.open uses wx.CallAfter
        self.failUnless(self.errorDialogCalled)
