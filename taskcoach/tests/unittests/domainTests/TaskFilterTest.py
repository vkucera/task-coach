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
from taskcoachlib import config
from taskcoachlib.domain import task, date


class ViewFilterTestCase(test.TestCase):
    def setUp(self):
        task.Task.settings = config.Settings(load=False)
        self.list = task.TaskList()
        self.filter = task.filter.ViewFilter(self.list, treeMode=self.treeMode) # pylint: disable-msg=E1101
        self.task = task.Task(subject='task')
        self.dueToday = task.Task(subject='due today', dueDateTime=date.Now().endOfDay())
        self.dueTomorrow = task.Task(subject='due tomorrow', 
            dueDateTime=date.Now().endOfTomorrow())
        self.dueYesterday = task.Task(subject='due yesterday', 
            dueDateTime=date.Now().endOfYesterday())
        self.child = task.Task(subject='child')
        
    def assertFilterShows(self, *tasks):
        self.assertEqual(len(tasks), len(self.filter))
        for task in tasks:
            self.failUnless(task in self.filter)
        
    def assertFilterIsEmpty(self):
        self.failIf(self.filter)


class ViewFilterTestsMixin(object):
    def testCreate(self):
        self.assertFilterIsEmpty()

    def testAddTask(self):
        self.filter.append(self.task)
        self.assertFilterShows(self.task)
        
    def testFilterCompletedTask(self):
        self.task.setCompletionDateTime()
        self.filter.append(self.task)
        self.assertFilterShows(self.task)
        self.filter.setFilteredByCompletionDateTime('Always')
        self.assertFilterIsEmpty()
        
    def testFilterCompletedTask_RootTasks(self):
        self.task.setCompletionDateTime()
        self.filter.append(self.task)
        self.filter.setFilteredByCompletionDateTime('Always')
        self.failIf(self.filter.rootItems())

    def testMarkTaskCompleted(self):
        self.filter.setFilteredByCompletionDateTime('Always')
        self.list.append(self.task)
        self.task.setCompletionDateTime()
        self.assertFilterIsEmpty()

    def testMarkTaskUncompleted(self):
        self.filter.setFilteredByCompletionDateTime('Always')
        self.task.setCompletionDateTime()
        self.list.append(self.task)
        self.task.setCompletionDateTime(date.DateTime())
        self.assertFilterShows(self.task)
        
    def testChangeCompletionDateOfAlreadyCompletedTask(self):
        self.filter.setFilteredByCompletionDateTime('Always')
        self.task.setCompletionDateTime()
        self.list.append(self.task)
        self.task.setCompletionDateTime(date.Now() + date.oneDay)
        self.assertFilterIsEmpty()
        
    def testFilterTasksCompletedBeforeToday(self):
        self.list.append(self.task)
        self.filter.setFilteredByCompletionDateTime('Today')
        self.task.setCompletionDateTime()
        self.assertFilterShows(self.task)
        self.task.setCompletionDateTime(date.DateTime(2000,1,1))
        self.assertFilterIsEmpty()
        
    def testFilterTasksCompletedBeforeYesterday(self):
        self.list.append(self.task)
        self.filter.setFilteredByCompletionDateTime('Yesterday')
        self.task.setCompletionDateTime(date.Now()-date.TimeDelta(hours=24))
        self.assertFilterShows(self.task)
        self.task.setCompletionDateTime(date.DateTime(2000,1,1))
        self.assertFilterIsEmpty()
        
    def testFilterInactiveTask(self):
        self.task.setStartDateTime(date.Now() + date.oneDay)
        self.list.append(self.task)
        self.filter.setFilteredByStartDateTime('Always')
        self.assertFilterIsEmpty()
        
    def testFilterInactiveTask_ChangeStartDateTime(self):
        self.task.setStartDateTime(date.Now() + date.oneDay)
        self.list.append(self.task)
        self.filter.setFilteredByStartDateTime('Always')
        self.task.setStartDateTime(date.Now())
        self.assertFilterShows(self.task)
        
    def testFilterInactiveTask_WhenStartDateTimePasses(self):
        self.task.setStartDateTime(date.Now() + date.oneDay)
        self.list.append(self.task)
        self.filter.setFilteredByStartDateTime('Always')
        oldNow = date.Now
        date.Now = lambda: oldNow() + date.oneDay + date.TimeDelta(seconds=1)
        date.Clock().notifySpecificTimeObservers(date.Now())
        self.assertFilterShows(self.task)
        date.Now = oldNow
        
    def testFilterDueToday(self):
        self.filter.extend([self.task, self.dueToday])
        self.assertFilterShows(self.task, self.dueToday)
        self.filter.setFilteredByDueDateTime('Today')
        self.assertFilterShows(self.dueToday)

    def testFilterDueToday_ChildDueToday(self):
        self.task.addChild(self.dueToday)
        self.list.append(self.task)
        self.filter.setFilteredByDueDateTime('Today')
        expectedNr = 2 if self.filter.treeMode() else 1
        self.assertEqual(expectedNr, len(self.filter))
            
    def testFilterDueToday_ShouldIncludeOverdueTasks(self):
        self.filter.append(self.dueYesterday)
        self.filter.setFilteredByDueDateTime('Today')
        self.assertFilterShows(self.dueYesterday)

    def testFilterDueToday_ShouldIncludeCompletedTasks(self):
        self.filter.append(self.dueToday)
        self.dueToday.setCompletionDateTime()
        self.filter.setFilteredByDueDateTime('Today')
        self.assertFilterShows(self.dueToday)
        
    def testFilterDueToday_DueDateEdited(self):
        self.filter.append(self.dueTomorrow)
        self.filter.setFilteredByDueDateTime('Today')
        self.assertFilterIsEmpty()
        self.dueTomorrow.setDueDateTime(date.Now())
        self.assertFilterShows(self.dueTomorrow)

    def testFilterDueToday_AtMidnight(self):
        self.filter.append(self.dueTomorrow)
        self.filter.setFilteredByDueDateTime('Today')
        self.assertFilterIsEmpty()
        oldNow = date.Now
        date.Now = lambda: oldNow().endOfDay() + date.TimeDelta(seconds=1)
        date.Clock().notifyMidnightObservers()
        self.assertFilterShows(self.dueTomorrow)
        date.Now = oldNow
        
    def testFilterDueTomorrow(self):
        self.filter.extend([self.task, self.dueTomorrow, self.dueToday])
        self.filter.setFilteredByDueDateTime('Tomorrow')
        self.assertFilterShows(self.dueTomorrow, self.dueToday)
    
    def testFilterDueWeekend(self):
        dueNextWeek = task.Task(dueDateTime=date.Now() + \
            date.TimeDelta(days=8))
        self.filter.extend([self.dueToday, dueNextWeek])
        self.filter.setFilteredByDueDateTime('Workweek')
        self.assertFilterShows(self.dueToday)

    def testMarkPrerequisiteCompletedWhileFilteringInactiveTasks(self):
        self.task.addPrerequisites([self.dueToday])
        self.task.setStartDateTime(date.Now())
        self.dueToday.setStartDateTime(date.Now())
        self.filter.extend([self.dueToday, self.task])
        self.filter.setFilteredByStartDateTime('Always')
        self.filter.setFilteredByCompletionDateTime('Always')
        self.assertFilterShows(self.dueToday)
        self.dueToday.setCompletionDateTime()
        self.assertFilterShows(self.task)
        
    def testAddPrerequisiteToActiveTaskWhileFilteringInactiveTasksShouldHideTask(self):
        for eachTask in (self.task, self.dueToday):
            eachTask.setStartDateTime(date.Now())
        self.filter.extend([self.dueToday, self.task])
        self.filter.setFilteredByStartDateTime('Always')
        self.task.addPrerequisites([self.dueToday])
        self.assertFilterShows(self.dueToday)
        

class ViewFilterInListModeTest(ViewFilterTestsMixin, ViewFilterTestCase):
    treeMode = False
            

class ViewFilterInTreeModeTest(ViewFilterTestsMixin, ViewFilterTestCase):
    treeMode = True
        
    def testFilterCompletedTasks(self):
        self.filter.setFilteredByCompletionDateTime('Always')
        child = task.Task()
        self.task.addChild(child)
        child.setParent(self.task)
        self.list.append(self.task)
        self.task.setCompletionDateTime()
        self.assertFilterIsEmpty()
        

class HideCompositeTasksTestCase(ViewFilterTestCase):
    def setUp(self):
        task.Task.settings = config.Settings(load=False)
        self.list = task.TaskList()
        self.filter = task.filter.ViewFilter(self.list, treeMode=self.treeMode) # pylint: disable-msg=E1101
        self.task = task.Task(subject='task')
        self.child = task.Task(subject='child')
        self.task.addChild(self.child)
        self.filter.append(self.task)

    def _addTwoGrandChildren(self):
        # pylint: disable-msg=W0201
        self.grandChild1 = task.Task(subject='grandchild 1')
        self.grandChild2 = task.Task(subject='grandchild 2')
        self.child.addChild(self.grandChild1)
        self.child.addChild(self.grandChild2)
        self.list.extend([self.grandChild1, self.grandChild2])


class HideCompositeTasksTestsMixin(object):
    def testTurnOn(self):
        self.filter.hideCompositeTasks()
        expectedTasks = (self.task, self.child) if self.filter.treeMode() else (self.child,)
        self.assertFilterShows(*expectedTasks)

    def testTurnOff(self):
        self.filter.hideCompositeTasks()
        self.filter.hideCompositeTasks(False)
        self.assertFilterShows(self.task, self.child)
                
    def testAddChild(self):
        self.filter.hideCompositeTasks()
        grandChild = task.Task(subject='grandchild')
        self.list.append(grandChild)
        self.child.addChild(grandChild)
        expectedTasks = (self.task, self.child, grandChild) if self.filter.treeMode() else (grandChild,)
        self.assertFilterShows(*expectedTasks)

    def testRemoveChild(self):
        self.filter.hideCompositeTasks()
        self.list.remove(self.child)
        self.assertFilterShows(self.task)

    def testAddTwoChildren(self):
        self.filter.hideCompositeTasks()
        self._addTwoGrandChildren()
        expectedTasks = (self.task, self.child, self.grandChild1, 
                         self.grandChild2) if self.filter.treeMode() else \
                        (self.grandChild1, self.grandChild2)
        self.assertFilterShows(*expectedTasks)

    def testRemoveTwoChildren(self):
        self._addTwoGrandChildren()
        self.filter.hideCompositeTasks()
        self.list.removeItems([self.grandChild1, self.grandChild2])
        expectedTasks = (self.task, self.child) if self.filter.treeMode() else (self.child,)
        self.assertFilterShows(*expectedTasks)


class HideCompositeTasksInListModeTest(HideCompositeTasksTestsMixin, 
                                       HideCompositeTasksTestCase):
    treeMode = False
            

class HideCompositeTasksInTreeModeTest(HideCompositeTasksTestsMixin, 
                                       HideCompositeTasksTestCase):
    treeMode = True
