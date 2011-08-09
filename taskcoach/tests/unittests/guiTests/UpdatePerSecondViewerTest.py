'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2011 Task Coach developers <developers@taskcoach.org>

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

import test
from taskcoachlib import gui, config, persistence, patterns
from taskcoachlib.domain import base, task, effort, category, date


class MockWidget(object):
    def __init__(self):
        self.refreshedItems = []
        
    def RefreshItems(self, *items):
        self.refreshedItems.extend(items)
    

class UpdatePerSecondViewerTestsMixin(object):
    def setUp(self):
        super(UpdatePerSecondViewerTestsMixin, self).setUp()
        task.Task.settings = self.settings = config.Settings(load=False)
        self.settings.set('taskviewer', 'columns', "['timeSpent']")
        self.taskFile = persistence.TaskFile()
        self.taskList = task.sorter.Sorter(self.taskFile.tasks(), sortBy='dueDateTime')
        self.updateViewer = self.createUpdateViewer()
        self.trackedTask = task.Task(subject='tracked')
        self.trackedEffort = effort.Effort(self.trackedTask)
        self.trackedTask.addEffort(self.trackedEffort)
        self.taskList.append(self.trackedTask)

    def tearDown(self):
        super(UpdatePerSecondViewerTestsMixin, self).tearDown()
        self.taskFile.close()
        self.taskFile.stop()

    def createUpdateViewer(self):
        return self.ListViewerClass(self.frame, self.taskFile, self.settings)
        
    def testViewerHasRegisteredWithClock(self):
        self.failUnless(self.updateViewer.secondRefresher.onEveryPeriod in
            patterns.Publisher().observers(eventType='clock.second'))

    def testClockNotificationResultsInRefreshedItem(self):
        self.updateViewer.widget = MockWidget()
        self.updateViewer.secondRefresher.onEverySecond(patterns.Event('clock.second', 
            date.Clock()))
        usingTaskViewer = self.ListViewerClass != gui.viewer.EffortViewer
        expected = self.trackedTask if usingTaskViewer else self.trackedEffort
        self.assertEqual([expected], self.updateViewer.widget.refreshedItems)

    def testClockNotificationResultsInRefreshedItem_OnlyForTrackedItems(self):
        self.taskList.append(task.Task('not tracked'))
        self.updateViewer.widget = MockWidget()
        self.updateViewer.secondRefresher.onEverySecond(patterns.Event('clock.second',
            date.Clock()))
        self.assertEqual(1, len(self.updateViewer.widget.refreshedItems))

    def testStopTrackingRemovesViewerFromClockObservers(self):
        self.trackedTask.stopTracking()
        self.failIf(self.updateViewer.secondRefresher.onEverySecond in
            patterns.Publisher().observers(eventType='clock.second'))
        
    def testStopTrackingRefreshesTrackedItems(self):
        self.updateViewer.widget = MockWidget()
        self.trackedTask.stopTracking()
        expectedNrRefreshedItems = 1 if self.ListViewerClass == gui.viewer.SquareTaskViewer else 2
        self.assertEqual(expectedNrRefreshedItems, len(self.updateViewer.widget.refreshedItems))
            
    def testRemoveTrackedChildAndParentRemovesViewerFromClockObservers(self):
        parent = task.Task()
        self.taskList.append(parent)
        parent.addChild(self.trackedTask)
        self.taskList.remove(parent)
        self.failIf(self.updateViewer.secondRefresher.onEverySecond in
            patterns.Publisher().observers(eventType='clock.second'))
        
    def testCreateViewerWithTrackedItemsStartsTheClock(self):
        viewer = self.createUpdateViewer()
        self.failUnless(viewer.secondRefresher.onEveryPeriod in
            patterns.Publisher().observers(eventType='clock.second'))
        
    def testViewerDoesNotReactToAddEventsFromOtherContainers(self):
        categories = base.filter.SearchFilter(category.CategoryList())
        try:
            categories.append(category.Category('Test'))
        except AttributeError: # pragma: no cover
            self.fail("Adding a category shouldn't affect the UpdatePerSecondViewer.")

    def testViewerDoesNotReactToRemoveEventsFromOtherContainers(self):
        categories = base.filter.SearchFilter(category.CategoryList())
        categories.append(category.Category('Test'))
        try:
            categories.clear()
        except AttributeError: # pragma: no cover
            self.fail("Removing a category shouldn't affect the UpdatePerSecondViewer.")
            

class TaskListViewerUpdatePerSecondViewerTest(UpdatePerSecondViewerTestsMixin, 
        test.wxTestCase):
    ListViewerClass = gui.viewer.TaskViewer


class SquareTaskViewerUpdatePerSecondViewerTest(UpdatePerSecondViewerTestsMixin, 
        test.wxTestCase):
    ListViewerClass = gui.viewer.SquareTaskViewer


class EffortListViewerUpdatePerSecondTest(UpdatePerSecondViewerTestsMixin, 
        test.wxTestCase):
    ListViewerClass = gui.viewer.EffortViewer

