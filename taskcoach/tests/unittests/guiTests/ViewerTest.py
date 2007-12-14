import test, gui, wx, config, patterns
from unittests import dummy
from domain import base, task, effort, date, category, note


class ViewerTest(test.wxTestCase):
    def setUp(self):
        self.settings = config.Settings(load=False)
        self.task = task.Task()
        self.taskList = task.sorter.Sorter(task.TaskList([self.task]))
        self.effortList = effort.EffortList(self.taskList)
        self.categories = category.CategoryList()
        self.notes = note.NoteContainer()
        self.viewerContainer = gui.viewercontainer.ViewerAUINotebook(self.frame, 
            self.settings, 'mainviewer')
        self.viewer = self.createViewer()
        self.viewerContainer.addViewer(self.viewer, self.viewer.title())
        
    def createViewer(self):
        return gui.viewer.TaskListViewer(self.viewerContainer, self.taskList, 
            gui.uicommand.UICommands(self.frame, None, self.viewerContainer, 
                self.settings, self.taskList, self.effortList, self.categories, 
                self.notes), 
            self.settings, categories=self.categories)
        
    def testSelectAll(self):
        self.viewer.selectall()
        self.assertEqual([self.task], self.viewer.curselection())
        
    def testFirstViewerInstanceSettingsSection(self):
        self.assertEqual('tasklistviewer', self.viewer.settingsSection())
        
    def testSecondViewerInstanceHasAnotherSettingsSection(self):
        viewer2 = self.createViewer()
        self.assertEqual('tasklistviewer1', viewer2.settingsSection())
        
    def testTitle(self):
        self.assertEqual('Task list', self.viewer.title())
        
    def testSetTitle(self):
        self.viewer.setTitle('New title')
        self.assertEqual('New title', self.viewer.title())
        
    def testSetTitleSavesTitleInSettings(self):
        self.viewer.setTitle('New title')
        self.assertEqual('New title', self.settings.get(self.viewer.settingsSection(), 'title'))        

    def testSetTitleChangesTabTitle(self):
        self.viewer.setTitle('New title')
        self.assertEqual('New title', self.viewerContainer.GetPageText(0))


class SortableViewerTest(test.TestCase):
    def setUp(self):
        self.settings = config.Settings(load=False)
        self.viewer = self.createViewer()
        
    def createViewer(self):
        viewer = gui.viewer.SortableViewer()
        viewer.settings = self.settings
        viewer.settingsSection = lambda: 'tasktreelistviewer'
        viewer.SorterClass = task.sorter.Sorter
        model = viewer.createSorter(task.TaskList())
        viewer.model = lambda: model
        return viewer
        
    def testIsSortable(self):
        self.failUnless(self.viewer.isSortable())

    def testSortBy(self):
        self.viewer.sortBy('subject')
        self.assertEqual('subject', 
            self.settings.get(self.viewer.settingsSection(), 'sortby'))

    def testSortByTwiceFlipsSortOrder(self):
        self.viewer.sortBy('subject')
        self.viewer.setSortOrderAscending(True)
        self.viewer.sortBy('subject')
        self.failIf(self.viewer.isSortOrderAscending())

    def testIsSortedBy(self):
        self.viewer.sortBy('description')
        self.failUnless(self.viewer.isSortedBy('description'))
        
    def testSortOrderAscending(self):
        self.viewer.setSortOrderAscending(True)
        self.failUnless(self.viewer.isSortOrderAscending())

    def testSortOrderDescending(self):
        self.viewer.setSortOrderAscending(False)
        self.failIf(self.viewer.isSortOrderAscending())
                
    def testSetSortCaseSensitive(self):
        self.viewer.setSortCaseSensitive(True)
        self.failUnless(self.viewer.isSortCaseSensitive())
        
    def testSetSortCaseInsensitive(self):
        self.viewer.setSortCaseSensitive(False)
        self.failIf(self.viewer.isSortCaseSensitive())
        
    def testApplySettingsWhenCreatingViewer(self):
        self.settings.set(self.viewer.settingsSection(), 'sortby', 'description')
        self.settings.set(self.viewer.settingsSection(), 'sortascending', 'True')
        anotherViewer = self.createViewer()
        anotherViewer.model().extend([task.Task(description='B'), 
                                      task.Task(description='A')])
        self.assertEqual(['A', 'B'], [t.description() for t in anotherViewer.model()])


class SortableViewerForTasksTest(test.TestCase):
    def setUp(self):
        self.settings = config.Settings(load=False)
        self.viewer = gui.viewer.SortableViewerForTasks()
        self.viewer.settings = self.settings
        self.viewer.settingsSection = lambda: 'tasktreelistviewer'
        self.viewer.model = lambda: task.sorter.Sorter(task.TaskList())

    def testSetSortByTaskStatusFirst(self):
        self.viewer.setSortByTaskStatusFirst(True)
        self.failUnless(self.viewer.isSortByTaskStatusFirst())
        
    def testSetNoSortByTaskStatusFirst(self):
        self.viewer.setSortByTaskStatusFirst(False)
        self.failIf(self.viewer.isSortByTaskStatusFirst())

      
class DummyViewer(object):
    def isTreeViewer(self):
        return False
    
    def createFilter(self, model):
        return model


class SearchableViewerUnderTest(gui.viewer.SearchableViewer, DummyViewer):
    pass   

    
class SearchableViewerTest(test.TestCase):
    def setUp(self):
        self.settings = config.Settings(load=False)
        self.viewer = self.createViewer()
        
    def createViewer(self):
        viewer = SearchableViewerUnderTest()
        viewer.settings = self.settings
        viewer.settingsSection = lambda: 'tasktreelistviewer'
        model = viewer.createFilter(task.TaskList())
        viewer.model = lambda: model
        return viewer
        
    def testIsSearchable(self):
        self.failUnless(self.viewer.isSearchable())
        
    def testDefaultSearchFilter(self):
        self.assertEqual(('', False, False), self.viewer.getSearchFilter())
        
    def testSetSearchFilterString(self):
        self.viewer.setSearchFilter('bla', matchCase=True)
        self.assertEqual('bla', self.settings.get(self.viewer.settingsSection(),
                                                  'searchfilterstring'))

    def testSetSearchFilterString_AffectsModel(self):
        self.viewer.model().append(task.Task())
        self.viewer.setSearchFilter('bla')
        self.failIf(self.viewer.model())
        
    def testSearchMatchCase(self):
        self.viewer.setSearchFilter('bla', matchCase=True)
        self.assertEqual(True, 
            self.settings.getboolean(self.viewer.settingsSection(), 
                                     'searchfiltermatchcase'))
        
    def testSearchMatchCase_AffectsModel(self):
        self.viewer.model().append(task.Task('BLA'))
        self.viewer.setSearchFilter('bla', matchCase=True)
        self.failIf(self.viewer.model())
        
    def testSearchIncludesSubItems(self):
        self.viewer.setSearchFilter('bla', includeSubItems=True)
        self.assertEqual(True, 
            self.settings.getboolean(self.viewer.settingsSection(), 
                                     'searchfilterincludesubitems'))
        
    def testSearchIncludesSubItems_AffectsModel(self):
        parent = task.Task('parent')
        child = task.Task('child')
        parent.addChild(child)
        self.viewer.model().append(parent)
        self.viewer.setSearchFilter('parent', includeSubItems=True)
        self.assertEqual(2, len(self.viewer.model()))
        
    def testApplySettingsWhenCreatingViewer(self):
        self.settings.set(self.viewer.settingsSection(), 'searchfilterstring', 'whatever')
        anotherViewer = self.createViewer()
        anotherViewer.model().append(task.Task())
        self.failIf(anotherViewer.model())


class FilterableViewerTest(test.TestCase):
    def setUp(self):
        self.viewer = gui.viewer.FilterableViewer()
        
    def testIsFilterable(self):
        self.failUnless(self.viewer.isFilterable())


class FilterableViewerForTasksUnderTest(gui.viewer.FilterableViewerForTasks, DummyViewer):
    pass
        
        
class FilterableViewerForTasks(test.TestCase):
    def setUp(self):
        self.settings = config.Settings(load=False)
        self.viewer = self.createViewer()
        
    def createViewer(self):
        viewer = FilterableViewerForTasksUnderTest()
        viewer.categories = category.CategoryList()
        viewer.settings = self.settings
        viewer.settingsSection = lambda: 'tasklistviewer'
        model = viewer.createFilter(task.TaskList())
        viewer.model = lambda: model
        return viewer
    
    def testIsFilterByDueDate_IsUnlimitedByDefault(self):
        self.failUnless(self.viewer.isFilteredByDueDate('Unlimited'))
        
    def testSetFilterByDueDate_ToToday(self):
        self.viewer.setFilteredByDueDate('Today')
        self.failUnless(self.viewer.isFilteredByDueDate('Today'))
        
    def testSetFilterByDueDate_SetsSetting(self):
        self.viewer.setFilteredByDueDate('Today')
        setting = self.settings.get(self.viewer.settingsSection(), 'tasksdue')
        self.assertEqual('Today', setting)
    
    def testSetFilterByDueDate_AffectsModel(self):
        self.viewer.model().append(task.Task(dueDate=date.Tomorrow()))
        self.viewer.setFilteredByDueDate('Today')
        self.failIf(self.viewer.model())
        
    def testSetFilterByDueDate_BackToUnlimited(self):
        self.viewer.model().append(task.Task(dueDate=date.Tomorrow()))
        self.viewer.setFilteredByDueDate('Today')
        self.viewer.setFilteredByDueDate('Unlimited')
        self.failUnless(self.viewer.model())
        
    def testIsNotHidingActiveTasksByDefault(self):
        self.failIf(self.viewer.isHidingActiveTasks())

    def testHideActiveTasks(self):
        self.viewer.hideActiveTasks()
        self.failUnless(self.viewer.isHidingActiveTasks())
    
    def testHideActiveTasks_SetsSetting(self):
        self.viewer.hideActiveTasks()
        self.failUnless(self.settings.getboolean(self.viewer.settingsSection(), 
                                                 'hideactivetasks'))

    def testHideActiveTasks_AffectsModel(self):
        self.viewer.model().append(task.Task())
        self.viewer.hideActiveTasks()
        self.failIf(self.viewer.model())
        
    def testUnhideActiveTasks(self):
        self.viewer.model().append(task.Task())
        self.viewer.hideActiveTasks()
        self.viewer.hideActiveTasks(False)
        self.failUnless(self.viewer.model())

    def testIsNotHidingInactiveTasksByDefault(self):
        self.failIf(self.viewer.isHidingInactiveTasks())

    def testHideInactiveTasks(self):
        self.viewer.hideInactiveTasks()
        self.failUnless(self.viewer.isHidingInactiveTasks())
        
    def testHideInactiveTasks_SetsSetting(self):
        self.viewer.hideInactiveTasks()    
        self.failUnless(self.settings.getboolean(self.viewer.settingsSection(), 
                                                 'hideinactivetasks'))

    def testHideInactiveTasks_AffectsModel(self):
        self.viewer.model().append(task.Task(startDate=date.Tomorrow()))
        self.viewer.hideInactiveTasks()
        self.failIf(self.viewer.model())
    
    def testUnhideInactiveTasks(self):
        self.viewer.model().append(task.Task(startDate=date.Tomorrow()))
        self.viewer.hideInactiveTasks()
        self.viewer.hideInactiveTasks(False)
        self.failUnless(self.viewer.model())
    
    def testIsNotHidingCompletedTasksByDefault(self):
        self.failIf(self.viewer.isHidingCompletedTasks())
        
    def testHideCompletedTasks(self):
        self.viewer.hideCompletedTasks()
        self.failUnless(self.viewer.isHidingCompletedTasks())
    
    def testHideCompletedTasks_SetsSetting(self):
        self.viewer.hideCompletedTasks()
        self.failUnless(self.settings.getboolean(self.viewer.settingsSection(),
                                                 'hidecompletedtasks'))
    
    def testHideCompletedTasks_AffectsModel(self):
        self.viewer.model().append(task.Task(completionDate=date.Today()))
        self.viewer.hideCompletedTasks()
        self.failIf(self.viewer.model())
        
    def testUnhideCompletedTasks(self):    
        self.viewer.model().append(task.Task(completionDate=date.Today()))
        self.viewer.hideCompletedTasks()
        self.viewer.hideCompletedTasks(False)
        self.failUnless(self.viewer.model())
        
    def testIsNotHidingOverdueTasksByDefault(self):
        self.failIf(self.viewer.isHidingOverdueTasks())
        
    def testHideOverdueTasks(self):
        self.viewer.hideOverdueTasks()
        self.failUnless(self.viewer.isHidingOverdueTasks())
        
    def testHideOverdueTasks_SetsSetting(self):
        self.viewer.hideOverdueTasks()
        self.failUnless(self.settings.getboolean(self.viewer.settingsSection(),
                                                 'hideoverduetasks'))
        
    def testHideOverdueTasks_AffectsModel(self):
        self.viewer.model().append(task.Task(dueDate=date.Yesterday()))
        self.viewer.hideOverdueTasks()
        self.failIf(self.viewer.model())
        
    def testUnhideOverdueTasks(self):
        self.viewer.model().append(task.Task(dueDate=date.Yesterday()))
        self.viewer.hideOverdueTasks()
        self.viewer.hideOverdueTasks(False)
        self.failUnless(self.viewer.model())
        
    def testIsNotHidingOverbudgetTasksByDefault(self):
        self.failIf(self.viewer.isHidingOverbudgetTasks())
        
    def testHideOverbudgetTasks(self):
        self.viewer.hideOverbudgetTasks()
        self.failUnless(self.viewer.isHidingOverbudgetTasks())
        
    def testHideOverbudgetTasks_SetsSetting(self):
        self.viewer.hideOverbudgetTasks()
        self.failUnless(self.settings.getboolean(self.viewer.settingsSection(),
                                                 'hideoverbudgettasks'))
        
    def testHideOverbudgetTasks_AffectsModel(self):
        overBudgetTask = task.Task(budget=date.TimeDelta(hours=10))
        overBudgetTask.addEffort(effort.Effort(overBudgetTask, date.Date(2000,1,1), date.Date(2000,1,2)))
        self.viewer.model().append(overBudgetTask)
        self.viewer.hideOverbudgetTasks()
        self.failIf(self.viewer.model())
        
    def testUnhideOverdueTasks(self):
        overBudgetTask = task.Task(budget=date.TimeDelta(hours=10))
        overBudgetTask.addEffort(effort.Effort(overBudgetTask, date.Date(2000,1,1), date.Date(2000,1,2)))
        self.viewer.model().append(overBudgetTask)
        self.viewer.hideOverbudgetTasks()
        self.viewer.hideOverbudgetTasks(False)
        self.failUnless(self.viewer.model())

    def testIsNotHidingCompositeTasksByDefault(self):
        self.failIf(self.viewer.isHidingCompositeTasks())
        
    def testHideCompositeTasks(self):
        self.viewer.hideCompositeTasks()
        self.failUnless(self.viewer.isHidingCompositeTasks())
        
    def testHideCompositeTasks_SetsSettings(self):
        self.viewer.hideCompositeTasks()
        self.failUnless(self.settings.getboolean(self.viewer.settingsSection(),
                                                 'hidecompositetasks'))

    def testHideCompositeTasks_AffectsModel(self):
        self.viewer.hideCompositeTasks()
        parent = task.Task()
        child = task.Task()
        parent.addChild(child)
        self.viewer.model().append(parent)
        self.assertEqual([child], self.viewer.model())
        
    def testUnhideCompositeTasks(self):
        self.viewer.hideCompositeTasks()
        parent = task.Task()
        child = task.Task()
        parent.addChild(child)
        self.viewer.model().append(parent)
        self.viewer.hideCompositeTasks(False)
        self.assertEqual(2, len(self.viewer.model()))
        
    def testClearAllFilters(self):
        self.viewer.hideActiveTasks()
        self.viewer.hideInactiveTasks()
        self.viewer.hideCompletedTasks()
        self.viewer.hideOverdueTasks()
        self.viewer.hideOverbudgetTasks()
        self.viewer.hideCompositeTasks()
        self.viewer.setFilteredByDueDate('Today')
        self.viewer.resetFilter()
        self.failIf(self.viewer.isHidingActiveTasks())
        self.failIf(self.viewer.isHidingInactiveTasks())
        self.failIf(self.viewer.isHidingCompletedTasks())
        self.failIf(self.viewer.isHidingOverdueTasks())
        self.failIf(self.viewer.isHidingOverbudgetTasks())
        self.failIf(self.viewer.isHidingCompositeTasks())
        self.failUnless(self.viewer.isFilteredByDueDate('Unlimited'))     
        
    def testApplySettingsWhenCreatingViewer(self):
        self.settings.set(self.viewer.settingsSection(), 'hidecompletedtasks', 'True')
        anotherViewer = self.createViewer()
        anotherViewer.model().append(task.Task(completionDate=date.Today()))
        self.failIf(anotherViewer.model())   


class TaskListViewerUnderTest(gui.viewer.TaskListViewer):
    def __init__(self, *args, **kwargs):
        super(TaskListViewerUnderTest, self).__init__(*args, **kwargs)
        self.events = []

    def onAttributeChanged(self, event):
        super(TaskListViewerUnderTest, self).onAttributeChanged(event)
        self.events.append(event)


class EffortListViewerUnderTest(dummy.EffortListViewerWithDummyWidget):
    def __init__(self, *args, **kwargs):
        super(EffortListViewerUnderTest, self).__init__(*args, **kwargs)
        self.events = []

    def onAttributeChanged(self, event):
        super(EffortListViewerUnderTest, self).onAttributeChanged(event)


class EffortPerDayViewerUnderTest(dummy.EffortPerDayViewerWithDummyWidget):
    def __init__(self, *args, **kwargs):
        super(EffortPerDayViewerUnderTest, self).__init__(*args, **kwargs)
        self.events = []

    def onAttributeChanged(self, event):
        super(EffortPerDayViewerUnderTest, self).onAttributeChanged(event)


class TaskListViewerTest(test.wxTestCase):
    def setUp(self):
        self.task = task.Task()
        self.settings = config.Settings(load=False)
        self.categories = category.CategoryList()
        self.notes = note.NoteContainer()
        self.taskList = task.sorter.Sorter(task.TaskList([self.task]))
        self.viewerContainer = gui.viewercontainer.ViewerNotebook(self.frame, 
            self.settings, 'mainviewer')
        self.viewer = TaskListViewerUnderTest(self.frame,
            self.taskList, gui.uicommand.UICommands(self.frame, None, 
                self.viewerContainer, self.settings, self.taskList, 
                effort.EffortList(self.taskList), self.categories, self.notes), 
            self.settings, categories=self.categories)

    def showColumn(self, columnName, show=True):
        self.viewer.showColumnByName(columnName, show)
        
    def testGetTimeSpent(self):
        self.showColumn('timeSpent')
        timeSpent = self.viewer.getItemText(0, 3)
        self.assertEqual("0:00:00", timeSpent)

    def testGetTotalTimeSpent(self):
        self.showColumn('totalTimeSpent')
        totalTimeSpent = self.viewer.getItemText(0, 3)
        self.assertEqual("0:00:00", totalTimeSpent)

    def testChangeSubject(self):
        self.task.setSubject('New subject')
        self.assertEqual(task.Task.subjectChangedEventType(), 
                         self.viewer.events[0].type())

    def testChangeStartDateWhileColumnShown(self):
        self.task.setStartDate(date.Yesterday())
        self.assertEqual('task.startDate', self.viewer.events[0].type())

    def testStartTracking(self):
        self.task.addEffort(effort.Effort(self.task))
        self.assertEqual('task.track.start', self.viewer.events[0].type())

    def testChangeStartDateWhileColumnNotShown(self):
        self.showColumn('startDate', False)
        self.task.setStartDate(date.Yesterday())
        self.assertEqual(1, len(self.viewer.events))

    def testChangeDueDate(self):
        self.task.setDueDate(date.Today())
        self.assertEqual('task.dueDate', self.viewer.events[0].type())

    def testChangeCompletionDateWhileColumnNotShown(self):
        self.task.setCompletionDate(date.Today())
        # We still get an event for the subject column:
        self.assertEqual('task.completionDate', self.viewer.events[0].type())

    def testChangeCompletionDateWhileColumnShown(self):
        self.showColumn('completionDate')
        self.task.setCompletionDate(date.Today())
        self.assertEqual('task.completionDate', self.viewer.events[0].type())

    def testChangePriorityWhileColumnNotShown(self):
        self.task.setPriority(10)
        self.failIf(self.viewer.events)

    def testChangePriorityWhileColumnShown(self):
        self.showColumn('priority')
        self.task.setPriority(10)
        self.assertEqual('task.priority', self.viewer.events[0].type())

    def testChangeTotalPriorityWhileColumnNotShown(self):
        child = task.Task()
        self.taskList.append(child)
        self.task.addChild(child)
        child.setPriority(10)
        self.failIf(self.viewer.events)

    def testChangePriorityWhileColumnShown(self):
        self.showColumn('totalPriority')
        child = task.Task()
        self.taskList.append(child)
        self.task.addChild(child)
        child.setPriority(10)
        self.assertEqual('task.totalPriority', self.viewer.events[0].type())

    # Test all attributes...

    def testGetColorForDefaultTask(self):
        self.assertEqual(wx.BLACK, self.viewer.getColor(self.task))

    def testGetColorForCompletedTask(self):
        self.task.setCompletionDate()
        self.assertEqual(wx.GREEN, self.viewer.getColor(self.task))
        
    def testColorForOverDueTask(self):
        self.task.setDueDate(date.Yesterday())
        self.assertEqual(wx.RED, self.viewer.getColor(self.task))
        
    def testColorForTaskDueToday(self):
        self.task.setDueDate(date.Today())
        expectedColor = wx.Color(*eval(self.settings.get('color', 'duetodaytasks')))
        self.assertEqual(expectedColor, self.viewer.getColor(self.task))

    def testColorForInactiveTasks(self):
        self.task.setStartDate(date.Tomorrow())
        expectedColor = wx.Color(*eval(self.settings.get('color', 'inactivetasks')))
        self.assertEqual(expectedColor, self.viewer.getColor(self.task))


class ViewerBaseClassTest(test.wxTestCase):
    def testNotImplementedError(self):
        taskList = task.TaskList()
        effortList = effort.EffortList(taskList)
        categories = category.CategoryList()
        notes = note.NoteContainer()
        settings = config.Settings(load=False)
        self.viewerContainer = gui.viewercontainer.ViewerNotebook(self.frame, 
            settings, 'mainviewer')
        try:
            baseViewer = gui.viewer.Viewer(self.frame, taskList,
                gui.uicommand.UICommands(self.frame, None, self.viewerContainer, 
                    settings, taskList, effortList, categories, notes), {}, settingsSection='bla')
            self.fail('Expected NotImplementedError')
        except NotImplementedError:
            pass


class ViewerIteratorTestCase(test.wxTestCase):
    def setUp(self):
        self.settings = config.Settings(load=False)
        self.taskList = task.TaskList()
        self.effortList = effort.EffortList(self.taskList)
        self.categories = category.CategoryList()
        self.notes = note.NoteContainer()
        self.viewerContainer = gui.viewercontainer.ViewerNotebook(self.frame, 
            self.settings, 'mainviewer')
        self.viewer = self.createViewer()
        self.viewer.sortBy('subject')

    def getItemsFromIterator(self):
        result = []
        for item in self.viewer.visibleItems():
            result.append(item)
        return result


class ViewerIteratorTests(object):
    def testEmptyModel(self):
        self.assertEqual([], self.getItemsFromIterator())
        
    def testOneItem(self):
        self.taskList.append(task.Task())
        self.assertEqual(self.taskList, self.getItemsFromIterator())
        
    def testOneParentAndOneChild(self):
        parent = task.Task('Z')
        child = task.Task('A')
        parent.addChild(child)
        self.taskList.append(parent)
        self.assertEqual(self.expectedParentAndChildOrder(parent, child), 
                         self.getItemsFromIterator())

    def testOneParentOneChildAndOneGrandChild(self):
        parent = task.Task('a-parent')
        child = task.Task('b-child')
        grandChild = task.Task('c-grandchild')
        parent.addChild(child)
        child.addChild(grandChild)
        self.taskList.append(parent)
        self.assertEqual([parent, child, grandChild], 
                         self.getItemsFromIterator())
    
    def testThatTasksNotInModelAreExcluded(self):
        parent = task.Task('parent')
        child = task.Task('child')
        parent.addChild(child)
        self.taskList.append(parent)
        self.viewer.setSearchFilter('parent', True)
        self.assertEqual([parent], self.getItemsFromIterator())
        
    
class TreeViewerIteratorTest(ViewerIteratorTestCase, ViewerIteratorTests):
    def createViewer(self):
        return gui.viewer.TaskTreeViewer(self.frame, self.taskList,
            gui.uicommand.UICommands(self.frame, None, self.viewerContainer, 
                self.settings, self.taskList, self.effortList, self.categories, 
                self.notes), 
            self.settings, categories=self.categories)
    
    def expectedParentAndChildOrder(self, parent, child):
        return [parent, child]
            
        
class ListViewerIteratorTest(ViewerIteratorTestCase, ViewerIteratorTests):
    def createViewer(self):
        return gui.viewer.TaskListViewer(self.frame, self.taskList,
            gui.uicommand.UICommands(self.frame, None, self.viewerContainer, 
                self.settings, self.taskList, self.effortList, self.categories, 
                self.notes), 
            self.settings, categories=self.categories)

    def expectedParentAndChildOrder(self, parent, child):
        return [child, parent]


class CompositeEffortListViewerTest(test.wxTestCase):
    def setUp(self):
        taskList = task.TaskList()
        self.settings = config.Settings(load=False)
        aTask = task.Task()
        aTask.addEffort(effort.Effort(aTask))
        taskList.append(aTask)
        self.viewer = dummy.EffortPerDayViewerWithDummyWidget(self.frame, 
            taskList, {}, self.settings)
            
    def testGetItemText_TimeSpent(self):
        self.assertEqual('0:00:00', self.viewer.getItemText(0, 2))
        
    def testGetItemText_Revenue(self):
        self.assertEqual('0.00', self.viewer.getItemText(0, 3))


class MockWidget(object):
    def __init__(self):
        self.refreshedItems = []
        
    def RefreshItem(self, index):
        self.refreshedItems.append(index)
    
    def curselection(self):
        return []


class UpdatePerSecondViewerTests(object):
    def setUp(self):
        self.settings = config.Settings(load=False)
        self.taskList = task.sorter.Sorter(task.TaskList(), sortBy='dueDate')
        self.categories = category.CategoryList()
        self.notes = note.NoteContainer()
        self.viewerContainer = gui.viewercontainer.ViewerNotebook(self.frame, 
            self.settings, 'mainviewer')
        self.updateViewer = self.createUpdateViewer()
        self.trackedTask = task.Task(subject='tracked')
        self.trackedTask.addEffort(effort.Effort(self.trackedTask))
        self.taskList.append(self.trackedTask)
        
    def createUpdateViewer(self):
        return self.ListViewerClass(self.frame, self.taskList, 
            gui.uicommand.UICommands(self.frame, None, self.viewerContainer, 
                self.settings, self.taskList, effort.EffortList(self.taskList), 
                self.categories, self.notes), 
            self.settings, categories=self.categories)
        
    def testViewerHasRegisteredWithClock(self):
        self.failUnless(self.updateViewer.onEverySecond in
            patterns.Publisher().observers(eventType='clock.second'))

    def testClockNotificationResultsInRefreshedItem(self):
        self.updateViewer.widget = MockWidget()
        self.updateViewer.onEverySecond(patterns.Event(date.Clock(),
            'clock.second'))
        self.assertEqual([self.taskList.index(self.trackedTask)], 
            self.updateViewer.widget.refreshedItems)

    def testClockNotificationResultsInRefreshedItem_OnlyForTrackedItems(self):
        self.taskList.append(task.Task('not tracked'))
        self.updateViewer.widget = MockWidget()
        self.updateViewer.onEverySecond(patterns.Event(date.Clock(),
            'clock.second'))
        self.assertEqual(1, len(self.updateViewer.widget.refreshedItems))

    def testStopTrackingRemovesViewerFromClockObservers(self):
        self.trackedTask.stopTracking()
        self.failIf(self.updateViewer.onEverySecond in
            patterns.Publisher().observers(eventType='clock.second'))
            
    def testRemoveTrackedChildAndParentRemovesViewerFromClockObservers(self):
        parent = task.Task()
        self.taskList.append(parent)
        parent.addChild(self.trackedTask)
        self.taskList.remove(parent)
        self.failIf(self.updateViewer.onEverySecond in
            patterns.Publisher().observers(eventType='clock.second'))
        
    def testCreateViewerWithTrackedItemsStartsTheClock(self):
        viewer = self.createUpdateViewer()
        self.failUnless(viewer.onEverySecond in
            patterns.Publisher().observers(eventType='clock.second'))


class TaskListViewerUpdatePerSecondViewerTest(UpdatePerSecondViewerTests, 
        test.wxTestCase):
    ListViewerClass = TaskListViewerUnderTest


class EffortListViewerUpdatePerSecondTest(UpdatePerSecondViewerTests, 
        test.wxTestCase):
    ListViewerClass = EffortListViewerUnderTest


class EffortPerDayViewerUpdatePerSecondTest(UpdatePerSecondViewerTests, 
        test.wxTestCase):
    ListViewerClass = EffortPerDayViewerUnderTest


