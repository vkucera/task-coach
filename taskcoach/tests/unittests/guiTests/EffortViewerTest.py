'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2012 Task Coach developers <developers@taskcoach.org>

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

from taskcoachlib import gui, config, persistence, render
from taskcoachlib.domain import task, effort, date
from unittests import dummy
import test
import wx


class EffortViewerUnderTest(gui.viewer.EffortViewer):  # pylint: disable-msg=W0223
    def createWidget(self):
        return dummy.DummyWidget(self)
    
    def columns(self):
        return []


class EffortViewerForSpecificTasksTest(test.wxTestCase):
    def setUp(self):
        super(EffortViewerForSpecificTasksTest, self).setUp()
        self.settings = config.Settings(load=False)
        task.Task.settings = self.settings
        self.taskFile = persistence.TaskFile()
        self.task1 = task.Task('Task 1')
        self.task2 = task.Task('Task 2')
        self.taskFile.tasks().extend([self.task1, self.task2])
        self.effort1 = effort.Effort(self.task1, date.DateTime(2006, 1, 1),
            date.DateTime(2006, 1, 2))
        self.task1.addEffort(self.effort1)
        self.effort2 = effort.Effort(self.task2, date.DateTime(2006, 1, 2),
            date.DateTime(2006, 1, 3))
        self.task2.addEffort(self.effort2)
        self.viewer = EffortViewerUnderTest(self.frame, self.taskFile,  
            self.settings, tasksToShowEffortFor=task.TaskList([self.task1]))

    def tearDown(self):
        super(EffortViewerForSpecificTasksTest, self).tearDown()
        self.taskFile.close()
        self.taskFile.stop()

    def testViewerShowsOnlyEffortForSpecifiedTask(self):
        self.assertEqual([self.effort1], self.viewer.presentation())
        
    def testEffortEditorDoesUseAllTasks(self):
        dialog = self.viewer.newItemDialog()
        self.assertEqual(2, len(dialog._taskFile.tasks()))  # pylint: disable-msg=W0212
        
    def testViewerKeepsShowingOnlyEffortForSpecifiedTasksWhenSwitchingAggregation(self):
        self.viewer.showEffortAggregation('week')
        self.assertEqual(2, len(self.viewer.presentation()))
        
        
class EffortViewerStatusMessageTest(test.wxTestCase):
    def setUp(self):
        super(EffortViewerStatusMessageTest, self).setUp()
        self.settings = config.Settings(load=False)
        self.taskFile = persistence.TaskFile()
        self.task = task.Task()
        self.taskFile.tasks().append(self.task)
        self.effort1 = effort.Effort(self.task, date.DateTime(2006, 1, 1),
            date.DateTime(2006, 1, 2))
        self.effort2 = effort.Effort(self.task, date.DateTime(2006, 1, 2),
            date.DateTime(2006, 1, 3))
        self.viewer = EffortViewerUnderTest(self.frame, self.taskFile,  
            self.settings)

    def tearDown(self):
        super(EffortViewerStatusMessageTest, self).tearDown()
        self.taskFile.close()
        self.taskFile.stop()

    def assertStatusMessages(self, message1, message2):
        self.assertEqual((message1, message2), self.viewer.statusMessages())
        
    def testStatusMessage_EmptyTaskList(self):
        self.taskFile.tasks().clear()
        self.assertStatusMessages('Effort: 0 selected, 0 visible, 0 total', 
            'Status: 0 tracking')
            
    def testStatusMessage_OneTaskNoEffort(self):
        self.assertStatusMessages('Effort: 0 selected, 0 visible, 0 total', 
            'Status: 0 tracking')
        
    def testStatusMessage_OneTaskOneEffort(self):
        self.task.addEffort(self.effort1)
        self.assertStatusMessages('Effort: 0 selected, 1 visible, 1 total', 
            'Status: 0 tracking')
            
    def testStatusMessage_OneTaskTwoEfforts(self):
        self.task.addEffort(self.effort1)
        self.task.addEffort(self.effort2)
        self.assertStatusMessages('Effort: 0 selected, 2 visible, 2 total', 
            'Status: 0 tracking')
            
    def testStatusMessage_OneTaskOneActiveEffort(self):
        self.task.addEffort(effort.Effort(self.task))
        self.assertStatusMessages('Effort: 0 selected, 1 visible, 1 total',
            'Status: 1 tracking')
        
    def testStatusMessageInAggregatedMode_OneTaskNoEffort(self):
        self.viewer.showEffortAggregation('day')
        self.assertStatusMessages('Effort: 0 selected, 0 visible, 0 total', 
            'Status: 0 tracking')

    def testStatusMessageInAggregateMode_OneTaskOneEffort(self):
        self.viewer.showEffortAggregation('day')
        self.task.addEffort(self.effort1)
        self.assertStatusMessages('Effort: 0 selected, 2 visible, 1 total', 
            'Status: 0 tracking')

    def testStatusMessageInAggregateMode_OneTaskTwoEfforts(self):
        self.viewer.showEffortAggregation('day')
        self.task.addEffort(self.effort1)
        self.task.addEffort(self.effort2)
        self.assertStatusMessages('Effort: 0 selected, 4 visible, 2 total', 
            'Status: 0 tracking')


class EffortViewerTest(test.wxTestCase):
    def setUp(self):
        super(EffortViewerTest, self).setUp()
        self.settings = config.Settings(load=False)
        self.taskFile = persistence.TaskFile()
        self.task = task.Task('task')
        self.taskFile.tasks().append(self.task)
        self.effort1 = effort.Effort(self.task, date.DateTime(2006, 1, 1),
            date.DateTime(2006, 1, 2))
        self.effort2 = effort.Effort(self.task, date.DateTime(2006, 1, 2),
            date.DateTime(2006, 1, 3))
        self.viewer = gui.viewer.EffortViewer(self.frame, self.taskFile, 
                                              self.settings)

    def tearDown(self):
        super(EffortViewerTest, self).tearDown()
        self.taskFile.close()
        self.taskFile.stop()

    @test.skipOnPlatform('__WXMSW__')  # GetItemBackgroundColour doesn't work on Windows
    def testEffortBackgroundColor(self):  # pragma: no cover
        self.task.setBackgroundColor(wx.RED)
        self.task.addEffort(self.effort1)
        self.assertEqual(wx.RED, self.viewer.widget.GetItemBackgroundColour(0))

    @test.skipOnPlatform('__WXMSW__')  # GetItemBackgroundColour doesn't work on Windows
    def testUpdateEffortBackgroundColor(self):  # pragma: no cover
        self.task.addEffort(self.effort1)
        self.task.setBackgroundColor(wx.RED)
        self.assertEqual(wx.RED, self.viewer.widget.GetItemBackgroundColour(0))
    
    def testSearch(self):
        self.task.addEffort(self.effort1)
        self.viewer.presentation().setSearchFilter('no such task')
        self.assertEqual(0, len(self.viewer.presentation()))
        self.viewer.presentation().setSearchFilter(self.task.subject())
        self.assertEqual(1, len(self.viewer.presentation()))
        
    def testSearchIncludeSubitems(self):
        self.task.addEffort(self.effort1)
        child = task.Task('child')
        self.task.addChild(child)
        child.setParent(self.task)
        self.taskFile.tasks().append(child)
        child.addEffort(effort.Effort(child))
        self.assertEqual(2, len(self.viewer.presentation()))
        self.viewer.presentation().setSearchFilter(self.task.subject())
        self.assertEqual(1, len(self.viewer.presentation()))
        self.viewer.presentation().setSearchFilter(self.task.subject(), 
                                                   includeSubItems=True)
        self.assertEqual(2, len(self.viewer.presentation()))
        
    def testAscendingSortOrder(self):
        self.task.addEffort(self.effort1)
        self.task.addEffort(self.effort2)
        self.viewer.presentation().sortAscending(True)
        self.assertEqual([self.effort1, self.effort2], list(self.viewer.presentation()))

    def testDescendingSortOrder(self):
        self.task.addEffort(self.effort1)
        self.task.addEffort(self.effort2)
        self.viewer.presentation().sortAscending(False)
        self.assertEqual([self.effort2, self.effort1], list(self.viewer.presentation()))
        
        
class EffortViewerAggregationTestCase(test.wxTestCase):
    aggregation = 'Subclass responsibility'
    
    def createViewer(self):
        return gui.viewer.EffortViewer(self.frame, self.taskFile, self.settings)

    def setUp(self):
        super(EffortViewerAggregationTestCase, self).setUp()
        task.Task.settings = self.settings = config.Settings(load=False)
        self.settings.set('effortviewer', 'aggregation', self.aggregation)

        self.taskFile = persistence.TaskFile()
        self.viewer = self.createViewer()
        self.task = task.Task('Task')
        self.task2 = task.Task('Task2')
        self.taskFile.tasks().extend([self.task, self.task2])
        self.task.addEffort(effort.Effort(self.task, 
            date.DateTime(2008, 7, 16, 10, 0, 0), 
            date.DateTime(2008, 7, 16, 11, 0, 0)))
        self.task.addEffort(effort.Effort(self.task, 
            date.DateTime(2008, 7, 16, 12, 0, 0), 
            date.DateTime(2008, 7, 16, 13, 0, 0)))
        self.task.addEffort(effort.Effort(self.task,
            date.DateTime(2008, 7, 17, 1, 0, 0), 
            date.DateTime(2008, 7, 17, 2, 0, 0)))
        mostRecentPeriod = (date.DateTime(2008, 7, 23, 1, 0, 0), 
                            date.DateTime(2008, 7, 23, 2, 0, 0))
        # pylint: disable-msg=W0142
        self.task.addEffort(effort.Effort(self.task, *mostRecentPeriod))
        self.task2.addEffort(effort.Effort(self.task2, *mostRecentPeriod))
        

    def tearDown(self):
        super(EffortViewerAggregationTestCase, self).tearDown()
        self.taskFile.close()
        self.taskFile.stop()

    def switchAggregation(self):
        aggregations = ['details', 'day', 'week', 'month']
        aggregations.remove(self.aggregation)
        self.viewer.showEffortAggregation(aggregations[0])
    

class CommonTestsMixin(object):
    def testNumberOfItems(self):
        self.assertEqual(self.expectedNumberOfItems, self.viewer.size())

    def testRenderPeriod(self):
        self.assertEqual(self.expectedPeriodRendering, 
                         self.viewer.widget.GetItemText(0))

    def testRenderRepeatedPeriod(self):
        self.assertEqual('', self.viewer.widget.GetItemText(1))

    def testSwitchAggregation(self):
        self.switchAggregation()    
        self.viewer.showEffortAggregation(self.aggregation)
        self.assertEqual(self.expectedNumberOfItems, self.viewer.size())

    def testAggregationIsSavedInSettings(self):
        self.assertEqual(self.aggregation, 
            self.settings.get(self.viewer.settingsSection(), 'aggregation'))

    def testToolbarChoiceCtrlShowsAggegrationMode(self):
        aggregationUICommand = self.viewer.aggregationUICommand
        index = aggregationUICommand.choiceData.index(self.aggregation)
        expectedLabel = aggregationUICommand.choiceLabels[index]
        actualLabel = aggregationUICommand.choiceCtrl.GetStringSelection()
        self.assertEqual(expectedLabel, actualLabel)
        
    def testSearch(self):
        self.viewer.setSearchFilter('Task2')
        self.assertEqual(1, self.viewer.size())
        
    def testSearchDescription(self):
        self.task.efforts()[0].setDescription('Description')
        self.viewer.setSearchFilter('Description', searchDescription=True)
        self.assertEqual(1, self.viewer.size())

    def testSearchWithIncludeSubitems(self):
        self.viewer.setSearchFilter('Task2', includeSubItems=True)
        self.assertEqual(1, self.viewer.size())
        
    def testDelete(self):
        self.viewer.widget.select([self.task.efforts()[-1]])
        self.viewer.updateSelection()
        self.viewer.deleteUICommand.doCommand(None)
        expectedNumberOfItems = self.expectedNumberOfItems - (1 if self.aggregation == 'details' else 3)
        self.assertEqual(expectedNumberOfItems, self.viewer.size())
    
    def testDeleteTask(self):
        self.taskFile.tasks().remove(self.task2)
        expectedNumberOfItems = self.expectedNumberOfItems - 1
        self.assertEqual(expectedNumberOfItems, self.viewer.size())
        
    def testNewEffortUsesSameTaskAsSelectedEffort(self):
        self.viewer.widget.select([self.task2.efforts()[-1]])
        self.viewer.updateSelection()
        dialog = self.viewer.newItemDialog(selectedTasks=[self.task2], 
                                           bitmap='new')
        for newEffort in dialog._items:  # pylint: disable-msg=W0212
            self.assertEqual(self.task2, newEffort.task())
        
    def testColumnUICommands(self):
        expectedLength = dict(details=6, day=8, week=9, month=8)[self.aggregation]
        self.assertEqual(expectedLength,
                         len(self.viewer.getColumnUICommands()))
        
    def testTotalTimeSpentColumnNotInDetailsMode(self):
        columns = [command.setting for command in self.viewer.getColumnUICommands() if command]
        self.assertEqual(self.aggregation != 'details', 
                         'totalTimeSpent' in columns)

    def testTotalRevenueColumnNotInDetailsMode(self):
        columns = [command.setting for command in self.viewer.getColumnUICommands() if command]
        self.assertEqual(self.aggregation != 'details', 
                         'totalRevenue' in columns)
    
    def testDefaultNrOfColumns(self):
        self.assertEqual(4, self.viewer.widget.GetColumnCount())

    def testHideTimeSpentColumn(self):
        self.viewer.showColumnByName('timeSpent', False)
        self.assertEqual(3, self.viewer.widget.GetColumnCount())
        
    def testHideRevenueColumn(self):
        self.viewer.showColumnByName('revenue', False)
        self.assertEqual(3, self.viewer.widget.GetColumnCount())
        
    def testShowTotalTimeSpentColumn(self):
        self.viewer.showColumnByName('totalTimeSpent', True)
        self.assertEqual(5, self.viewer.widget.GetColumnCount())

    def testShowTotalRevenueColumn(self):
        self.viewer.showColumnByName('totalRevenue', True)
        self.assertEqual(5, self.viewer.widget.GetColumnCount())
        
    def testTotalTimeSpentColumnIsHiddenWhenSwitchingToDetails(self):
        self.viewer.showColumnByName('totalTimeSpent', True)
        self.switchAggregation()
        self.assertEqual(self.viewer.isShowingAggregatedEffort(),
                         self.viewer.isVisibleColumnByName('totalTimeSpent'))

    def testTotalRevenueColumnIsHiddenWhenSwitchingToDetails(self):
        self.viewer.showColumnByName('totalRevenue', True)
        self.switchAggregation()
        self.assertEqual(self.viewer.isShowingAggregatedEffort(),
                         self.viewer.isVisibleColumnByName('totalRevenue'))

    def testActiveEffort(self):
        self.task2.efforts()[0].setStop(date.DateTime.max)  # Make active
        self.viewer.secondRefresher.onEverySecond()  # Simulate clock firing
        expectedNrOfTrackedItems = 1 if self.aggregation == 'details' else 2
        self.assertEqual(expectedNrOfTrackedItems, 
                         len(self.viewer.secondRefresher.currentlyTrackedItems()))
        
    def testActiveEffortAfterSwitch(self):
        self.task2.efforts()[0].setStop(date.DateTime.max)  # Make active
        self.switchAggregation()    
        self.viewer.secondRefresher.onEverySecond()  # Simulate clock firing
        expectedNrOfTrackedItems = 2 if self.aggregation == 'details' else 1
        self.assertEqual(expectedNrOfTrackedItems, 
                         len(self.viewer.secondRefresher.currentlyTrackedItems()))
        
    def testIsShowingAggregatedEffort(self):
        isAggregating = self.aggregation != 'details'
        self.assertEqual(isAggregating, self.viewer.isShowingAggregatedEffort())
        
    def testStopEffortTracking(self):
        self.task.addEffort(effort.Effort(self.task))
        stopUICommand = gui.uicommand.EffortStop(effortList=self.taskFile.efforts(),
                                                 taskList=self.taskFile.tasks())
        stopUICommand.doCommand()
        self.failIf(self.task.isBeingTracked())
    

class EffortViewerWithoutAggregationTest(CommonTestsMixin, 
                                         EffortViewerAggregationTestCase):
    aggregation = 'details'
    expectedNumberOfItems = 5
    expectedPeriodRendering = render.dateTimePeriod(\
        date.DateTime(2008, 7, 23, 1, 0), date.DateTime(2008, 7, 23, 2, 0))
    
    
class EffortViewerWithAggregationPerDayTest(CommonTestsMixin, 
                                            EffortViewerAggregationTestCase):
    aggregation = 'day'
    expectedNumberOfItems = 7  # 4 day/task combinations on 3 days (== 3 total rows) 
    expectedPeriodRendering = render.date(date.DateTime(2008, 7, 23))


class EffortViewerWithAggregationPerWeekTest(CommonTestsMixin, 
                                             EffortViewerAggregationTestCase):
    aggregation = 'week'
    expectedNumberOfItems = 5  # 3 week/task combinations in 2 weeks (== 2 total rows)
    expectedPeriodRendering = '2008-30'


class EffortViewerWithAggregationPerMonthTest(CommonTestsMixin, 
                                              EffortViewerAggregationTestCase):
    aggregation = 'month'
    expectedNumberOfItems = 3  # 2 month/task combinations in 1 month (== 1 total row)
    expectedPeriodRendering = render.month(date.DateTime(2008, 07, 01))
