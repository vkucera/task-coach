'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>

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
from taskcoachlib import gui, config
from taskcoachlib.domain import task, effort, category, note, date


class EffortViewerTestCase(test.wxTestCase):
    def createViewer(self):
        return gui.viewer.EffortListViewer(self.frame,
                                           self.taskList,
                                           self.settings,
                                           category.CategoryList(),
                                           note.NoteContainer())

    def setUp(self):
        super(EffortViewerTestCase, self).setUp()
        self.settings = config.Settings(load=False)
        self.settings.set('effortlistviewer', 'aggregation', self.aggregation)

        self.task = task.Task('Task')
        self.task.addEffort(effort.Effort(self.task, 
            date.DateTime(2008,7,16,10,0,0), date.DateTime(2008,7,16,11,0,0)))
        self.task.addEffort(effort.Effort(self.task, 
            date.DateTime(2008,7,16,12,0,0), date.DateTime(2008,7,16,13,0,0)))
        self.task.addEffort(effort.Effort(self.task,
            date.DateTime(2008,7,17,1,0,0), date.DateTime(2008,7,17,2,0,0)))            
        mostRecentPeriod = (date.DateTime(2008,7,23,1,0,0), 
                            date.DateTime(2008,7,23,2,0,0))
        self.task.addEffort(effort.Effort(self.task, *mostRecentPeriod))
        self.task2 = task.Task('Task2')
        self.task2.addEffort(effort.Effort(self.task2, *mostRecentPeriod))
        
        self.taskList = task.TaskList([self.task, self.task2])
        self.viewer = self.createViewer()

    def switchAggregation(self):
        aggregations = ['details', 'day', 'week', 'month']
        aggregations.remove(self.aggregation)
        self.viewer.showEffortAggregation(aggregations[0])
    

class CommonTests(object):
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

    def testDelete(self):
        self.viewer.widget.select((0,))
        self.viewer.deleteUICommand.doCommand(None)
        self.assertEqual(self.expectedNumberOfItems - 1, self.viewer.size())
    
    def testColumnUICommands(self):
        if self.aggregation == 'details':
            expectedLength = 7
        elif self.aggregation == 'week':
            expectedLength= 10
        else:
            expectedLength = 9
        self.assertEqual(expectedLength,
                         len(self.viewer.getColumnUICommands()))
    
    def testDefaultNrOfColumns(self):
        self.assertEqual(4, self.viewer.widget.GetColumnCount())

    def testHideTimeSpentColumn(self):
        self.viewer.showColumnByName('timeSpent', False)
        self.assertEqual(3, self.viewer.widget.GetColumnCount())
        
    def testHideRevenueColumn(self):
        self.viewer.showColumnByName('revenue', False)
        self.assertEqual(3, self.viewer.widget.GetColumnCount())

    def testHideTotalColumnsWhenSwitchingToDetailView(self):
        self.viewer.showColumnByName('totalTimeSpent')
        self.viewer.showEffortAggregation('details')
        self.assertEqual(4, self.viewer.widget.GetColumnCount())
        
    def testShowTotalColumnsWhenSwitchingToAggregatedView(self):
        self.viewer.showColumnByName('totalTimeSpent')
        self.viewer.showEffortAggregation(self.aggregation)
        if self.aggregation == 'details':
            expectedColumnCount = 4
        else:
            expectedColumnCount = 5
        self.assertEqual(expectedColumnCount, 
                         self.viewer.widget.GetColumnCount())
        
    def testActiveEffort(self):
        self.task2.efforts()[0].setStop(date.DateTime.max) # Make active
        self.viewer.onEverySecond(None) # Simulate clock firing
        self.assertEqual(1, len(self.viewer.currentlyTrackedItems()))
        
    def testActiveEffortAfterSwitch(self):
        self.task2.efforts()[0].setStop(date.DateTime.max) # Make active
        self.switchAggregation()    
        self.viewer.onEverySecond(None) # Simulate clock firing
        self.assertEqual(1, len(self.viewer.currentlyTrackedItems()))
    

class EffortViewerWithoutAggregationTest(CommonTests, 
                                         EffortViewerTestCase):
    aggregation = 'details'
    expectedNumberOfItems = 5
    expectedPeriodRendering = '2008-07-23 01:00 - 02:00'
    

class EffortViewerWithAggregationPerDayTest(CommonTests, 
                                            EffortViewerTestCase):
    aggregation = 'day'
    expectedNumberOfItems = 4
    expectedPeriodRendering = '2008-07-23'


class EffortViewerWithAggregationPerWeekTest(CommonTests, 
                                             EffortViewerTestCase):
    aggregation = 'week'
    expectedNumberOfItems = 3
    expectedPeriodRendering = '2008-30'


class EffortViewerWithAggregationPerMonthTest(CommonTests, 
                                              EffortViewerTestCase):
    aggregation = 'month'
    expectedNumberOfItems = 2
    expectedPeriodRendering = gui.render.month(date.Date(2008,07,01))

