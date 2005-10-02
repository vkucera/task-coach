import test, gui, wx, config, dummy, task
from gui import uicommand

class DummyCommand(uicommand.UICommand):
    def onActivateCommand(self, event):
        self.event = event

class DummyCheckCommand(uicommand.UICheckCommand):
    def __init__(self, *args, **kwargs):
        super(DummyCheckCommand, self).__init__(section='test',
            setting='test', *args, **kwargs)

    def onCommandActivate(self, event):
        self.event = event

class DummyRadioCommand(uicommand.UIRadioCommand):
    def __init__(self, *args, **kwargs):
        super(DummyRadioCommand, self).__init__(section='test',
            setting='test', value='on', *args, **kwargs)

    def onCommandActivate(self, event):
        self.event = event

class DummySettings(config.Settings):
    def __init__(self, value, *args, **kwargs):
        super(DummySettings, self).__init__(*args, **kwargs)
        self.add_section('test')
        self.set('test', 'test', str(value))

    def read(self, *args):
        pass

class MenuTest(test.wxTestCase):
    def setUp(self):
        self.menu = gui.menu.Menu(self.frame)
        self.command = DummyCommand()

    def testLenEmptyMenu(self):
        self.assertEqual(0, len(self.menu))

    def testLenNonEmptyMenu(self):
        self.menu.appendUICommand(self.command)
        self.menu.AppendSeparator()
        self.assertEqual(2, len(self.menu))

    def testAppendUICommandDoesNotInvokeTheCommand(self):
        self.menu.appendUICommand(self.command)
        self.failIf(hasattr(self.command, 'event'))

    def testCheckedCheckCommandIsNotInvoked(self):
        settings = DummySettings(True)
        command = DummyCheckCommand(settings=settings)
        self.menu.appendUICommand(command)
        self.failIf(hasattr(self.command, 'event'))

    def testUncheckedUICheckCommandIsInvoked(self):
        settings = DummySettings(False)
        command = DummyCheckCommand(settings=settings)
        id = self.menu.appendUICommand(command)
        self.assertEqual(id, command.event.GetId())

    def testUncheckedUIRadioCommandIsNotInvoked(self):
        settings = DummySettings('off')
        command = DummyRadioCommand(settings=settings)
        self.menu.appendUICommand(command)
        self.failIf(hasattr(self.command, 'event'))

    def testCheckedUIRadioCommandIsInvoked(self):
        settings = DummySettings('on')
        command = DummyRadioCommand(settings=settings)
        id = self.menu.appendUICommand(command)
        self.assertEqual(id, command.event.GetId())


class MockIOController:
    def __init__(self, *args, **kwargs):
        self.openCalled = False
        
    def open(self, *args, **kwargs):
        self.openCalled = True

    
class RecentFilesMenuTest(test.wxTestCase):
    def setUp(self):
        self.ioController = MockIOController()
        self.settings = config.Settings(load=False)
        self.initialFileMenuLength = len(self.createFileMenu())
        self.filename1 = 'c:/Program Files/TaskCoach/test.tsk'
        self.filename2 = 'c:/two.tsk'
        self.filenames = []
        
    def createFileMenu(self):
        return gui.menu.FileMenu(self.frame, dummy.DummyUICommands(self.ioController), 
                                 self.settings)
        
    def setRecentFilesAndCreateMenu(self, *filenames):
        self.addRecentFiles(*filenames)
        self.menu = self.createFileMenu()
    
    def addRecentFiles(self, *filenames):
        self.filenames.extend(filenames)
        self.settings.set('file', 'recentfiles', str(list(self.filenames)))
        
    def assertRecentFileMenuItems(self, *expectedFilenames):
        expectedFilenames = expectedFilenames or self.filenames
        self.openMenu()
        numberOfMenuItemsAdded = len(expectedFilenames)
        if numberOfMenuItemsAdded > 0:
            numberOfMenuItemsAdded += 1 # the extra separator
        self.assertEqual(self.initialFileMenuLength + numberOfMenuItemsAdded, len(self.menu))
        for index, expectedFilename in enumerate(expectedFilenames):
            menuItem = self.menu.FindItemByPosition(self.initialFileMenuLength-1+index)
            # Apparently the '&' can also be a '_' (seen on Ubuntu)
            expectedLabel = u'&%d %s'%(index+1, expectedFilename)
            self.assertEqual(expectedLabel[1:], menuItem.GetText()[1:])
    
    def openMenu(self):
        self.menu.onOpenMenu(wx.MenuEvent(menu=self.menu))
        
    def testNoRecentFiles(self):
        self.setRecentFilesAndCreateMenu()
        self.assertRecentFileMenuItems()
        
    def testOneRecentFileWhenCreatingMenu(self):
        self.setRecentFilesAndCreateMenu(self.filename1)
        self.assertRecentFileMenuItems()
        
    def testTwoRecentFilesWhenCreatingMenu(self):
        self.setRecentFilesAndCreateMenu(self.filename1, self.filename2)
        self.assertRecentFileMenuItems()
                
    def testAddRecentFileAfterCreatingMenu(self):
        self.setRecentFilesAndCreateMenu()
        self.addRecentFiles(self.filename1)
        self.assertRecentFileMenuItems()
        
    def testOneRecentFileWhenCreatingMenuAndAddOneRecentFileAfterCreatingMenu(self):
        self.setRecentFilesAndCreateMenu(self.filename1)
        self.addRecentFiles(self.filename2)
        self.assertRecentFileMenuItems()
        
    def testOpenARecentFile(self):
        self.setRecentFilesAndCreateMenu(self.filename1)
        self.openMenu()
        menuItem = self.menu.FindItemByPosition(self.initialFileMenuLength-1)
        self.menu.invokeMenuItem(menuItem)
        self.failUnless(self.ioController.openCalled)
        
    def testNeverShowMoreThanTheMaximumNumberAllowed(self):
        self.setRecentFilesAndCreateMenu(self.filename1, self.filename2)
        self.settings.set('file', 'maxrecentfiles', '1')
        self.assertRecentFileMenuItems(self.filename1)


class ViewMenuTestCase(test.wxTestCase):
    def setUp(self):
        self.settings = config.Settings(load=False)
        self.mainWindow = self.createMainWindow()
        self.filteredTaskList = self.createFilteredTaskList()
        self.uiCommands = uicommand.UICommands(self.mainWindow, None, None, self.settings, 
                                               self.filteredTaskList, None)
        self.menu = self.createMenu()
        
    def createMainWindow(self):
        return None
        
    def createFilteredTaskList(self):
        return None


class ViewSortMenuTest(ViewMenuTestCase):
    def createMenu(self):
        return gui.menu.SortMenu(self.frame, self.uiCommands)
        
    def testSortOrderAscending(self):
        self.settings.set('view', 'sortascending', 'True')
        self.menu.openMenu()
        self.failUnless(self.menu.FindItemByPosition(0).IsChecked())
        
    def testSortOrderDescending(self):
        self.settings.set('view', 'sortascending', 'False')
        self.menu.openMenu()
        self.failIf(self.menu.FindItemByPosition(0).IsChecked())

    def testSortBySubject(self):
        self.settings.set('view', 'sortby', 'subject')
        self.menu.openMenu()
        self.failIf(self.menu.FindItemByPosition(3).IsChecked())
        self.failUnless(self.menu.FindItemByPosition(4).IsChecked())


class ViewAllTasksTest(ViewMenuTestCase):
    def createMenu(self):
        return gui.menu.ViewMenu(self.frame, self.uiCommands)

    def createMainWindow(self):
        return dummy.MainWindow()
        
    def createFilteredTaskList(self):
        return task.filter.SearchFilter(task.filter.CategoryFilter(task.filter.ViewFilter(task.TaskList(), settings=self.settings)))

    def invokeViewAllTasks(self):
        self.menu.invokeMenuItem(self.menu.FindItemByPosition(0))
        
    def testInvokingViewAllTasksResetsTasksDue(self):
        self.settings.set('view', 'tasksdue', 'Today')
        self.invokeViewAllTasks()
        self.failUnless('Unlimited', self.settings.get('view', 'tasksdue'))
        
    def testInvokingViewAllTasksResetsViewCompletedTasks(self):
        self.settings.set('view', 'completedtasks', 'False')
        self.invokeViewAllTasks()
        self.failUnless(self.settings.getboolean('view', 'completedtasks'))
        
    def testInvokingViewAllTasksResetsSearchFilter(self):
        self.filteredTaskList.setSubject('test')
        self.invokeViewAllTasks()
        self.assertEqual('', self.filteredTaskList.getSubject())
