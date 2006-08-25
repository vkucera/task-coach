import test, gui, wx, config, patterns
from unittests import dummy
from domain import task, effort, date

class ViewerTest(test.wxTestCase):
    def setUp(self):
        self.settings = config.Settings(load=False)
        self.task = task.Task()
        self.taskList = task.sorter.Sorter(task.TaskList([self.task]), 
            settings=self.settings)
        self.viewer = dummy.ViewerWithDummyWidget(self.frame,
            self.taskList, dummy.DummyUICommands(), self.settings)

    def testSelectAll(self):
        self.viewer.selectall()
        self.assertEqual([self.task], self.viewer.curselection())


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
        self.taskList = task.sorter.Sorter(task.TaskList([self.task]), 
            settings=self.settings)
        self.viewer = TaskListViewerUnderTest(self.frame,
            self.taskList, dummy.DummyUICommands(), self.settings)

    def testGetTimeSpent(self):
        timeSpent = self.viewer.getItemText(0, self.viewer.columns()[7])
        self.assertEqual("0:00:00", timeSpent)

    def testGetTotalTimeSpent(self):
        totalTimeSpent = self.viewer.getItemText(0, self.viewer.columns()[8])
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
        self.failIf(self.viewer.events)

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

class ViewerBaseClassTest(test.wxTestCase):
    def testNotImplementedError(self):
        taskList = task.TaskList()
        try:
            baseViewer = gui.viewer.Viewer(self.frame, taskList,
                dummy.DummyUICommands(), {})
            self.fail('Expected NotImplementedError')
        except NotImplementedError:
            pass


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
        self.assertEqual('0:00:00', 
                         self.viewer.getItemText(0, self.viewer.columns()[2]))
        
    def testGetItemText_Revenue(self):
        self.assertEqual('0.00', 
                         self.viewer.getItemText(0, self.viewer.columns()[3]))
    

class UpdatePerSecondViewerTests(object):
    def setUp(self):
        self.settings = config.Settings(load=False)
        self.taskList = task.sorter.Sorter(task.TaskList(), settings=self.settings)
        self.updateViewer = self.ListViewerClass(self.frame, self.taskList, 
            dummy.DummyUICommands(), self.settings)
        self.trackedTask = task.Task(subject='tracked')
        self.trackedTask.addEffort(effort.Effort(self.trackedTask))
        self.taskList.append(self.trackedTask)

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
        self.assertEqual([self.taskList.index(self.trackedTask)], 
            self.updateViewer.widget.refreshedItems)

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


class TaskListViewerUpdatePerSecondViewerTest(UpdatePerSecondViewerTests, 
        test.wxTestCase):
    ListViewerClass = TaskListViewerUnderTest


class EffortListViewerUpdatePerSecondTest(UpdatePerSecondViewerTests, 
        test.wxTestCase):
    ListViewerClass = EffortListViewerUnderTest


class EffortPerDayViewerUpdatePerSecondTest(UpdatePerSecondViewerTests, 
        test.wxTestCase):
    ListViewerClass = EffortPerDayViewerUnderTest

