import test, gui, wx, config, patterns
from unittests import dummy
from domain import task, effort, date, category, note

class ViewerTest(test.wxTestCase):
    def setUp(self):
        self.settings = config.Settings(load=False)
        self.task = task.Task()
        self.taskList = task.sorter.Sorter(task.TaskList([self.task]))
        effortList = effort.EffortList(self.taskList)
        categories = category.CategoryList()
        notes = note.NoteContainer()
        self.viewer = dummy.ViewerWithDummyWidget(self.frame, self.taskList, 
            gui.uicommand.UICommands(self.frame, None, None, 
                self.settings, self.taskList, effortList, categories, notes), 
            self.settings)

    def testSelectAll(self):
        self.viewer.selectall()
        self.assertEqual([self.task], self.viewer.curselection())


class ViewerWithColumnsTest(test.wxTestCase):
    def setUp(self):
        self.settings = config.Settings(load=False)
        self.task = task.Task()
        self.taskList = task.sorter.Sorter(task.TaskList([self.task]))
        effortList = effort.EffortList(self.taskList)
        categories = category.CategoryList()
        notes = note.NoteContainer()
        self.viewerContainer = gui.viewercontainer.ViewerContainer(None, 
            self.settings, 'mainviewer')
        self.viewer = gui.viewer.TaskListViewer(self.frame, self.taskList, 
            gui.uicommand.UICommands(self.frame, None, self.viewerContainer, 
                self.settings, self.taskList, effortList, categories, notes), 
            self.settings, categories=categories)
        
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

    def testSetSortByTaskStatusFirst(self):
        self.viewer.setSortByTaskStatusFirst(True)
        self.failUnless(self.viewer.isSortByTaskStatusFirst())
        
    def testSetNoSortByTaskStatusFirst(self):
        self.viewer.setSortByTaskStatusFirst(False)
        self.failIf(self.viewer.isSortByTaskStatusFirst())


class TaskListViewerUnderTest(dummy.TaskListViewerWithDummyWidget):
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
        self.viewerContainer = gui.viewercontainer.ViewerContainer(None, 
            self.settings, 'mainviewer')
        self.viewer = TaskListViewerUnderTest(self.frame,
            self.taskList, gui.uicommand.UICommands(self.frame, None, 
                self.viewerContainer, self.settings, self.taskList, 
                effort.EffortList(self.taskList), self.categories, self.notes), 
            self.settings, categories=self.categories)

    def testGetTimeSpent(self):
        self.settings.set('view', 'timespent', 'True')
        timeSpent = self.viewer.getItemText(0, 3)
        self.assertEqual("0:00:00", timeSpent)

    def testGetTotalTimeSpent(self):
        self.settings.set('view', 'totaltimespent', 'True')
        totalTimeSpent = self.viewer.getItemText(0, 3)
        self.assertEqual("0:00:00", totalTimeSpent)

    def testChangeSubject(self):
        self.task.setSubject('New subject')
        self.assertEqual('task.subject', self.viewer.events[0].type())

    def testChangeStartDateWhileColumnShown(self):
        self.task.setStartDate(date.Yesterday())
        self.assertEqual('task.startDate', self.viewer.events[0].type())

    def testStartTracking(self):
        self.task.addEffort(effort.Effort(self.task))
        self.assertEqual('task.track.start', self.viewer.events[0].type())

    def testChangeStartDateWhileColumnNotShown(self):
        self.settings.set('view', 'startdate', 'False')
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
        self.settings.set('view', 'completiondate', 'True')
        self.task.setCompletionDate(date.Today())
        self.assertEqual('task.completionDate', self.viewer.events[0].type())

    def testChangePriorityWhileColumnNotShown(self):
        self.task.setPriority(10)
        self.failIf(self.viewer.events)

    def testChangePriorityWhileColumnShown(self):
        self.settings.set('view', 'priority', 'True')
        self.task.setPriority(10)
        self.assertEqual('task.priority', self.viewer.events[0].type())

    def testChangeTotalPriorityWhileColumnNotShown(self):
        child = task.Task()
        self.taskList.append(child)
        self.task.addChild(child)
        child.setPriority(10)
        self.failIf(self.viewer.events)

    def testChangePriorityWhileColumnShown(self):
        self.settings.set('view', 'totalpriority', 'True')
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
        self.viewerContainer = gui.viewercontainer.ViewerContainer(None, 
            settings, 'mainviewer')
        try:
            baseViewer = gui.viewer.Viewer(self.frame, taskList,
                gui.uicommand.UICommands(self.frame, None, self.viewerContainer, 
                    settings, taskList, effortList, categories, notes), {})
            self.fail('Expected NotImplementedError')
        except NotImplementedError:
            pass


class ViewerIteratorTestCase(test.wxTestCase):
    def setUp(self):
        self.settings = config.Settings(load=False)
        self.settings.set('view', 'sortby', 'subject')
        self.taskList = task.TaskList()
        self.effortList = effort.EffortList(self.taskList)
        self.categories = category.CategoryList()
        self.notes = note.NoteContainer()
        self.viewerContainer = gui.viewercontainer.ViewerContainer(None, 
            self.settings, 'mainviewer')
        self.viewer = self.createViewer()

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
        self.settings.set('view', 'tasksearchfilterstring', 'parent')
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
    

class UpdatePerSecondViewerTests(object):
    def setUp(self):
        self.settings = config.Settings(load=False)
        self.taskList = task.sorter.Sorter(task.TaskList(), sortBy='dueDate')
        self.categories = category.CategoryList()
        self.notes = note.NoteContainer()
        self.viewerContainer = gui.viewercontainer.ViewerContainer(None, 
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
        self.updateViewer.onEverySecond(patterns.Event(date.Clock(),
            'clock.second'))
        self.assertEqual([self.taskList.index(self.trackedTask)], 
            self.updateViewer.widget.refreshedItems)

    def testClockNotificationResultsInRefreshedItem_OnlyForTrackedItems(self):
        self.taskList.append(task.Task('not tracked'))
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

