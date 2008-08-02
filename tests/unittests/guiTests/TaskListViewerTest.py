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

import wx
import test, TaskViewerTest
from taskcoachlib import gui, config, widgets
from taskcoachlib.gui import render
from taskcoachlib.i18n import _
from taskcoachlib.domain import task, effort, date, category, note


class CommonTests(object):
    ''' Tests common to all TaskListViewers, i.e. TaskListViewer and
        TaskTreeListViewer. '''
    
    def testSubjectColumnIsVisible(self):
        self.assertEqual(_('Subject'), self.viewer.GetColumn(0).GetText())
    
    def testStartDateColumnIsVisibleByDefault(self):
        self.assertEqual(_('Start date'), self.viewer.GetColumn(1).GetText())
        
    def testDueDateColumnIsVisibleByDefault(self):
        self.assertEqual(_('Due date'), self.viewer.GetColumn(2).GetText())

    def testThreeColumnsByDefault(self):
        self.assertEqual(3, self.viewer.GetColumnCount())
    
    def testTurnOffStartDateColumn(self):
        self.showColumn('startDate', False)
        self.assertEqual(_('Due date'), self.viewer.GetColumn(1).GetText())
        self.assertEqual(2, self.viewer.GetColumnCount())
        
    def testShowSort_Subject(self):
        self.viewer.sortBy('subject')
        self.assertNotEqual(-1, self.viewer.GetColumn(0).GetImage())
        self.assertEqual(-1, self.viewer.GetColumn(1).GetImage())
    
    def testColorWhenTaskIsCompleted(self):
        self.taskList.append(self.task)
        self.task.setCompletionDate()
        newColor = gui.color.taskColor(self.task, self.settings)
        self.newColor = newColor.Red(), newColor.Green(), newColor.Blue()
        self.assertColor()

    def testTurnOnHourlyFeeColumn(self):
        self.showColumn('hourlyFee')
        self.assertEqual(_('Hourly fee'), self.viewer.GetColumn(3).GetText())

    def testTurnOnFixedFeeColumn(self):
        self.showColumn('fixedFee')
        self.assertEqual(_('Fixed fee'), self.viewer.GetColumn(3).GetText())

    def testTurnOnTotalFixedFeeColumn(self):
        self.showColumn('totalFixedFee')
        self.assertEqual(_('Total fixed fee'), self.viewer.GetColumn(3).GetText())

    def testTurnOnFixedFeeColumnWithItemsInTheList(self):
        taskWithFixedFee = task.Task(fixedFee=100)
        self.taskList.append(taskWithFixedFee)
        self.showColumn('fixedFee')
        self.assertEqual(_('Fixed fee'), self.viewer.GetColumn(3).GetText())

    def testTurnOnPriorityColumn(self):
        taskWithPriority = task.Task(priority=10)
        self.taskList.append(taskWithPriority)
        self.showColumn('priority')
        self.assertEqual(_('Priority'), self.viewer.GetColumn(3).GetText())
        
    def testTurnOffPriorityColumn(self):
        self.showColumn('priority')
        taskWithPriority = task.Task(priority=10)
        self.taskList.append(taskWithPriority)
        self.showColumn('priority', False)
        self.assertEqual(3, self.viewer.GetColumnCount())
        
    def testTurnOnRecurrenceColumn(self):
        taskWithRecurrence = task.Task(recurrence='weekly')
        self.taskList.append(taskWithRecurrence)
        self.showColumn('recurrence')
        self.assertEqual(_('Recurrence'), self.viewer.GetColumn(3).GetText())

    def testTurnOffRecurrenceColumn(self):
        self.showColumn('recurrence')
        taskWithRecurrence = task.Task(recurrence='weekly')
        self.taskList.append(taskWithRecurrence)
        self.showColumn('recurrence', False)
        self.assertEqual(3, self.viewer.GetColumnCount())

        
class TaskListViewerTest(CommonTests, TaskViewerTest.CommonTests, 
        test.wxTestCase):
    def setUp(self):
        super(TaskListViewerTest, self).setUp()
        self.settings = config.Settings(load=False)
        self.categories = category.CategoryList()
        self.taskList = task.sorter.Sorter(task.TaskList())
        effortList = effort.EffortList(self.taskList)
        self.task = task.Task('task')
        self.viewer = gui.viewer.TaskListViewer(self.frame, self.taskList, 
            self.settings, categories=self.categories, efforts=effortList)
        self.viewer.sortBy('subject')
                
    def assertItems(self, *tasks):
        self.assertEqual(len(tasks), self.viewer.size())
        for index, task in enumerate(tasks):
            self.assertEqual(task.subject(recursive=True), 
                             self.viewer.widget.GetItemText(index))
                             
    def getFirstItemTextColor(self):
        return self.viewer.widget.GetItemTextColour(0)
    
    def getFirstItemBackgroundColor(self):
        return self.viewer.widget.GetItemBackgroundColour(0)

    def assertColor(self):
        # There seems to be a bug in the ListCtrl causing GetItemTextColour() to
        # always return the 'unknown' colour on Windows. We keep this test like
        # this so it will fail when the bug is fixed.
        if '__WXMSW__' in wx.PlatformInfo:
            self.assertEqual(wx.NullColour, self.getFirstItemTextColor())
        else:
            super(TaskListViewerTest, self).assertColor()

    def assertBackgroundColor(self):
        # There seems to be a bug in the ListCtrl causing 
        # GetItemBackgroundColour() to always return the 'unknown' colour on 
        # Windows. We keep this test like this so it will fail when the bug is 
        # fixed.
        if '__WXMSW__' in wx.PlatformInfo:
            self.assertEqual(wx.NullColour, self.getFirstItemBackgroundColor())
        else:
            super(TaskListViewerTest, self).assertBackgroundColor()
        
    def testEmptyTaskList(self):
        self.assertItems()

    def testAddTask(self):
        self.taskList.append(self.task)
        self.assertItems(self.task)

    def testRemoveTask(self):
        self.taskList.append(self.task)
        self.taskList.remove(self.task)
        self.assertItems()

    def testCurrent(self):
        self.taskList.append(self.task)
        self.viewer.widget.select([0])
        self.assertEqual([self.task], self.viewer.curselection())

    def testOneDayLeft(self):
        self.showColumn('timeLeft')
        self.task.setDueDate(date.Tomorrow())
        self.taskList.append(self.task)
        self.assertEqual(render.daysLeft(self.task.timeLeft(), False), 
            self.viewer.widget.GetItem(0, 3).GetText())

    def testChildSubjectRendering(self):
        child = task.Task(subject='child')
        self.task.addChild(child)
        self.taskList.append(self.task)
        self.assertItems(child, self.task)
           
    def testMarkCompleted(self):
        task2 = task.Task(subject='task2')
        self.taskList.extend([self.task, task2])
        self.assertItems(self.task, task2)
        self.task.setCompletionDate()
        self.assertItems(task2, self.task)
            
    def testSortByDueDate(self):
        self.viewer.sortBy('subject')
        self.viewer.setSortOrderAscending(True)
        child = task.Task(subject='child')
        self.task.addChild(child)
        task2 = task.Task('zzz')
        child2 = task.Task('child 2')
        task2.addChild(child2)
        self.taskList.extend([self.task, task2])
        self.assertItems(child, child2, self.task, task2) 
        child2.setDueDate(date.Today())
        self.viewer.sortBy('dueDate')
        self.assertItems(child2, child, self.task, task2)

