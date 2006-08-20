import test, gui, wx, config, persistence, meta
from unittests import dummy
import domain.task as task


class MainWindowUnderTest(gui.MainWindow):
    def canCreateTaskBarIcon(self):
        return False


class MainWindowTest(test.wxTestCase):
    def setUp(self):
        self.settings = config.Settings(load=False)
        self.taskFile = persistence.TaskFile()
        self.mainwindow = MainWindowUnderTest(dummy.IOController(),
            self.taskFile, [], self.settings)

    def testStatusBar_Show(self):
        self.settings.set('view', 'statusbar', 'True')
        self.failUnless(self.mainwindow.GetStatusBar().IsShown())

    def testStatusBar_Hide(self):
        self.settings.set('view', 'statusbar', 'False')
        self.failIf(self.mainwindow.GetStatusBar().IsShown())

    def testFilterSideBar_Show(self):
        self.settings.set('view', 'filtersidebar', 'True')
        self.failUnless(self.mainwindow.filterSideBarWindow.IsShown())
        
    def testFilterSideBar_Hide(self):
        self.settings.set('view', 'filtersidebar', 'False')
        self.failIf(self.mainwindow.filterSideBarWindow.IsShown())

    def testTitle_Default(self):
        self.assertEqual(meta.name, self.mainwindow.GetTitle())
        
    def testTitle_AfterFilenameChange(self):
        self.taskFile.setFilename('New filename')
        self.assertEqual('%s - %s'%(meta.name, self.taskFile.filename()), 
            self.mainwindow.GetTitle())
