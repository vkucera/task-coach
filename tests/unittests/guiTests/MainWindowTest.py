'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2009 Frank Niessink <frank@niessink.com>

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
from taskcoachlib import gui, config, persistence, meta

class MockViewer(wx.Frame):
    def title(self):
        return ''
    
    def bitmap(self):
        return ''
    
    def statusMessages(self):
        return '', ''
    
    def settingsSection(self):
        return 'taskviewer'
    
    def selectEventType(self):
        return ''


class MainWindowUnderTest(gui.MainWindow):
    def createWindowComponents(self):
        # Create only the window components we really need for the tests
        self.createViewerContainer()
        self.viewer.addViewer(MockViewer(None))
        self.createStatusBar()
    

class DummyIOController:
    def needSave(self, *args, **kwargs):
        return False # pragma: no cover


class MainWindowTestCase(test.wxTestCase):
    def setUp(self):
        super(MainWindowTestCase, self).setUp()
        self.settings = config.Settings(load=False)
        self.setSettings()
        self.taskFile = persistence.TaskFile()
        self.mainwindow = MainWindowUnderTest(DummyIOController(),
            self.taskFile, self.settings)
        
    def setSettings(self):
        pass

    def tearDown(self):
        del self.mainwindow
        super(MainWindowTestCase, self).tearDown()
        
        
class MainWindowTest(MainWindowTestCase):
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

        

class MainWindowMaximizeTestCase(MainWindowTestCase):
    def setUp(self):
        super(MainWindowMaximizeTestCase, self).setUp()
        self.mainwindow.Show() # Or IsMaximized() returns always False...
        
    def setSettings(self):
        self.settings.setboolean('window', 'maximized', self.maximized)


class MainWindowNotMaximizedTest(MainWindowMaximizeTestCase):
    maximized = False
    
    def testCreate(self):
        self.failIf(self.mainwindow.IsMaximized())

    def testMaximize(self):
        self.mainwindow.Maximize()
        if '__WXGTK__' == wx.Platform: 
            wx.YieldIfNeeded() # pragma: no cover
        else:
            wx.Yield() # pragma: no cover
        self.failUnless(self.settings.getboolean('window', 'maximized'))


class MainWindowMaximizedTest(MainWindowMaximizeTestCase):
    maximized = True

    @test.skipOnPlatform('__WXMAC__')
    def testCreate(self):
        self.failUnless(self.mainwindow.IsMaximized()) # pragma: no cover


class MainWindowIconizedTest(MainWindowTestCase):
    def setUp(self):
        super(MainWindowIconizedTest, self).setUp()        
        if '__WXGTK__' == wx.Platform:
            wx.Yield() # pragma: no cover
            
    def setSettings(self):
        self.settings.set('window', 'starticonized', 'Always')
        
    def testIsIconized(self):
        self.failUnless(self.mainwindow.IsIconized())
                        
    def testWindowSize(self):
        # On Mac OS X, the window height is increased by 29 pixels in 
        # "real life" but not when running this test...
        height = 500
        if wx.Platform == '__WXMAC__':
            height -= 29 # pragma: no cover
        self.assertEqual((700, height), 
                         eval(self.settings.get('window', 'size')))
        
    def testWindowSizeShouldnotChangeWhenReceivingChangeSizeEvent(self):
        event = wx.SizeEvent((100, 20))
        process = self.mainwindow.ProcessEvent
        if '__WXGTK__' == wx.Platform:
            wx.CallAfter(process, event) # pragma: no cover
        else:
            process(event) # pragma: no cover
        height = 500
        if wx.Platform == '__WXMAC__':
            height -= 29 # pragma: no cover
        self.assertEqual((700, height), eval(self.settings.get('window', 'size')))

