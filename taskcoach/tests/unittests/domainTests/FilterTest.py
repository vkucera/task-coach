'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2010 Task Coach developers <developers@taskcoach.org>

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
from taskcoachlib import patterns, config
from taskcoachlib.domain import task, date, base


class TestFilter(base.Filter):
    def filter(self, items):
        return [item for item in items if item > 'b']


class FilterTestsMixin(object):
    def setUp(self):
        self.observable = self.collectionClass(['a', 'b', 'c', 'd'])
        self.filter = TestFilter(self.observable)

    def testLength(self):
        self.assertEqual(2, len(self.filter))

    def testContents(self):
        self.failUnless('c' in self.filter and 'd' in self.filter)

    def testRemoveItem(self):
        self.filter.remove('c')
        self.assertEqual(1, len(self.filter))
        self.failUnless('d' in self.filter)
        self.assertEqual(['a', 'b', 'd'], self.observable)

    def testNotification(self):
        self.observable.append('e')
        self.assertEqual(3, len(self.filter))
        self.failUnless('e' in self.filter)

        
class FilterListTest(FilterTestsMixin, test.TestCase):
    collectionClass = patterns.ObservableList


class FilterSetTest(FilterTestsMixin, test.TestCase):
    collectionClass = patterns.ObservableSet
    
    
class DummyFilter(base.Filter):
    def filter(self, items):
        return items
    
    def test(self):
        self.testcalled = 1 # pylint: disable-msg=W0201


class DummyItem(str):
    def ancestors(self):
        return []
    
    def children(self, *args, **kwargs):
        return []


class StackedFilterTest(test.TestCase):
    def setUp(self):
        self.list = patterns.ObservableList([DummyItem('a'), DummyItem('b'), 
                                             DummyItem('c'), DummyItem('d')])
        self.filter1 = DummyFilter(self.list)
        self.filter2 = TestFilter(self.filter1)

    def testDelegation(self):
        self.filter2.test()
        self.assertEqual(1, self.filter1.testcalled)
        
    def testSetTreeMode_True(self):
        self.filter2.setTreeMode(True)
        self.failUnless(self.filter1.treeMode())
        
    def testSetTreeMode_False(self):
        self.filter2.setTreeMode(False)
        self.failIf(self.filter1.treeMode())
        

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


class ViewFilterTestsMixin(object):
    def testCreate(self):
        self.assertEqual(0, len(self.filter))

    def testAddTask(self):
        self.filter.append(self.task)
        self.assertEqual(1, len(self.filter))
        
    def testFilterCompletedTask(self):
        self.task.setCompletionDateTime()
        self.filter.append(self.task)
        self.assertEqual(1, len(self.filter))
        self.filter.hideCompletedTasks()
        self.assertEqual(0, len(self.filter))
        
    def testFilterCompletedTask_RootTasks(self):
        self.task.setCompletionDateTime()
        self.filter.append(self.task)
        self.filter.hideCompletedTasks()
        self.assertEqual(0, len(self.filter.rootItems()))

    def testMarkTaskCompleted(self):
        self.filter.hideCompletedTasks()
        self.list.append(self.task)
        self.task.setCompletionDateTime()
        self.assertEqual(0, len(self.filter))

    def testMarkTaskUncompleted(self):
        self.filter.hideCompletedTasks()
        self.task.setCompletionDateTime()
        self.list.append(self.task)
        self.task.setCompletionDateTime(date.DateTime())
        self.assertEqual(1, len(self.filter))
        
    def testChangeCompletionDateOfAlreadyCompletedTask(self):
        self.filter.hideCompletedTasks()
        self.task.setCompletionDateTime()
        self.list.append(self.task)
        self.task.setCompletionDateTime(date.Now() + date.oneDay)
        self.assertEqual(0, len(self.filter))

    def testFilterDueToday(self):
        self.filter.extend([self.task, self.dueToday])
        self.assertEqual(2, len(self.filter))
        self.filter.setFilteredByDueDateTime('Today')
        self.assertEqual(1, len(self.filter))

    def testFilterDueToday_ChildDueToday(self):
        self.task.addChild(self.dueToday)
        self.list.append(self.task)
        self.filter.setFilteredByDueDateTime('Today')
        if self.filter.treeMode():
            self.assertEqual(2, len(self.filter))
        else:
            self.assertEqual(1, len(self.filter))
            
    def testFilterDueToday_ShouldIncludeOverdueTasks(self):
        self.filter.append(self.dueYesterday)
        self.filter.setFilteredByDueDateTime('Today')
        self.assertEqual(1, len(self.filter))

    def testFilterDueToday_ShouldIncludeCompletedTasks(self):
        self.filter.append(self.dueToday)
        self.dueToday.setCompletionDateTime()
        self.filter.setFilteredByDueDateTime('Today')
        self.assertEqual(1, len(self.filter))

    def testFilterDueTomorrow(self):
        self.filter.extend([self.task, self.dueTomorrow, self.dueToday])
        self.assertEqual(3, len(self.filter))
        self.filter.setFilteredByDueDateTime('Tomorrow')
        self.assertEqual(2, len(self.filter))
    
    def testFilterDueWeekend(self):
        dueNextWeek = task.Task(dueDateTime=date.Now() + \
            date.TimeDelta(days=8))
        self.filter.extend([self.dueToday, dueNextWeek])
        self.filter.setFilteredByDueDateTime('Workweek')
        self.assertEqual(1, len(self.filter))

    def testMarkPrerequisiteCompletedWhileFilteringInactiveTasks(self):
        self.task.addPrerequisites([self.dueToday])
        self.task.setStartDateTime(date.Now())
        self.dueToday.setStartDateTime(date.Now())
        self.filter.extend([self.dueToday, self.task])
        self.filter.hideInactiveTasks()
        self.filter.hideCompletedTasks()
        self.assertEqual(self.dueToday, list(self.filter)[0])
        self.dueToday.setCompletionDateTime()
        self.assertEqual(self.task, list(self.filter)[0])
        
    def testAddPrerequisiteToActiveTaskWhileFilteringInactiveTasksShouldHideTask(self):
        for eachTask in (self.task, self.dueToday):
            eachTask.setStartDateTime(date.Now())
        self.filter.extend([self.dueToday, self.task])
        self.filter.hideInactiveTasks()
        self.task.addPrerequisites([self.dueToday])
        self.assertEqual([self.dueToday], list(self.filter))
        

class ViewFilterInListModeTest(ViewFilterTestsMixin, ViewFilterTestCase):
    treeMode = False
            

class ViewFilterInTreeModeTest(ViewFilterTestsMixin, ViewFilterTestCase):
    treeMode = True
        
    def testFilterCompletedTasks(self):
        self.filter.hideCompletedTasks()
        child = task.Task()
        self.task.addChild(child)
        child.setParent(self.task)
        self.list.append(self.task)
        self.task.setCompletionDateTime()
        self.assertEqual(0, len(self.filter))
        

class HideCompositeTasksTestCase(ViewFilterTestCase):
    def setUp(self):
        task.Task.settings = config.Settings(load=False)
        self.list = task.TaskList()
        self.filter = task.filter.ViewFilter(self.list, treeMode=self.treeMode) # pylint: disable-msg=E1101
        self.task = task.Task(subject='task')
        self.child = task.Task(subject='child')
        self.task.addChild(self.child)
        self.filter.append(self.task)


class HideCompositeTasksTestsMixin(object):
    def testTurnOn(self):
        self.filter.hideCompositeTasks()
        if self.filter.treeMode():
            self.assertEqual(2, len(self.filter))
        else:
            self.assertEqual([self.child], list(self.filter))

    def testTurnOff(self):
        self.filter.hideCompositeTasks()
        self.filter.hideCompositeTasks(False)
        self.assertEqual(2, len(self.filter))
                
    def testAddChild(self):
        self.filter.hideCompositeTasks()
        grandChild = task.Task(subject='grandchild')
        self.list.append(grandChild)
        self.child.addChild(grandChild)
        if self.filter.treeMode():
            self.assertEqual(3, len(self.filter))
        else:
            self.assertEqual([grandChild], list(self.filter))

    def testRemoveChild(self):
        self.filter.hideCompositeTasks()
        self.list.remove(self.child)
        self.assertEqual([self.task], list(self.filter))

    def _addTwoGrandChildren(self):
        # pylint: disable-msg=W0201
        self.grandChild1 = task.Task(subject='grandchild 1')
        self.grandChild2 = task.Task(subject='grandchild 2')
        self.child.addChild(self.grandChild1)
        self.child.addChild(self.grandChild2)
        self.list.extend([self.grandChild1, self.grandChild2])

    def testAddTwoChildren(self):
        self.filter.hideCompositeTasks()
        self._addTwoGrandChildren()
        if self.filter.treeMode():
            self.assertEqual(4, len(self.filter))
        else:
            self.assertEqual(set([self.grandChild1, self.grandChild2]), 
                set(self.filter))

    def testRemoveTwoChildren(self):
        self._addTwoGrandChildren()
        self.filter.hideCompositeTasks()
        self.list.removeItems([self.grandChild1, self.grandChild2])
        if self.filter.treeMode():
            self.assertEqual(2, len(self.filter))
        else:
            self.assertEqual([self.child], list(self.filter))


class HideCompositeTasksInListModeTest(HideCompositeTasksTestsMixin, 
                                       HideCompositeTasksTestCase):
    treeMode = False
            

class HideCompositeTasksInTreeModeTest(HideCompositeTasksTestsMixin, 
                                       HideCompositeTasksTestCase):
    treeMode = True
        

class SearchFilterTest(test.TestCase):
    def setUp(self):
        task.Task.settings = config.Settings(load=False)
        self.parent = task.Task(subject='*ABC', description='Parent description')
        self.child = task.Task(subject='DEF', description='Child description')
        self.parent.addChild(self.child)
        self.list = task.TaskList([self.parent, self.child])
        self.filter = base.SearchFilter(self.list)

    def setSearchString(self, searchString, matchCase=False,
                        includeSubItems=False, searchDescription=False):
        self.filter.setSearchFilter(searchString, matchCase=matchCase, 
                                    includeSubItems=includeSubItems,
                                    searchDescription=searchDescription)
        
    def testNoMatch(self):
        self.setSearchString('XYZ')
        self.assertEqual(0, len(self.filter))

    def testMatch(self):
        self.setSearchString('AB')
        self.assertEqual(1, len(self.filter))

    def testMatchIsCaseInSensitiveByDefault(self):
        self.setSearchString('abc')
        self.assertEqual(1, len(self.filter))

    def testMatchCaseInsensitive(self):
        self.setSearchString('abc', True)
        self.assertEqual(0, len(self.filter))

    def testMatchWithRE(self):
        self.setSearchString('a.c')
        self.assertEqual(1, len(self.filter))

    def testMatchWithEmptyString(self):
        self.setSearchString('')
        self.assertEqual(2, len(self.filter))

    def testMatchChildDoesNotSelectParentWhenNotInTreeMode(self):
        self.setSearchString('DEF')
        self.assertEqual(1, len(self.filter))

    def testMatchChildAlsoSelectsParentWhenInTreeMode(self):
        self.filter.setTreeMode(True)
        self.setSearchString('DEF')
        self.assertEqual(2, len(self.filter))
        
    def testMatchChildDoesNotSelectParentWhenChildNotInList(self):
        self.list.remove(self.child) 
        self.parent.addChild(self.child) # simulate a child that has been filtered 
        self.setSearchString('DEF')
        self.assertEqual(0, len(self.filter))

    def testAddTask(self):
        self.setSearchString('XYZ')
        taskXYZ = task.Task(subject='subject with XYZ')
        self.list.append(taskXYZ)
        self.assertEqual([taskXYZ], list(self.filter))

    def testRemoveTask(self):
        self.setSearchString('DEF')
        self.list.remove(self.child)
        self.failIf(self.filter)
        
    def testIncludeSubItems(self):
        self.setSearchString('ABC', includeSubItems=True)
        self.assertEqual(2, len(self.filter))

    def testInvalidRegex(self):
        self.setSearchString('*')
        self.assertEqual(1, len(self.filter))

    def testInvalidRegex_WhileMatchCase(self):
        self.setSearchString('*', matchCase=True)
        self.assertEqual(1, len(self.filter))

    def testSearchDescription(self):
        self.setSearchString('parent description', searchDescription=True)
        self.assertEqual(1, len(self.filter))

    def testSearchDescription_TurnedOff(self):
        self.setSearchString('parent description')
        self.assertEqual(0, len(self.filter))
        
    def testSearchDescriptionWithSubItemsIncluded(self):
        self.setSearchString('parent description', includeSubItems=True,
                             searchDescription=True)
        self.assertEqual(2, len(self.filter))

    def testSearchDescription_MatchChildDoesNotSelectParentWhenNotInTreeMode(self):
        self.setSearchString('child description', searchDescription=True)
        self.assertEqual(1, len(self.filter))

    def testSearchDescription_MatchChildAlsoSelectsParentWhenInTreeMode(self):
        self.filter.setTreeMode(True)
        self.setSearchString('child description', searchDescription=True)
        self.assertEqual(2, len(self.filter))


class DeletedFilterTest(test.TestCase):
    def setUp(self):
        self.list = task.TaskList()
        self.filter = base.DeletedFilter(self.list)
        self.task = task.Task()
        
    def testAddItem(self):
        self.list.append(self.task)
        self.assertEqual(1, len(self.filter))
     
    def testDeleteItem(self):
        self.list.append(self.task)
        self.list.remove(self.task)
        self.assertEqual(0, len(self.filter))
        
    def testMarkDeleted(self):
        self.list.append(self.task)
        self.task.markDeleted()
        self.assertEqual(0, len(self.filter))
        
    def testMarkNotDeleted(self):
        self.list.append(self.task)
        self.task.markDeleted()
        self.task.cleanDirty()
        self.assertEqual(1, len(self.filter))


class SelectedItemsFilterTest(test.TestCase):
    def setUp(self):
        task.Task.settings = config.Settings(load=False)
        self.task = task.Task()
        self.child = task.Task(parent=self.task)
        self.list = task.TaskList([self.task])
        self.filter = base.SelectedItemsFilter(self.list, 
                                               selectedItems=[self.task])
        
    def testInitialContent(self):
        self.assertEqual([self.task], list(self.filter))
        
    def testAddChild(self):
        self.list.append(self.child)
        self.failUnless(self.child in self.filter)
        
    def testAddChildWithGrandchild(self):
        grandchild = task.Task(parent=self.child)
        self.child.addChild(grandchild)
        self.list.append(self.child)
        self.failUnless(grandchild in self.filter)
        
    def testRemoveSelectedItem(self):
        self.list.remove(self.task)
        self.failIf(self.filter)
        
    def testSelectedItemsFilterShowsAllTasksWhenSelectedItemsRemoved(self):
        otherTask = task.Task()
        self.list.append(otherTask)
        self.list.remove(self.task)
        self.assertEqual([otherTask], list(self.filter))

