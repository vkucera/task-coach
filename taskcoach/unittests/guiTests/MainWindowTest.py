import test, gui, wx, config, persistence
from unittests import dummy
import domain.task as task
import domain.effort as effort

class MainWindowUnderTest(gui.MainWindow):
    def canCreateTaskBarIcon(self):
        return False


class MainWindowTest(test.wxTestCase):
    def setUp(self):
        self.settings = config.Settings(load=False)
        taskList = task.filter.SearchFilter(persistence.TaskFile(), 
            settings=self.settings)
        self.mainwindow = MainWindowUnderTest(dummy.IOController(), taskList,
            taskList, effort.EffortList(taskList), self.settings)

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
