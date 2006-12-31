import test, gui, wx, config
from unittests import dummy
from gui import uicommand
from domain import task, effort, category


class MenuTestCase(test.wxTestCase):
    def setUp(self):
        self.menu = gui.menu.Menu(self.frame)
        menuBar = wx.MenuBar()
        menuBar.Append(self.menu, 'menu')
        self.frame.SetMenuBar(menuBar)


class MenuTest(MenuTestCase):
    def testLenEmptyMenu(self):
        self.assertEqual(0, len(self.menu))

    def testLenNonEmptyMenu(self):
        self.menu.AppendSeparator()
        self.assertEqual(1, len(self.menu))


class MenuWithBooleanMenuItemsTestCase(MenuTestCase):
    def setUp(self):
        super(MenuWithBooleanMenuItemsTestCase, self).setUp()
        self.settings = config.Settings(load=False)

    def assertMenuItemsChecked(self, *expectedStates):
        for command in self.commands:
            self.menu.appendUICommand(command)
        self.menu.openMenu()
        for index, shouldBeChecked in enumerate(expectedStates):
            isChecked = self.menu.FindItemByPosition(index).IsChecked()
            if shouldBeChecked:
                self.failUnless(isChecked)
            else:
                self.failIf(isChecked)


class MenuWithCheckItemsTest(MenuWithBooleanMenuItemsTestCase):
    def setUp(self):
        super(MenuWithCheckItemsTest, self).setUp()
        self.commands = [uicommand.UICheckCommand(settings=self.settings,
            section='view', setting='statusbar')]

    def testCheckedItem(self):
        self.settings.set('view', 'statusbar', 'True')
        self.assertMenuItemsChecked(True)

    def testUncheckedItem(self):
        self.settings.set('view', 'statusbar', 'False')
        self.assertMenuItemsChecked(False)


class MenuWithRadioItemsTest(MenuWithBooleanMenuItemsTestCase):
    def setUp(self):
        super(MenuWithRadioItemsTest, self).setUp()
        self.commands = [uicommand.UIRadioCommand(settings=self.settings,
                section='view', setting='toolbar', value=value) for value in
                ['None', '(16, 16)']]

    def testRadioItem_FirstChecked(self):
        self.settings.set('view', 'toolbar', 'None')
        self.assertMenuItemsChecked(True, False)

    def testRadioItem_SecondChecked(self):
        self.settings.set('view', 'toolbar', '(16, 16)')
        self.assertMenuItemsChecked(False, True)


class MockIOController:
    def __init__(self, *args, **kwargs):
        self.openCalled = False
        
    def open(self, *args, **kwargs):
        self.openCalled = True

    
class RecentFilesMenuTest(test.wxTestCase):
    def setUp(self):
        self.ioController = MockIOController()
        self.settings = config.Settings(load=False)
        self.taskList = task.TaskList()
        self.effortList = effort.EffortList(self.taskList)
        self.categories = category.CategoryList()
        self.initialFileMenuLength = len(self.createFileMenu())
        self.filename1 = 'c:/Program Files/TaskCoach/test.tsk'
        self.filename2 = 'c:/two.tsk'
        self.filenames = []
        
    def createFileMenu(self):
        return gui.menu.FileMenu(self.frame, gui.uicommand.UICommands(self.frame,
            self.ioController, None, self.settings, self.taskList, 
            self.effortList, self.categories), self.settings)
        
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
        self.uiCommands = uicommand.UICommands(self.mainWindow, None, None, 
            self.settings, self.filteredTaskList, 
            effort.EffortList(self.filteredTaskList), category.CategoryList())
        self.menu = self.createMenu()
        menuBar = wx.MenuBar()
        menuBar.Append(self.menu, 'menu')
        self.frame.SetMenuBar(menuBar)
        
    def createMainWindow(self):
        return None
        
    def createFilteredTaskList(self):
        return task.TaskList()


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
        self.categories = category.CategoryList()
        return task.filter.SearchFilter(task.filter.CategoryFilter(task.filter.ViewFilter(task.TaskList(), 
            settings=self.settings), settings=self.settings, 
            categories=self.categories), settings=self.settings)

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
        self.settings.set('view', 'tasksearchfilterstring', 'test')
        self.invokeViewAllTasks()
        self.assertEqual('', self.settings.get('view', 'tasksearchfilterstring'))
