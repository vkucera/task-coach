'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>
Copyright (C) 2008 Jerome Laheurte <fraca7@free.fr>

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

import test, wx, sets
from unittests import asserts
from taskcoachlib import patterns
from taskcoachlib.domain import task, effort, date, attachment, note


# Handy globals
zeroHour = date.TimeDelta(hours=0)
oneHour = date.TimeDelta(hours=1)
twoHours = date.TimeDelta(hours=2)
threeHours = date.TimeDelta(hours=3)


class TaskTestCase(test.TestCase):
    eventTypes = []
    
    def labelTaskChildrenAndEffort(self, task, taskLabel):
        for childIndex, child in enumerate(task.children()):
            childLabel = '%s_%d'%(taskLabel, childIndex+1)
            setattr(self, childLabel, child)
            self.labelTaskChildrenAndEffort(child, childLabel)
            self.labelEfforts(child, childLabel)
            
    def labelEfforts(self, task, taskLabel):
        for effortIndex, effort in enumerate(task.efforts()):
            effortLabel = '%seffort%d'%(taskLabel, effortIndex+1)
            setattr(self, effortLabel, effort)
            
    def setUp(self):
        self.tasks = self.createTasks()
        self.task = self.tasks[0]
        for index, task in enumerate(self.tasks):
            taskLabel = 'task%d'%(index+1)
            setattr(self, taskLabel, task)
            self.labelTaskChildrenAndEffort(task, taskLabel)
            self.labelEfforts(task, taskLabel)
        for eventType in self.eventTypes:
            self.registerObserver(eventType)
            
    def createTasks(self):
        def createAttachments(kwargs):
            if kwargs.has_key('attachments'):
                kwargs['attachments'] = [attachment.FileAttachment(filename) for filename in kwargs['attachments']]
            return kwargs

        return [task.Task(**createAttachments(kwargs)) for kwargs in \
                self.taskCreationKeywordArguments()]

    def taskCreationKeywordArguments(self):
        return [{}]

    def addEffort(self, hours, task=None):
        task = task or self.task
        start = date.DateTime(2005,1,1)
        task.addEffort(effort.Effort(task, start, start+hours))

    def assertReminder(self, expectedReminder, task=None):
        task = task or self.task
        self.assertEqual(expectedReminder, task.reminder())
        
        
class CommonTaskTests(asserts.TaskAsserts):
    ''' These tests should succeed for all tasks, regardless of state. '''
    def testCopy(self):
        copy = self.task.copy()
        self.assertTaskCopy(copy, self.task)


class NoBudgetTests(object):
    ''' These tests should succeed for all tasks without budget. '''
    def testTaskHasNoBudget(self):
        self.assertEqual(date.TimeDelta(), self.task.budget())
        
    def testTaskHasNoRecursiveBudget(self):
        self.assertEqual(date.TimeDelta(), self.task.budget(recursive=True))

    def testTaskHasNoBudgetLeft(self):
        self.assertEqual(date.TimeDelta(), self.task.budgetLeft())

    def testTaskHasNoRecursiveBudgetLeft(self):
        self.assertEqual(date.TimeDelta(), self.task.budgetLeft(recursive=True))


class DefaultTaskStateTest(TaskTestCase, CommonTaskTests, NoBudgetTests):

    # Getters

    def testTaskHasNoDueDateByDefault(self):
        self.assertEqual(date.Date(), self.task.dueDate())

    def testTaskStartDateIsTodayByDefault(self):
        self.assertEqual(date.Today(), self.task.startDate())

    def testTaskIsNotCompletedByDefault(self):
        self.failIf(self.task.completed())

    def testTaskHasNoCompletionDateByDefault(self):
        self.assertEqual(date.Date(), self.task.completionDate())

    def testTaskIsActiveByDefault(self):
        self.failUnless(self.task.active())
        
    def testTaskIsNotInactiveByDefault(self):
        self.failIf(self.task.inactive())
        
    def testTaskIsNotDueTodayByDefault(self):
        self.failIf(self.task.dueToday())

    def testTaskIsNotDueTomorrowByDefault(self):
        self.failIf(self.task.dueTomorrow())

    def testTaskHasNoDescriptionByDefault(self):
        self.assertEqual('', self.task.description())

    def testTaskHasNoChildrenByDefaultSoNotAllChildrenAreCompleted(self):
        self.failIf(self.task.allChildrenCompleted())

    def testTaskHasNoEffortByDefault(self):
        zero = date.TimeDelta()
        for recursive in False, True:
            self.assertEqual(zero, self.task.timeSpent(recursive=recursive))

    def testTaskPriorityIsZeroByDefault(self):
        for recursive in False, True:
            self.assertEqual(0, self.task.priority(recursive=recursive))

    def testTaskHasNoReminderSetByDefault(self):
        self.assertReminder(None)
    
    def testShouldMarkTaskCompletedIsUndecidedByDefault(self):
        self.assertEqual(None, 
            self.task.shouldMarkCompletedWhenAllChildrenCompleted)
        
    def testTaskHasNoAttachmentsByDefault(self):
        self.assertEqual([], self.task.attachments())
        
    def testTaskHasNoFixedFeeByDefault(self):
        for recursive in False, True:
            self.assertEqual(0, self.task.fixedFee(recursive=recursive))
        
    def testTaskHasNoRevenueByDefault(self):
        for recursive in False, True:
            self.assertEqual(0, self.task.revenue(recursive=recursive))
        
    def testTaskHasNoHourlyFeeByDefault(self):
        for recursive in False, True:
            self.assertEqual(0, self.task.hourlyFee(recursive=recursive))
            
    def testTaskDoesNotRecurByDefault(self):
        self.failIf(self.task.recurrence())
        
    def testTaskDoesNotHaveNotesByDefault(self):
        self.failIf(self.task.notes())
                                         
    # Setters

    def testSetStartDate(self):
        self.task.setStartDate(date.Yesterday())
        self.assertEqual(date.Yesterday(), self.task.startDate())

    def testSetStartDateNotification(self):
        self.registerObserver('task.startDate')
        self.task.setStartDate(date.Yesterday())
        self.assertEqual(date.Yesterday(), self.events[0].value())

    def testSetStartDateUnchangedCausesNoNotification(self):
        self.registerObserver('task.startDate')
        self.task.setStartDate(self.task.startDate())
        self.failIf(self.events)

    def testSetDueDate(self):
        self.date = date.Tomorrow()
        self.task.setDueDate(self.date)
        self.assertEqual(self.date, self.task.dueDate())

    def testSetDueDateNotification(self):
        self.registerObserver('task.dueDate')
        self.task.setDueDate(date.Tomorrow())
        self.assertEqual(date.Tomorrow(), self.events[0].value())

    def testSetDueDateUnchangedCausesNoNotification(self):
        self.registerObserver('task.dueDate')
        self.task.setDueDate(self.task.dueDate())
        self.failIf(self.events)

    def testSetCompletionDate(self):
        self.task.setCompletionDate(date.Today())
        self.assertEqual(date.Today(), self.task.completionDate())

    def testSetCompletionDateNotification(self):
        self.registerObserver('task.completionDate')
        self.task.setCompletionDate(date.Today())
        self.assertEqual(date.Today(), self.events[0].value())

    def testSetCompletionDateUnchangedCausesNoNotification(self):
        self.registerObserver('task.completionDate')
        self.task.setCompletionDate(date.Date())
        self.failIf(self.events)

    def testSetCompletionDateMakesTaskCompleted(self):
        self.task.setCompletionDate()
        self.failUnless(self.task.completed())

    def testSetCompletionDateDefaultsToToday(self):
        self.task.setCompletionDate()
        self.assertEqual(date.Today(), self.task.completionDate())

    def testSetDescription(self):
        self.task.setDescription('A new description')
        self.assertEqual('A new description', self.task.description())

    def testSetDescriptionNotification(self):
        self.registerObserver(task.Task.descriptionChangedEventType())
        self.task.setDescription('A new description')
        self.failUnless('A new description', self.events[0].value())

    def testSetDescriptionUnchangedCausesNoNotification(self):
        self.registerObserver(task.Task.descriptionChangedEventType())
        self.task.setDescription(self.task.description())
        self.failIf(self.events)

    def testSetBudget(self):
        budget = date.TimeDelta(hours=1)
        self.task.setBudget(budget)
        self.assertEqual(budget, self.task.budget())

    def testSetBudgetNotification(self):
        self.registerObserver('task.budget')
        budget = date.TimeDelta(hours=1)
        self.task.setBudget(budget)
        self.assertEqual(budget, self.events[0].value())

    def testSetBudgetUnchangedCausesNoNotification(self):
        self.registerObserver('task.budget')
        self.task.setBudget(self.task.budget())
        self.failIf(self.events)

    def testSetPriority(self):
        self.task.setPriority(10)
        self.assertEqual(10, self.task.priority())

    def testSetPriorityCausesNotification(self):
        self.registerObserver('task.priority')
        self.task.setPriority(10)
        self.assertEqual(10, self.events[0].value())

    def testSetPriorityUnchangedCausesNoNotification(self):
        self.registerObserver('task.priority')
        self.task.setPriority(self.task.priority())
        self.failIf(self.events)

    def testNegativePriority(self):
        self.task.setPriority(-1)
        self.assertEqual(-1, self.task.priority())

    def testSetFixedFee(self):
        self.task.setFixedFee(1000)
        self.assertEqual(1000, self.task.fixedFee())

    def testSetFixedFeeUnchangedCausesNoNotification(self):
        self.registerObserver('task.fixedFee')
        self.task.setFixedFee(self.task.fixedFee())
        self.failIf(self.events)
        
    def testSetFixedFeeCausesNotification(self):
        self.registerObserver('task.fixedFee')
        self.task.setFixedFee(1000)
        self.assertEqual(1000, self.events[0].value())

    def testSetFixedFeeCausesTotalFixedFeeNotification(self):
        self.registerObserver('task.totalFixedFee')
        self.task.setFixedFee(1000)
        self.assertEqual([patterns.Event(self.task, 'task.totalFixedFee', 
                          1000)], 
                         self.events)
    
    def testSetFixedFeeCausesRevenueChangeNotification(self):
        self.registerObserver('task.revenue')
        self.task.setFixedFee(1000)
        self.assertEqual([patterns.Event(self.task, 'task.revenue',
            1000)], self.events)
  
    def testSetHourlyFeeViaSetter(self):
        self.task.setHourlyFee(100)
        self.assertEqual(100, self.task.hourlyFee())
  
    def testSetHourlyFeeCausesNotification(self):
        self.registerObserver(self.task.hourlyFeeChangedEventType())
        self.task.setHourlyFee(100)
        self.assertEqual([patterns.Event(self.task, 
            self.task.hourlyFeeChangedEventType(), 100)], self.events)
  
    def testSetRecurrence(self):
        self.task.setRecurrence(date.Recurrence('weekly'))
        self.assertEqual(date.Recurrence('weekly'), self.task.recurrence())

    def testSetRecurrenceCausesNotification(self):
        self.registerObserver('task.recurrence')
        self.task.setRecurrence(date.Recurrence('weekly'))
        self.assertEqual([patterns.Event(self.task, 'task.recurrence',
            date.Recurrence('weekly'))], self.events)
                        
    # Add child
        
    def testAddChildNotification(self):
        self.registerObserver(task.Task.addChildEventType())
        child = task.Task()
        self.task.addChild(child)
        self.assertEqual(child, self.events[0].value())

    def testAddChildWithBudgetCausesTotalBudgetNotification(self):
        self.registerObserver('task.totalBudget')
        child = task.Task()
        child.setBudget(date.TimeDelta(100))
        self.task.addChild(child)
        self.assertEqual(patterns.Event(self.task, 'task.totalBudget',
            date.TimeDelta(100)), self.events[-1])

    def testAddChildWithoutBudgetCausesNoTotalBudgetNotification(self):
        self.registerObserver('task.totalBudget')
        child = task.Task()
        self.task.addChild(child)
        self.failIf(self.events)

    def testAddChildWithEffortCausesTotalBudgetLeftNotification(self):
        self.task.setBudget(date.TimeDelta(hours=100))
        self.registerObserver('task.totalBudgetLeft')
        child = task.Task()
        child.addEffort(effort.Effort(child, date.DateTime(2000,1,1,10,0,0),
            date.DateTime(2000,1,1,11,0,0)))
        self.task.addChild(child)
        self.assertEqual(patterns.Event(self.task, 'task.totalBudgetLeft',
            date.TimeDelta(hours=99)), self.events[0])

    def testAddChildWithoutEffortCausesNoTotalBudgetLeftNotification(self):
        self.task.setBudget(date.TimeDelta(hours=100))
        self.registerObserver('task.totalBudgetLeft')
        child = task.Task()
        self.task.addChild(child)
        self.failIf(self.events)

    def testAddChildWithEffortToTaskWithoutBudgetCausesNoTotalBudgetLeftNotification(self):
        self.registerObserver('task.totalBudgetLeft')
        child = task.Task()
        child.addEffort(effort.Effort(child, date.DateTime(2000,1,1,10,0,0),
            date.DateTime(2000,1,1,11,0,0)))
        self.task.addChild(child)
        self.failIf(self.events)

    def testAddChildWithBudgetCausesTotalBudgetLeftNotification(self):
        child = task.Task()
        child.setBudget(date.TimeDelta(hours=100))
        self.registerObserver('task.totalBudgetLeft')
        self.task.addChild(child)
        self.assertEqual(patterns.Event(self.task, 'task.totalBudgetLeft',
            date.TimeDelta(hours=100)), self.events[0])

    def testAddChildWithEffortCausesTotalTimeSpentNotification(self):
        child = task.Task()
        child.addEffort(effort.Effort(child, date.DateTime(2000,1,1,10,0,0),
            date.DateTime(2000,1,1,11,0,0)))
        self.registerObserver('task.totalTimeSpent')
        self.task.addChild(child)
        self.assertEqual(patterns.Event(self.task, 'task.totalTimeSpent',
            date.TimeDelta(hours=1)), self.events[0])

    def testAddChildWithoutEffortCausesNoTotalTimeSpentNotification(self):
        self.registerObserver('task.totalTimeSpent')
        child = task.Task()
        self.task.addChild(child)
        self.failIf(self.events)

    def testAddChildWithHigherPriorityCausesTotalPriorityNotification(self):
        child = task.Task()
        child.setPriority(10)
        self.registerObserver('task.totalPriority')
        self.task.addChild(child)
        self.assertEqual(patterns.Event(self.task, 'task.totalPriority', 10), 
            self.events[0])

    def testAddChildWithLowerPriorityCausesNoTotalPriorityNotification(self):
        child = task.Task()
        child.setPriority(-10)
        self.registerObserver('task.totalPriority')
        self.task.addChild(child)
        self.failIf(self.events)

    def testAddChildWithRevenueCausesTotalRevenueNotification(self):
        child = task.Task()
        child.setFixedFee(1000)
        self.registerObserver('task.totalRevenue')
        self.task.addChild(child)
        self.assertEqual(patterns.Event(self.task, 'task.totalRevenue', 1000),
            self.events[0])

    def testAddChildWithoutRevenueCausesNoTotalRevenueNotification(self):
        self.registerObserver('task.totalRevenue')
        child = task.Task()
        self.task.addChild(child)
        self.failIf(self.events)

    def testAddTrackedChildCausesStartTrackingNotification(self):
        child = task.Task()
        child.addEffort(effort.Effort(child))
        self.registerObserver('task.track.start')
        self.task.addChild(child)
        self.assertEqual(patterns.Event(self.task, 'task.track.start',
            child.efforts()[0]), self.events[0])

    # Constructor

    def testNewChild_WithSubject(self):
        child = self.task.newChild(subject='Test')
        self.assertEqual('Test', child.subject())

    # Add effort

    def testAddEffortCausesNoBudgetLeftNotification(self):
        self.registerObserver('task.budgetLeft')
        self.task.addEffort(effort.Effort(self.task))
        self.failIf(self.events)

    def testAddEffortCausesNoTotalBudgetLeftNotification(self):
        self.registerObserver('task.totalBudgetLeft')
        self.task.addEffort(effort.Effort(self.task))
        self.failIf(self.events)
        
    def testAddActiveEffortCausesStartTrackingNotification(self):
        self.registerObserver('task.track.start')
        activeEffort = effort.Effort(self.task)
        self.task.addEffort(activeEffort)
        self.assertEqual([patterns.Event(self.task, 'task.track.start', 
            activeEffort)], self.events)

    # Notes:
    
    def testAddNote(self):
        aNote = note.Note()
        self.task.addNote(aNote)
        self.assertEqual([aNote], self.task.notes())

    def testAddNoteCausesNotification(self):
        eventType = task.Task.notesChangedEventType()
        self.registerObserver(eventType)
        aNote = note.Note()
        self.task.addNote(aNote)
        self.assertEqual([patterns.Event(self.task, eventType, aNote)], 
                         self.events)
        
    # State (FIXME: need to test other attributes too)
 
    def testTaskStateIncludesPriority(self):
        state = self.task.__getstate__()
        self.task.setPriority(10)
        self.task.__setstate__(state)
        self.assertEqual(0, self.task.priority())

    def testTaskStateIncludesRecurrence(self):
        state = self.task.__getstate__()
        self.task.setRecurrence('weekly')
        self.task.__setstate__(state)
        self.failIf(self.task.recurrence())

    def testTaskStateIncludesNotes(self):
        state = self.task.__getstate__()
        self.task.addNote(note.Note())
        self.task.__setstate__(state)
        self.failIf(self.task.notes())
        
    def testTaskStateIncludesReminder(self):
        state = self.task.__getstate__()
        self.task.setReminder(date.DateTime.now() + date.TimeDelta(seconds=10))
        self.task.__setstate__(state)
        self.failIf(self.task.reminder())                     


class TaskDueTodayTest(TaskTestCase, CommonTaskTests):
    def taskCreationKeywordArguments(self):
        return [{'dueDate': date.Today()}]
    
    def testIsDueToday(self):
        self.failUnless(self.task.dueToday())

    def testDaysLeft(self):
        self.assertEqual(0, self.task.timeLeft().days)

    def testDueDate(self):
        self.assertEqual(self.taskCreationKeywordArguments()[0]['dueDate'], 
            self.task.dueDate())


class TaskDueTomorrowTest(TaskTestCase, CommonTaskTests):
    def taskCreationKeywordArguments(self):
        return [{'dueDate': date.Tomorrow()}]
        
    def testIsDueTomorrow(self):
        self.failUnless(self.task.dueTomorrow())

    def testDaysLeft(self):
        self.assertEqual(1, self.task.timeLeft().days)

    def testDueDate(self):
        self.assertEqual(self.taskCreationKeywordArguments()[0]['dueDate'], 
                         self.task.dueDate())


class OverdueTaskTest(TaskTestCase, CommonTaskTests):
    def taskCreationKeywordArguments(self):
        return [{'dueDate' : date.Yesterday()}]

    def testIsOverdue(self):
        self.failUnless(self.task.overdue())
        
    def testCompletedOverdueTaskIsNoLongerOverdue(self):
        self.task.setCompletionDate()
        self.failIf(self.task.overdue())

    def testDueDate(self):
        self.assertEqual(self.taskCreationKeywordArguments()[0]['dueDate'], self.task.dueDate())


class CompletedTaskTest(TaskTestCase, CommonTaskTests):
    def taskCreationKeywordArguments(self):
        return [{'completionDate': date.Today()}]
        
    def testATaskWithACompletionDateIsCompleted(self):
        self.failUnless(self.task.completed())

    def testSettingTheCompletionDateToInfiniteMakesTheTaskUncompleted(self):
        self.task.setCompletionDate(date.Date())
        self.failIf(self.task.completed())

    def testSettingTheCompletionDateToAnotherDateLeavesTheTaskCompleted(self):
        self.task.setCompletionDate(date.Yesterday())
        self.failUnless(self.task.completed())


class TaskCompletedInTheFutureTest(TaskTestCase, CommonTaskTests):
    def taskCreationKeywordArguments(self):
        return [{'completionDate': date.Tomorrow()}]
        
    def testATaskWithAFutureCompletionDateIsCompleted(self):
        self.failUnless(self.task.completed())


class InactiveTaskTest(TaskTestCase, CommonTaskTests):
    def taskCreationKeywordArguments(self):
        return [{'startDate': date.Tomorrow()}]

    def testTaskWithStartDateInTheFutureIsInactive(self):
        self.failUnless(self.task.inactive())
        
    def testACompletedTaskWithStartDateInTheFutureIsNotInactive(self):
        self.task.setCompletionDate()
        self.failIf(self.task.inactive())

    def testStartDate(self):
        self.assertEqual(date.Tomorrow(), self.task.startDate())

    def testSetStartDateToTodayMakesTaskActive(self):
        self.task.setStartDate(date.Today())
        self.failUnless(self.task.active())


class TaskWithSubject(TaskTestCase, CommonTaskTests):
    eventTypes = [task.Task.subjectChangedEventType()]

    def taskCreationKeywordArguments(self):
        return [{'subject': 'Subject'}]
        
    def testSubject(self):
        self.assertEqual('Subject', self.task.subject())

    def testSetSubject(self):
        self.task.setSubject('Done')
        self.assertEqual('Done', self.task.subject())

    def testSetSubjectNotification(self):
        self.task.setSubject('Done')
        self.assertEqual('Done', self.events[0].value())

    def testSetSubjectUnchangedDoesNotTriggerNotification(self):
        self.task.setSubject(self.task.subject())
        self.failIf(self.events)
        
    def testRepresentationEqualsSubject(self):
        self.assertEqual(self.task.subject(), repr(self.task))


class TaskWithDescriptionTest(TaskTestCase, CommonTaskTests):
    def taskCreationKeywordArguments(self):
        return [{'description': 'Description'}]

    def testDescription(self):
        self.assertEqual('Description', self.task.description())

    def testSetDescription(self):
        self.task.setDescription('New description')
        self.assertEqual('New description', self.task.description())

                
class TwoTasksTest(TaskTestCase):
    def taskCreationKeywordArguments(self):
        return [{}, {}]
        
    def testTwoDefaultTasksAreNotEqual(self):
        self.assertNotEqual(self.task1, self.task2)

    def testEqualStatesDoesNotImplyEqualTasks(self):
        state = self.task1.__getstate__()
        self.task2.__setstate__(state)
        self.assertNotEqual(self.task1, self.task2)


class NewChildTestCase(TaskTestCase):
    def setUp(self):
        super(NewChildTestCase, self).setUp()
        self.child = self.task.newChild()


class NewChildOfDefaultTaskTest(NewChildTestCase):
    def taskCreationKeywordArguments(self):
        return [{}]
    
    def testNewChildHasSameDueDateAsParent(self):
        self.assertEqual(self.task.dueDate(), self.child.dueDate())
                
    def testNewChildHasStartDateToday(self):
        self.assertEqual(date.Today(), self.child.startDate())

    def testNewChildIsNotCompleted(self):
        self.failIf(self.child.completed())


class NewChildOfInactiveTask(NewChildTestCase):
    def taskCreationKeywordArguments(self):
        return [{'startDate': date.Tomorrow()}]
    
    def testChildHasSameStartDateAsParent(self):
        self.assertEqual(self.task.startDate(), self.child.startDate())


class NewChildOfActiveTask(NewChildTestCase):
    def taskCreationKeywordArguments(self):
        return [{'startDate': date.Yesterday()}]

    def testNewChildHasStartDateToday(self):
        self.assertEqual(date.Today(), self.child.startDate())
        

class TaskWithChildTest(TaskTestCase, CommonTaskTests, NoBudgetTests):
    def taskCreationKeywordArguments(self):
        return [{'children': [task.Task(subject='child')]}]
    
    def testRemoveChildNotification(self):
        self.registerObserver(task.Task.removeChildEventType())
        self.task1.removeChild(self.task1_1)
        self.assertEqual([patterns.Event(self.task1, 
            task.Task.removeChildEventType(), self.task1_1)], self.events)

    def testRemoveChildWithBudgetCausesTotalBudgetNotification(self):
        self.task1_1.setBudget(date.TimeDelta(hours=100))
        self.registerObserver('task.totalBudget')
        self.task1.removeChild(self.task1_1)
        self.assertEqual(patterns.Event(self.task1, 'task.totalBudget',
            date.TimeDelta()), self.events[0])

    def testRemoveChildWithoutBudgetCausesNoTotalBudgetNotification(self):
        self.registerObserver('task.totalBudget')
        self.task1.removeChild(self.task1_1)
        self.failIf(self.events)

    def testRemoveChildWithEffortFromTaskWithBudgetCausesTotalBudgetLeftNotification(self):
        self.registerObserver('task.totalBudgetLeft')
        self.task1.setBudget(date.TimeDelta(hours=100))
        self.task1_1.addEffort(effort.Effort(self.task1_1, 
            date.DateTime(2005,1,1,11,0,0), date.DateTime(2005,1,1,12,0,0)))
        self.task1.removeChild(self.task1_1)
        self.assertEqual(patterns.Event(self.task1, 'task.totalBudgetLeft',
            date.TimeDelta(hours=100)), self.events[0])

    def testRemoveChildWithEffortFromTaskWithoutBudgetCausesNoTotalBudgetLeftNotification(self):
        self.registerObserver('task.totalBudgetLeft')
        self.task1_1.addEffort(effort.Effort(self.task1_1, 
            date.DateTime(2005,1,1,11,0,0), date.DateTime(2005,1,1,12,0,0)))
        self.task1.removeChild(self.task1_1)
        self.failIf(self.events)

    def testRemoveChildWithEffortCausesTotalTimeSpentNotification(self):
        self.task1_1.addEffort(effort.Effort(self.task1_1, 
            date.DateTime(2005,1,1,11,0,0), date.DateTime(2005,1,1,12,0,0)))
        self.registerObserver('task.totalTimeSpent')
        self.task1.removeChild(self.task1_1)
        self.assertEqual(patterns.Event(self.task1, 'task.totalTimeSpent',
            date.TimeDelta()), self.events[0])

    def testRemoveChildWithoutEffortCausesNoTotalTimeSpentNotification(self):
        self.registerObserver('task.totalTimeSpent')
        self.task1.removeChild(self.task1_1)
        self.failIf(self.events)

    def testRemoveChildWithHighPriorityCausesTotalPriorityNotification(self):
        self.task1_1.setPriority(10)
        self.registerObserver('task.totalPriority')
        self.task1.removeChild(self.task1_1)
        self.assertEqual(patterns.Event(self.task1, 'task.totalPriority', 0), 
            self.events[0])

    def testRemoveChildWithLowPriorityCausesNoTotalPriorityNotification(self):
        self.task1_1.setPriority(-10)
        self.registerObserver('task.totalPriority')
        self.task1.removeChild(self.task1_1)
        self.failIf(self.events)

    def testRemoveChildWithRevenueCausesTotalRevenueNotification(self):
        self.task1_1.setFixedFee(1000)
        self.registerObserver('task.totalRevenue')
        self.task1.removeChild(self.task1_1)
        self.assertEqual(patterns.Event(self.task1, 'task.totalRevenue', 0), 
            self.events[0])

    def testRemoveChildWithoutRevenueCausesNoTotalRevenueNotification(self):
        self.registerObserver('task.totalRevenue')
        self.task1.removeChild(self.task1_1)
        self.failIf(self.events)

    def testRemoveTrackedChildCausesStopTrackingNotification(self):
        self.registerObserver('task.track.stop')
        self.task1_1.addEffort(effort.Effort(self.task1_1))
        self.task1.removeChild(self.task1_1)
        self.assertEqual(patterns.Event(self.task1, 'task.track.stop',
            self.task1_1.efforts()[0]), self.events[0])

    def testRemoveTrackedChildWhenParentIsTrackedTooCausesNoStopTrackingNotification(self):
        self.registerObserver('task.track.stop')
        self.task1.addEffort(effort.Effort(self.task1))
        self.task1_1.addEffort(effort.Effort(self.task1_1))
        self.task1.removeChild(self.task1_1)
        self.failIf(self.events)

    def testNotAllChildrenAreCompleted(self):
        self.failIf(self.task1.allChildrenCompleted())
        
    def testAllChildrenAreCompletedAfterMarkingTheOnlyChildAsCompleted(self):
        self.task1_1.setCompletionDate()
        self.failUnless(self.task1.allChildrenCompleted())

    def testTimeLeftRecursivelyIsInfinite(self):
        self.assertEqual(date.TimeDelta.max, 
            self.task1.timeLeft(recursive=True))

    def testTimeSpentRecursivelyIsZero(self):
        self.assertEqual(date.TimeDelta(), self.task.timeSpent(recursive=True))

    def testRecursiveBudgetWhenParentHasNoBudgetWhileChildDoes(self):
        self.task1_1.setBudget(oneHour)
        self.assertEqual(oneHour, self.task.budget(recursive=True))

    def testRecursiveBudgetLeftWhenParentHasNoBudgetWhileChildDoes(self):
        self.task1_1.setBudget(oneHour)
        self.assertEqual(oneHour, self.task.budgetLeft(recursive=True))

    def testRecursiveBudgetWhenBothHaveBudget(self):
        self.task1_1.setBudget(oneHour)
        self.task.setBudget(oneHour)
        self.assertEqual(twoHours, self.task.budget(recursive=True))

    def testRecursiveBudgetLeftWhenBothHaveBudget(self):
        self.task1_1.setBudget(oneHour)
        self.task.setBudget(oneHour)
        self.assertEqual(twoHours, self.task.budgetLeft(recursive=True))
        
    def testRecursiveBudgetLeftWhenChildBudgetIsAllSpent(self):
        self.task1_1.setBudget(oneHour)
        self.addEffort(oneHour, self.task1_1)
        self.assertEqual(zeroHour, self.task.budgetLeft(recursive=True))

    def testTotalBudgetNotification(self):
        self.registerObserver('task.totalBudget')
        self.task1_1.setBudget(oneHour)
        self.assertEqual(oneHour, self.events[0].value())

    def testTotalBudgetNotification_WhenRemovingChild(self):
        self.task1_1.setBudget(oneHour)
        self.registerObserver('task.totalBudget')
        self.task.removeChild(self.task1_1)
        self.assertEqual([patterns.Event(self.task, 'task.totalBudget', 
                                         date.TimeDelta(0))], 
                         self.events)

    def testTotalBudgetLeftNotification_WhenChildBudgetChanges(self):
        self.registerObserver('task.totalBudgetLeft')
        self.task1_1.setBudget(oneHour)
        self.assertEqual(oneHour, self.events[0].value())

    def testTotalBudgetLeftNotification_WhenChildTimeSpentChanges(self):
        self.task1_1.setBudget(twoHours)
        self.registerObserver('task.totalBudgetLeft')
        self.task1_1.addEffort(effort.Effort(self.task1_1,
            date.DateTime(2005,1,1,10,0,0), date.DateTime(2005,1,1,11,0,0)))
        self.assertEqual(oneHour, self.events[0].value())

    def testNoTotalBudgetLeftNotification_WhenChildTimeSpentChangesButNoBudget(self):
        self.registerObserver('task.totalBudgetLeft')
        self.task1_1.addEffort(effort.Effort(self.task1_1,
            date.DateTime(2005,1,1,10,0,0), date.DateTime(2005,1,1,11,0,0)))
        self.failIf(self.events)

    def testTotalTimeSpentNotification(self):
        self.registerObserver('task.totalTimeSpent')
        self.task1_1.addEffort(effort.Effort(self.task1_1,
            date.DateTime(2005,1,1,10,0,0), date.DateTime(2005,1,1,11,0,0)))
        self.assertEqual(oneHour, self.events[0].value())

    def testTotalPriorityNotification(self):
        self.registerObserver('task.totalPriority')
        self.task1_1.setPriority(10)
        self.assertEqual(10, self.events[0].value())

    def testNoTotalPriorityNotification_WithLowerChildPriority(self):
        self.registerObserver('task.totalPriority')
        self.task1_1.setPriority(-1)
        self.assertEqual([patterns.Event(self.task1_1, 'task.totalPriority', -1)], 
            self.events)

    def testTotalRevenueNotification(self):
        self.registerObserver('task.totalRevenue')
        self.task1_1.setHourlyFee(100)
        self.task1_1.addEffort(effort.Effort(self.task1_1,
            date.DateTime(2005,1,1,10,0,0), date.DateTime(2005,1,1,12,0,0)))
        self.assertEqual(200, self.events[0].value())

    def testIsBeingTrackedRecursiveWhenChildIsNotTracked(self):
        self.failIf(self.task1.isBeingTracked(recursive=True))

    def testIsBeingTrackedRecursiveWhenChildIsTracked(self):
        self.failIf(self.task1.isBeingTracked(recursive=True))
        self.task1_1.addEffort(effort.Effort(self.task1_1))
        self.failUnless(self.task1.isBeingTracked(recursive=True))

    def testNotificationWhenChildIsBeingTracked(self):
        self.registerObserver('task.track.start')
        activeEffort = effort.Effort(self.task1_1)
        self.task1_1.addEffort(activeEffort)
        self.assertEqual(patterns.Event(self.task1, 'task.track.start',
            activeEffort), self.events[-1])

    def testNotificationWhenChildTrackingStops(self):
        self.registerObserver('task.track.stop')
        activeEffort = effort.Effort(self.task1_1)
        self.task1_1.addEffort(activeEffort)
        activeEffort.setStop()
        self.assertEqual(patterns.Event(self.task1, 'task.track.stop',
            activeEffort), self.events[-1])

    def testSetFixedFeeOfChild(self):
        self.registerObserver('task.totalFixedFee')
        self.task1_1.setFixedFee(1000)
        self.failUnless(patterns.Event(self.task, 'task.totalFixedFee', 1000) \
                        in self.events)

    def testGetFixedFeeRecursive(self):
        self.task.setFixedFee(2000)
        self.task1_1.setFixedFee(1000)
        self.assertEqual(3000, self.task.fixedFee(recursive=True))

    def testRecursiveRevenueFromFixedFee(self):
        self.task.setFixedFee(2000)
        self.task1_1.setFixedFee(1000)
        self.assertEqual(3000, self.task.revenue(recursive=True))
        

class TaskWithGrandChildTest(TaskTestCase, CommonTaskTests, NoBudgetTests):
    def taskCreationKeywordArguments(self):
        return [{}, {}, {}]
    
    def setUp(self):
        super(TaskWithGrandChildTest, self).setUp()
        self.task1.addChild(self.task2)
        self.task2.addChild(self.task3)

    def testTimeSpentRecursivelyIsZero(self):
        self.assertEqual(date.TimeDelta(), self.task.timeSpent(recursive=True))
        

class TaskWithOneEffortTest(TaskTestCase, CommonTaskTests):
    eventTypes = ['task.track.start', 'task.track.stop']

    def taskCreationKeywordArguments(self):
        return [{'efforts': [effort.Effort(None, date.DateTime(2005,1,1),
            date.DateTime(2005,1,2))]}]

    def testTimeSpentOnTaskEqualsEffortDuration(self):
        self.assertEqual(self.task1effort1.duration(), self.task.timeSpent())
        
    def testTimeSpentRecursivelyOnTaskEqualsEffortDuration(self):
        self.assertEqual(self.task1effort1.duration(), 
            self.task.timeSpent(recursive=True))

    def testTimeSpentOnTaskIsZeroAfterRemovalOfEffort(self):
        self.task.removeEffort(self.task1effort1)
        self.assertEqual(date.TimeDelta(), self.task.timeSpent())
        
    def testTaskEffortListContainsTheOneEffortAdded(self):
        self.assertEqual([self.task1effort1], self.task.efforts())

    def testStartTrackingEffort(self):
        self.task1effort1.setStop(date.DateTime.max)
        self.assertEqual(patterns.Event(self.task, 'task.track.start',
            self.task1effort1), self.events[0])

    def testStopTrackingEffort(self):
        self.task1effort1.setStop(date.DateTime.max)
        self.task1effort1.setStop()
        self.assertEqual(patterns.Event(self.task, 'task.track.stop',
            self.task1effort1), self.events[1])

    def testRevenueWithEffortButWithZeroFee(self):
        self.assertEqual(0, self.task.revenue())

    def testNotifyEffortOfColorChange(self):
        self.registerObserver(effort.Effort.colorChangedEventType())
        self.task.setColor(wx.RED)
        self.assertEqual(patterns.Event(self.task1effort1,
            effort.Effort.colorChangedEventType(), wx.RED), self.events[0])
        

class TaskWithTwoEffortsTest(TaskTestCase, CommonTaskTests):
    def taskCreationKeywordArguments(self):
        return [{'efforts': [effort.Effort(None, date.DateTime(2005,1,1),
            date.DateTime(2005,1,2)), effort.Effort(None, 
            date.DateTime(2005,2,1), date.DateTime(2005,2,2))]}]
    
    def setUp(self):
        super(TaskWithTwoEffortsTest, self).setUp()
        self.totalDuration = self.task1effort1.duration() + \
            self.task1effort2.duration()
                    
    def testTimeSpentOnTaskEqualsEffortDuration(self):
        self.assertEqual(self.totalDuration, self.task.timeSpent())

    def testTimeSpentRecursivelyOnTaskEqualsEffortDuration(self):
        self.assertEqual(self.totalDuration, self.task.timeSpent(recursive=True))


class TaskWithActiveEffort(TaskTestCase, CommonTaskTests):
    eventTypes = ['task.track.start', 'task.track.stop']

    def taskCreationKeywordArguments(self):
        return [{'efforts': [effort.Effort(None, date.DateTime.now())]}]
    
    def testTaskIsBeingTracked(self):
        self.failUnless(self.task.isBeingTracked())
        
    def testStopTracking(self):
        self.task.stopTracking()
        self.failIf(self.task.isBeingTracked())
        
    def testNoStartTrackingEventBecauseActiveEffortWasAddedViaConstructor(self):
        self.failIf(self.events)

    def testNoStartTrackingEventAfterAddingASecondActiveEffort(self):
        self.task.addEffort(effort.Effort(self.task))
        self.failIf(self.events)

    def testNoStopTrackingEventAfterRemovingFirstOfTwoActiveEfforts(self):
        secondEffort = effort.Effort(self.task)
        self.task.addEffort(secondEffort)
        self.task.removeEffort(secondEffort)
        self.failIf(self.events)

    def testRemoveActiveEffortShouldCauseStopTrackingEvent(self):
        self.task.removeEffort(self.task1effort1)
        self.assertEqual(patterns.Event(self.task, 'task.track.stop', 
            self.task1effort1), self.events[0])

    def testStopTrackingEvent(self):
        self.task.stopTracking()
        self.assertEqual([patterns.Event(self.task, 'task.track.stop', 
            self.task1effort1)], self.events)


class TaskWithChildAndEffortTest(TaskTestCase, CommonTaskTests):
    def taskCreationKeywordArguments(self):
        return [{'children': [task.Task(efforts=[effort.Effort(None, 
            date.DateTime(2005,2,1), date.DateTime(2005,2,2))])], 
            'efforts': [effort.Effort(None, date.DateTime(2005,1,1), 
            date.DateTime(2005,1,2))]}]

    def testTimeSpentOnTaskEqualsEffortDuration(self):
        self.assertEqual(self.task1effort1.duration(), self.task1.timeSpent())

    def testTimeSpentRecursivelyOnTaskEqualsTotalEffortDuration(self):
        self.assertEqual(self.task1effort1.duration() + self.task1_1effort1.duration(), 
                         self.task1.timeSpent(recursive=True))

    def testEffortsRecursive(self):
        self.assertEqual([self.task1effort1, self.task1_1effort1],
            self.task1.efforts(recursive=True))

    def testRecursiveRevenue(self):
        self.task.setHourlyFee(100)
        self.task1_1.setHourlyFee(100)
        self.assertEqual(4800, self.task.revenue(recursive=True))
        

class TaskWithGrandChildAndEffortTest(TaskTestCase, CommonTaskTests):
    def taskCreationKeywordArguments(self):
        return [{'children': [task.Task(children=[task.Task(efforts=\
            [effort.Effort(None, date.DateTime(2005,3,1), 
            date.DateTime(2005,3,2))])], efforts=[effort.Effort(None, 
            date.DateTime(2005,2,1), date.DateTime(2005,2,2))])], 
            'efforts': [effort.Effort(None, date.DateTime(2005,1,1), 
            date.DateTime(2005,1,2))]}]

    def testTimeSpentRecursivelyOnTaskEqualsTotalEffortDuration(self):
        self.assertEqual(self.task1effort1.duration() + self.task1_1effort1.duration() + \
                         self.task1_1_1effort1.duration(), 
                         self.task1.timeSpent(recursive=True))

    def testEffortsRecursive(self):
        self.assertEqual([self.task1effort1, self.task1_1effort1, self.task1_1_1effort1],
            self.task1.efforts(recursive=True))

    
class TaskWithBudgetTest(TaskTestCase, CommonTaskTests):
    def taskCreationKeywordArguments(self):
        return [{'budget': twoHours}]
    
    def setUp(self):
        super(TaskWithBudgetTest, self).setUp()
        self.oneHourEffort = effort.Effort(self.task, 
            date.DateTime(2005,1,1,13,0), date.DateTime(2005,1,1,14,0))
                                          
    def expectedBudget(self):
        return self.taskCreationKeywordArguments()[0]['budget']
    
    def testBudget(self):
        self.assertEqual(self.expectedBudget(), self.task.budget())

    def testBudgetLeft(self):
        self.assertEqual(self.expectedBudget(), self.task.budgetLeft())

    def testBudgetLeftAfterHalfSpent(self):
        self.addEffort(oneHour)
        self.assertEqual(oneHour, self.task.budgetLeft())

    def testBudgetNotifications(self):
        self.registerObserver('task.budgetLeft')
        self.addEffort(oneHour)
        self.assertEqual(oneHour, self.events[0].value())

    def testBudgetLeftAfterAllSpent(self):
        self.addEffort(twoHours)
        self.assertEqual(zeroHour, self.task.budgetLeft())

    def testBudgetLeftWhenOverBudget(self):
        self.addEffort(threeHours)
        self.assertEqual(-oneHour, self.task.budgetLeft())

    def testRecursiveBudget(self):
        self.assertEqual(self.expectedBudget(), 
            self.task.budget(recursive=True))
        
    def testRecursiveBudgetWithChildWithoutBudget(self):
        self.task.addChild(task.Task())
        self.assertEqual(self.expectedBudget(), 
            self.task.budget(recursive=True))

    def testBudgetIsCopiedWhenTaskIsCopied(self):
        copy = self.task.copy()
        self.assertEqual(copy.budget(), self.task.budget())
        self.task.setBudget(oneHour)
        self.assertEqual(twoHours, copy.budget())


class TaskReminderTestCase(TaskTestCase, CommonTaskTests):
    eventTypes = ['task.reminder']

    def taskCreationKeywordArguments(self):
        return [{'reminder': date.DateTime(2005,1,1)}]

    def initialReminder(self):
        return self.taskCreationKeywordArguments()[0]['reminder']
    
    def testReminder(self):
        self.assertReminder(self.initialReminder())
    
    def testSetReminder(self):
        someOtherTime = date.DateTime(2005,1,2)
        self.task.setReminder(someOtherTime)
        self.assertReminder(someOtherTime)

    def testCancelReminder(self):
        self.task.setReminder()
        self.assertReminder(None)
        
    def testCancelReminderWithMaxDateTime(self):
        self.task.setReminder(date.DateTime.max)
        self.assertReminder(None)
        
    def testTaskNotifiesObserverOfNewReminder(self):
        newReminder = self.initialReminder() + date.TimeDelta(seconds=1)
        self.task.setReminder(newReminder)
        self.assertEqual(newReminder, self.events[0].value())
            
    def testNewReminderCancelsPreviousReminder(self):
        self.task.setReminder()
        self.assertEqual(None, self.events[0].value())
        
    def testMarkCompletedCancelsReminder(self):
        self.task.setCompletionDate()
        self.assertReminder(None)


class TaskSettingTestCase(TaskTestCase, CommonTaskTests):
    eventTypes = ['task.setting.shouldMarkCompletedWhenAllChildrenCompleted']

    
class MarkTaskCompletedWhenAllChildrenCompletedSettingIsTrueFixture(TaskSettingTestCase):
    def taskCreationKeywordArguments(self):
        return [{'shouldMarkCompletedWhenAllChildrenCompleted': True}]
    
    def testSetting(self):
        self.assertEqual(True, 
            self.task.shouldMarkCompletedWhenAllChildrenCompleted)
    
    def testSetSetting(self):
        self.task.shouldMarkCompletedWhenAllChildrenCompleted = False
        self.assertEqual(False, 
            self.task.shouldMarkCompletedWhenAllChildrenCompleted)

    def testSetSettingCausesNotification(self):
        self.task.shouldMarkCompletedWhenAllChildrenCompleted = False
        self.assertEqual(False, self.events[0].value())
        

class MarkTaskCompletedWhenAllChildrenCompletedSettingIsFalseFixture(TaskTestCase):
    def taskCreationKeywordArguments(self):
        return [{'shouldMarkCompletedWhenAllChildrenCompleted': False}]
    
    def testSetting(self):
        self.assertEqual(False, 
            self.task.shouldMarkCompletedWhenAllChildrenCompleted)
    
    def testSetSetting(self):
        self.task.shouldMarkCompletedWhenAllChildrenCompleted = True
        self.assertEqual(True, 
            self.task.shouldMarkCompletedWhenAllChildrenCompleted)
        

class AttachmentTestCase(TaskTestCase, CommonTaskTests):
    eventTypes = [task.Task.attachmentsChangedEventType()]


class TaskWithoutAttachmentFixture(AttachmentTestCase):
    def testRemoveNonExistingAttachmentRaisesNoException(self):
        self.task.removeAttachments('Non-existing attachment')
        
    def testAddEmptyListOfAttachments(self):
        self.task.addAttachments()
        self.failIf(self.events, self.events)
        
    
class TaskWithAttachmentFixture(AttachmentTestCase):
    def taskCreationKeywordArguments(self):
        return [{'attachments': ['/home/frank/attachment.txt']}]

    def testAttachments(self):
        for idx, name in enumerate(self.taskCreationKeywordArguments()[0]['attachments']):
            self.assertEqual(attachment.FileAttachment(name), self.task.attachments()[idx])
                                 
    def testRemoveNonExistingAttachment(self):
        self.task.removeAttachments('Non-existing attachment')

        for idx, name in enumerate(self.taskCreationKeywordArguments()[0]['attachments']):
            self.assertEqual(attachment.FileAttachment(name), self.task.attachments()[idx])

    def testCopy_CreatesNewListOfAttachments(self):
        copy = self.task.copy()
        self.assertEqual(copy.attachments(), self.task.attachments())
        self.task.removeAttachments(self.task.attachments()[0])
        self.assertNotEqual(copy.attachments(), self.task.attachments())

    def testCopy_CopiesIndividualAttachments(self):
        copy = self.task.copy()
        self.assertEqual(copy.attachments()[0].location(),
                         self.task.attachments()[0].location())
        self.task.attachments()[0].setDescription('new')
        # The location of a copy is actually the same; it's a filename
        # or URI.
        self.assertEqual(copy.attachments()[0].location(),
                         self.task.attachments()[0].location())


class TaskWithAttachmentAddedTestCase(AttachmentTestCase):
    def setUp(self):
        super(TaskWithAttachmentAddedTestCase, self).setUp()
        self.attachment = attachment.FileAttachment('./test.txt')
        self.task.addAttachments(self.attachment)


class TaskWithAttachmentAddedFixture(TaskWithAttachmentAddedTestCase):
    def testAddAttachment(self):
        self.failUnless(self.attachment in self.task.attachments())
        
    def testNotification(self):
        self.failUnless(self.events)


class TaskWithAttachmentRemovedFixture(TaskWithAttachmentAddedTestCase):
    def setUp(self):
        super(TaskWithAttachmentRemovedFixture, self).setUp()
        self.task.removeAttachments(self.attachment)

    def testRemoveAttachment(self):
        self.failIf(self.attachment in self.task.attachments())
        
    def testNotification(self):
        self.assertEqual(2, len(self.events))

        
class RecursivePriorityFixture(TaskTestCase, CommonTaskTests):
    def taskCreationKeywordArguments(self):
        return [{'priority': 1, 'children': [task.Task(priority=2)]}]

    def testPriority_RecursiveWhenChildHasLowestPriority(self):
        self.task1_1.setPriority(0)
        self.assertEqual(1, self.task1.priority(recursive=True))

    def testPriority_RecursiveWhenParentHasLowestPriority(self):
        self.assertEqual(2, self.task1.priority(recursive=True))
        
    def testPriority_RecursiveWhenChildHasHighestPriorityAndIsCompleted(self):
        self.task1_1.setCompletionDate()
        self.assertEqual(1, self.task1.priority(recursive=True))
        
    def testTotalPriorityNotificationWhenMarkingChildCompleted(self):
        self.registerObserver('task.totalPriority')
        self.task1_1.setCompletionDate()
        self.assertEqual(1, self.events[0].value())
        
    def testTotalPriorityNotificationWhenMarkingChildUncompleted(self):
        self.task1_1.setCompletionDate()
        self.registerObserver('task.totalPriority')
        self.task1_1.setCompletionDate(date.Date())
        self.assertEqual(2, self.events[0].value())


class TaskWithFixedFeeFixture(TaskTestCase, CommonTaskTests):
    def taskCreationKeywordArguments(self):
        return [{'fixedFee': 1000}]
    
    def testSetFixedFeeViaContructor(self):
        self.assertEqual(1000, self.task.fixedFee())

    def testRevenueFromFixedFee(self):
        self.assertEqual(1000, self.task.revenue())


class TaskWithHourlyFeeFixture(TaskTestCase, CommonTaskTests):
    def taskCreationKeywordArguments(self):
        return [{'hourlyFee': 100}]
    
    def setUp(self):
        super(TaskWithHourlyFeeFixture, self).setUp()
        self.effort = effort.Effort(self.task, date.DateTime(2005,1,1,10,0,0),
            date.DateTime(2005,1,1,11,0,0))
            
    def testSetHourlyFeeViaConstructor(self):
        self.assertEqual(100, self.task.hourlyFee())
    
    def testRevenue_WithoutEffort(self):
        self.assertEqual(0, self.task.revenue())
        
    def testRevenue_WithOneHourEffort(self):
        self.task.addEffort(effort.Effort(self.task, date.DateTime(2005,1,1,10,0,0),
                            date.DateTime(2005,1,1,11,0,0)))
        self.assertEqual(100, self.task.revenue())    
    
    def testRevenue_Notification(self):
        self.registerObserver('task.revenue')
        self.task.addEffort(self.effort)
        self.assertEqual([patterns.Event(self.task, 'task.revenue', 100)], 
            self.events)

    def testAddingEffortDoesNotTriggerRevenueNotificationForEffort(self):
        self.registerObserver('effort.revenue')
        self.task.addEffort(self.effort)
        self.assertEqual([], self.events)


class RecurringTaskTestCase(TaskTestCase):
    def taskCreationKeywordArguments(self):
        return [dict(recurrence=self.createRecurrence())]
    

class RecurringTaskWithChildTestCase(TaskTestCase):
    def taskCreationKeywordArguments(self):
        return [dict(recurrence=self.createRecurrence(),
                     children=[task.Task(subject='child')])]


class RecurringTaskWithRecurringChildTestCase(TaskTestCase):
    def taskCreationKeywordArguments(self):
        return [dict(recurrence=self.createRecurrence(),
                     children=[task.Task(subject='child', 
                               recurrence=self.createRecurrence())])]


class CommonRecurrenceTests(CommonTaskTests):        
    def testSetRecurrenceViaConstructor(self):
        self.assertEqual(self.createRecurrence(), self.task.recurrence())

    def testMarkCompletedSetsNewStartDateIfItWasSetPreviously(self):
        startDate = self.task.startDate()
        self.task.setCompletionDate()
        self.assertEqual(self.createRecurrence()(startDate), self.task.startDate())

    def testMarkCompletedSetsNewDueDateIfItWasSetPreviously(self):
        dueDate = date.Tomorrow()
        self.task.setDueDate(dueDate)
        self.task.setCompletionDate()
        self.assertEqual(self.createRecurrence()(dueDate), self.task.dueDate())

    def testMarkCompletedDoesNotSetStartDateIfItWasNotSetPreviously(self):
        self.task.setStartDate(date.Date())
        self.task.setCompletionDate()
        self.assertEqual(date.Date(), self.task.startDate())

    def testMarkCompletedDoesNotSetDueDateIfItWasNotSetPreviously(self):
        self.task.setCompletionDate()
        self.assertEqual(date.Date(), self.task.dueDate())
                
    def testRecurringTaskIsNotCompletedWhenMarkedCompleted(self):
        self.task.setCompletionDate()
        self.failIf(self.task.completed())

    def testMarkCompletedDoesNotSetReminderIfItWasNotSetPreviously(self):
        self.task.setCompletionDate()
        self.assertEqual(None, self.task.reminder())
    
    def testMarkCompletedSetsNewReminderIfItWasSetPreviously(self):
        reminder = date.DateTime.now() + date.TimeDelta(seconds=10)
        self.task.setReminder(reminder)
        self.task.setCompletionDate()
        self.assertEqual(self.createRecurrence()(reminder), self.task.reminder())
        
    def testCopyRecurrence(self):
        self.assertEqual(self.task.copy().recurrence(), self.task.recurrence())
                
        
class TaskWithWeeklyRecurrenceFixture(RecurringTaskTestCase,  
                                      CommonRecurrenceTests):
    def createRecurrence(self):
        return date.Recurrence('weekly')
        
        
class TaskWithDailyRecurrenceFixture(RecurringTaskTestCase, 
                                     CommonRecurrenceTests):
    def createRecurrence(self):
        return date.Recurrence('daily')


class TaskWithMonthlyRecurrenceFixture(RecurringTaskTestCase,
                                       CommonRecurrenceTests):
    def createRecurrence(self):
        return date.Recurrence('monthly')


class TaskWithYearlyRecurrenceFixture(RecurringTaskTestCase,
                                      CommonRecurrenceTests):
    def createRecurrence(self):
        return date.Recurrence('yearly')
       

class TaskWithDailyRecurrenceThatHasRecurredFixture( \
        RecurringTaskTestCase, CommonRecurrenceTests):
    initialRecurrenceCount = 3
    
    def createRecurrence(self):
        return date.Recurrence('daily', count=self.initialRecurrenceCount)
    


class TaskWithDailyRecurrenceThatHasMaxRecurrenceCountFixture( \
        RecurringTaskTestCase, CommonRecurrenceTests):
    maxRecurrenceCount = 2
    
    def createRecurrence(self):
        return date.Recurrence('daily', max=self.maxRecurrenceCount)

    def testRecurLessThanMaxRecurrenceCount(self):
        for i in range(self.maxRecurrenceCount):
            self.task.setCompletionDate()
        self.failIf(self.task.completed())
          
    def testRecurExactlyMaxRecurrenceCount(self):
        for i in range(self.maxRecurrenceCount + 1):
            self.task.setCompletionDate()
        self.failUnless(self.task.completed())


class CommonRecurrenceTestsWithChild(CommonRecurrenceTests):
    def testChildStartDateRecursToo(self):
        self.task.setCompletionDate()
        self.assertEqual(self.task.startDate(), 
                         self.task.children()[0].startDate())

    def testChildDueDateRecursToo_ParentAndChildHaveNoDueDate(self):
        self.task.setCompletionDate()
        self.assertEqual(self.task.dueDate(), 
                         self.task.children()[0].dueDate())

    def testChildDueDateRecursToo_ParentAndChildHaveSameDueDate(self):
        child = self.task.children()[0]
        self.task.setDueDate(date.Tomorrow())
        child.setDueDate(date.Tomorrow())
        self.task.setCompletionDate()
        self.assertEqual(self.task.dueDate(), 
                         self.task.children()[0].dueDate())

    def testChildDueDateRecursToo_ChildHasEarlierDueDate(self):
        child = self.task.children()[0]
        self.task.setDueDate(date.Tomorrow())
        child.setDueDate(date.Today())
        self.task.setCompletionDate()
        self.assertEqual(self.createRecurrence()(date.Today()),
                         self.task.children()[0].dueDate())


class CommonRecurrenceTestsWithRecurringChild(CommonRecurrenceTests):
    def testChildDoesNotRecurWhenParentDoes(self):
        origStartDate = self.task.children()[0].startDate()
        self.task.setCompletionDate()
        self.assertEqual(origStartDate, self.task.children()[0].startDate())
        
        
class TaskWithWeeklyRecurrenceWithChildFixture(RecurringTaskWithChildTestCase,
                                              CommonRecurrenceTestsWithChild):
    def createRecurrence(self):
        return date.Recurrence('weekly')
    

class TaskWithDailyRecurrenceWithChildFixture(RecurringTaskWithChildTestCase,
                                             CommonRecurrenceTestsWithChild):
    def createRecurrence(self):
        return date.Recurrence('daily')
    
    
class TaskWithWeeklyRecurrenceWithRecurringChildFixture(\
    RecurringTaskWithRecurringChildTestCase, 
    CommonRecurrenceTestsWithRecurringChild):
    
    def createRecurrence(self):
        return date.Recurrence('weekly')

    
class TaskWithDailyRecurrenceWithRecurringChildFixture(\
    RecurringTaskWithRecurringChildTestCase, 
    CommonRecurrenceTestsWithRecurringChild):
    
    def createRecurrence(self):
        return date.Recurrence('daily')

