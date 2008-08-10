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

import wx, test
from unittests import dummy
from taskcoachlib import gui, config, persistence, meta


class MainWindowUnderTest(gui.MainWindow):
    def canCreateTaskBarIcon(self):
        return False


class MainWindowTest(test.wxTestCase):
    def setUp(self):
        self.settings = config.Settings(load=False)
        self.taskFile = persistence.TaskFile()
        self.mainwindow = MainWindowUnderTest(dummy.IOController(),
            self.taskFile, self.settings)
        
    def tearDown(self):
        del self.mainwindow
        super(MainWindowTest, self).tearDown()

    def testStatusBar_Show(self):
        self.settings.set('view', 'statusbar', 'True')
        self.failUnless(self.mainwindow.GetStatusBar().IsShown())

    def testStatusBar_Hide(self):
        self.settings.set('view', 'statusbar', 'False')
        self.failIf(self.mainwindow.GetStatusBar().IsShown())

    def testTitle_Default(self):
        self.assertEqual(meta.name, self.mainwindow.GetTitle())
        
    def testTitle_AfterFilenameChange(self):
        self.taskFile.setFilename('New filename')
        self.assertEqual('%s - %s'%(meta.name, self.taskFile.filename()), 
            self.mainwindow.GetTitle())

class MainWindowMaximizeTest(test.wxTestCase):
    maximized = False

    def setUp(self):
        self.settings = config.Settings(load=False)
        self.settings.setboolean('window', 'maximized', self.maximized)
        self.taskFile = persistence.TaskFile()
        self.mainwindow = MainWindowUnderTest(dummy.IOController(),
            self.taskFile, self.settings)
        self.mainwindow.Show() # Or IsMaximized() returns always False...

    def tearDown(self):
        self.mainwindow.Hide()
        del self.mainwindow
        super(MainWindowMaximizeTest, self).tearDown()


class MainWindowNotMaximizedTest(MainWindowMaximizeTest):
    def testCreate(self):
        self.failIf(self.mainwindow.IsMaximized())

    def testMaximize(self):
        self.mainwindow.Maximize()
        wx.Yield()
        self.failUnless(self.settings.getboolean('window', 'maximized'))


class MainWindowMaximizedTest(MainWindowMaximizeTest):
    maximized = True

    def testCreate(self):
        if '__WXMAC__' not in wx.PlatformInfo:
            self.failUnless(self.mainwindow.IsMaximized())
