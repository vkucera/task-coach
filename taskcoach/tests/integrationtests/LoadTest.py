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

import os, sys, wx
import test, mock
from taskcoachlib.domain import task


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
        wx.GetApp().Yield() # io.open uses wx.CallAfter
        self.failUnless(self.errorDialogCalled)
