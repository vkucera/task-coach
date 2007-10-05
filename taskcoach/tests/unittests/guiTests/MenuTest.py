import test, gui, wx, config
from unittests import dummy
from gui import uicommand
from domain import task, effort, category, note


class MockViewerContainer(object):
    def getColumnUICommands(self):
        return []
    

class MenuTestCase(test.wxTestCase):
    def setUp(self):
        self.frame.viewer = MockViewerContainer()
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


class MockViewerContainer:
    def __init__(self, *args, **kwargs):
        self.__sortBy = 'subject'
        self.__ascending = True
        
    def viewerChangeEventType(self):
        return 'bla'
    
    def isSortable(self):
        return True
        
    def setSortBy(self, sortKey):
        self.__sortBy = sortKey
        
    def isSortedBy(self, sortKey):
        return sortKey == self.__sortBy

    def isSortOrderAscending(self, *args, **kwargs):
        return self.__ascending
    
    def setSortOrderAscending(self, ascending=True):
        self.__ascending = ascending

    def isSortByTaskStatusFirst(self):
        return True
    
    def isSortCaseSensitive(self):
        return True

    def getSortUICommands(self):
        return ['viewsortorder', 'viewsortcasesensitive', 
                'viewsortbystatusfirst', None, 'viewsortbysubject', 
                'viewsortbydescription']
        
    def isVisibleColumnByName(self, *args, **kwargs):
        return True
    
    def hasHideableColumns(self):
        return False
    
    def getColumnUICommands(self):
        return []
    
    def isFilteredByDueDate(self, *args, **kwargs):
        return False
    
    def isFilterable(self):
        return False
    
    def getFilterUICommands(self):
        return []
    
    def resetFilter(self):
        pass
    
    
class RecentFilesMenuTest(test.wxTestCase):
    def setUp(self):
        self.ioController = MockIOController()
        self.settings = config.Settings(load=False)
        self.taskList = task.sorter.Sorter(task.TaskList())
        self.effortList = effort.EffortList(self.taskList)
        self.categories = category.CategoryList()
        self.notes = note.NoteContainer()
        self.uiCommands = gui.uicommand.UICommands(self.frame, 
            self.ioController, MockViewerContainer(), self.settings, self.taskList, 
            self.effortList, self.categories, self.notes)
        self.initialFileMenuLength = len(self.createFileMenu())
        self.filename1 = 'c:/Program Files/TaskCoach/test.tsk'
        self.filename2 = 'c:/two.tsk'
        self.filenames = []
        
    def createFileMenu(self):
        return gui.menu.FileMenu(self.frame, self.uiCommands, self.settings)
        
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
        self.viewerContainer = MockViewerContainer()
        self.uiCommands = uicommand.UICommands(self.mainWindow, None, 
            self.viewerContainer, self.settings, self.filteredTaskList, 
            effort.EffortList(self.filteredTaskList), category.CategoryList(),
            note.NoteContainer())
        self.menuBar = wx.MenuBar()
        self.parentMenu = wx.Menu()
        self.menuBar.Append(self.parentMenu, 'parentMenu')
        self.menu = self.createMenu()
        self.parentMenu.AppendSubMenu(self.menu, 'menu')
        self.frame.SetMenuBar(self.menuBar)
        
    def createMainWindow(self):
        return None
        
    def createFilteredTaskList(self):
        return task.TaskList()


class ViewSortMenuTest(ViewMenuTestCase):
    def createMenu(self):
        self.frame.viewer = self.viewerContainer
        menu = gui.menu.SortMenu(self.frame, self.uiCommands, self.parentMenu, 
            'menu')
        menu.updateMenuInIdleTime()
        return menu
        
    def testSortOrderAscending(self):
        self.viewerContainer.setSortOrderAscending(True)
        self.menu.UpdateUI()
        self.failUnless(self.menu.FindItemByPosition(0).IsChecked())
        
    def testSortOrderDescending(self):
        self.viewerContainer.setSortOrderAscending(False)
        self.menu.UpdateUI()
        self.failIf(self.menu.FindItemByPosition(0).IsChecked())

    def testSortBySubject(self):
        self.viewerContainer.setSortBy('subject')
        self.menu.UpdateUI()
        self.failUnless(self.menu.FindItemByPosition(4).IsChecked())
        self.failIf(self.menu.FindItemByPosition(5).IsChecked())

    def testSortByDescription(self):
        self.viewerContainer.setSortBy('description')
        self.menu.UpdateUI()
        self.failIf(self.menu.FindItemByPosition(4).IsChecked())
        self.failUnless(self.menu.FindItemByPosition(5).IsChecked())
