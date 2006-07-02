import test, wx, sets
import unittests.asserts as asserts
import domain.task as task
import domain.effort as effort
import domain.date as date


''' I'm rearranging these unittests to be more fixture based instead of 
'subject' (e.g. budget, effort, priority) based to see how that feels. '''

# Handy globals
zeroHour = date.TimeDelta(hours=0)
oneHour = date.TimeDelta(hours=1)
twoHours = date.TimeDelta(hours=2)
threeHours = date.TimeDelta(hours=3)


class TaskTestCase(test.TestCase):
    eventTypes = []

    def setUp(self):
        self.tasks = self.createTasks()
        self.task = self.tasks[0]
        self.events = []
        for index, task in enumerate(self.tasks):
            setattr(self, 'task%d'%(index+1), task)
        for eventType in self.eventTypes:
            self.task.registerObserver(self.onEvent, eventType)
            
    def createTasks(self):
        return [task.Task(**kwargs) for kwargs in \
                self.taskCreationKeywordArguments()]

    def taskCreationKeywordArguments(self):
        return [{}]

    def onEvent(self, event):
        self.events.append(event)
    
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

    def testFirstPartOfTaskIdEqualsTheObjectId(self):
        self.assertEqual(str(id(self.task)), self.task.id().split(':')[0])

    def testTaskIdHasStringType(self):
        self.assertEqual(type(''), type(self.task.id()))

    def testTaskHasNoChildrenByDefault(self):
        self.assertEqual([], self.task.children())

    def testTaskHasNoChildrenByDefaultSoAllChildrenReturnsAnEmptyListToo(self):
        self.assertEqual([], self.task.allChildren())

    def testTaskHasNoChildrenByDefaultSoNotAllChildrenAreCompleted(self):
        self.failIf(self.task.allChildrenCompleted())

    def testTaskHasNoParentByDefault(self):
        self.assertEqual(None, self.task.parent())

    def testTaskHasNoAncestorsByDefault(self):
        self.assertEqual([], self.task.ancestors())

    def testTaskIsItsOnlyFamilyByDefault(self):
        self.assertEqual([self.task], self.task.family())        

    def testTaskHasNoEffortByDefault(self):
        self.assertEqual(date.TimeDelta(), self.task.timeSpent())

    def testTaskHasNoRecursiveEffortByDefault(self):
        self.assertEqual(date.TimeDelta(), self.task.timeSpent(recursive=True))

    def testTaskPriorityIsZeroByDefault(self):
        self.assertEqual(0, self.task.priority())

    def testTaskHasNoReminderSetByDefault(self):
        self.assertReminder(None)
    
    def testShouldMarkTaskCompletedIsUndecidedByDefault(self):
        self.assertEqual(None, 
            self.task.shouldMarkCompletedWhenAllChildrenCompleted)
        
    def testTaskHasNoAttachmentsByDefault(self):
        self.assertEqual([], self.task.attachments())
        
    # Setters

    def testSetStartDate(self):
        self.task.setStartDate(date.Yesterday())
        self.assertEqual(date.Yesterday(), self.task.startDate())

    def testSetStartDateNotification(self):
        self.task.registerObserver(self.onEvent, 'task.startDate')
        self.task.setStartDate(date.Yesterday())
        self.assertEqual(date.Yesterday(), self.events[0].value())

    def testSetStartDateUnchangedCausesNoNotification(self):
        self.task.registerObserver(self.onEvent, 'task.startDate')
        self.task.setStartDate(self.task.startDate())
        self.failIf(self.events)

    def testSetDueDate(self):
        self.date = date.Tomorrow()
        self.task.setDueDate(self.date)
        self.assertEqual(self.date, self.task.dueDate())

    def testSetDueDateNotification(self):
        self.task.registerObserver(self.onEvent, 'task.dueDate')
        self.task.setDueDate(date.Tomorrow())
        self.assertEqual(date.Tomorrow(), self.events[0].value())

    def testSetDueDateUnchangedCausesNoNotification(self):
        self.task.registerObserver(self.onEvent, 'task.dueDate')
        self.task.setDueDate(self.task.dueDate())
        self.failIf(self.events)

    def testSetCompletionDate(self):
        self.task.setCompletionDate(date.Today())
        self.assertEqual(date.Today(), self.task.completionDate())

    def testSetCompletionDateNotification(self):
        self.task.registerObserver(self.onEvent, 'task.completionDate')
        self.task.setCompletionDate(date.Today())
        self.assertEqual(date.Today(), self.events[0].value())

    def testSetCompletionDateUnchangedCausesNoNotification(self):
        self.task.registerObserver(self.onEvent, 'task.completionDate')
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
        self.task.registerObserver(self.onEvent, 'task.description')
        self.task.setDescription('A new description')
        self.failUnless('A new description', self.events[0].value())

    def testSetDescriptionUnchangedCausesNoNotification(self):
        self.task.registerObserver(self.onEvent, 'task.description')
        self.task.setDescription(self.task.description())
        self.failIf(self.events)

    def testSetBudget(self):
        budget = date.TimeDelta(hours=1)
        self.task.setBudget(budget)
        self.assertEqual(budget, self.task.budget())

    def testSetBudgetNotification(self):
        self.task.registerObserver(self.onEvent, 'task.budget')
        budget = date.TimeDelta(hours=1)
        self.task.setBudget(budget)
        self.assertEqual(budget, self.events[0].value())

    def testSetBudgetUnchangedCausesNoNotification(self):
        self.task.registerObserver(self.onEvent, 'task.budget')
        self.task.setBudget(self.task.budget())
        self.failIf(self.events)

    def testSetPriority(self):
        self.task.setPriority(10)
        self.assertEqual(10, self.task.priority())

    def testSetPriorityCausesNotification(self):
        self.task.registerObserver(self.onEvent, 'task.priority')
        self.task.setPriority(10)
        self.assertEqual(10, self.events[0].value())

    def testSetPriorityUnchangedCausesNoNotification(self):
        self.task.registerObserver(self.onEvent, 'task.priority')
        self.task.setPriority(self.task.priority())
        self.failIf(self.events)

    def testNegativePriority(self):
        self.task.setPriority(-1)
        self.assertEqual(-1, self.task.priority())

    # Children
        
    def testAddChild(self):
        child = self.task.newSubTask()
        self.task.addChild(child)
        self.failUnlessParentAndChild(self.task, child)

    def testAddChildNotification(self):
        self.task.registerObserver(self.onEvent, 'task.child.add')
        child = self.task.newSubTask()
        self.task.addChild(child)
        self.assertEqual(child, self.events[0].value())

    def testSetParentInConstructor_DoesNotAffectParent(self):
        child = task.Task(parent=self.task)
        self.failIf(child in self.task.children())
        self.assertEqual(self.task, child.parent())
        self.failIf(self.events)

    def testNewSubTask_WithSubject(self):
        child = self.task.newSubTask(subject='Test')
        self.assertEqual('Test', child.subject())

    # State (FIXME: need to test other attributes too)
 
    def testTaskStateIncludesPriority(self):
        state = self.task.__getstate__()
        self.task.setPriority(10)
        self.task.__setstate__(state)
        self.assertEqual(0, self.task.priority())


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
        
    def testThatATaskWithACompletionDateIsCompleted(self):
        self.failUnless(self.task.completed())

    def testThatSettingTheCompletionDateToInfiniteMakesTheTaskUncompleted(self):
        self.task.setCompletionDate(date.Date())
        self.failIf(self.task.completed())

    def testThatSettingTheCompletionDateToAnotherDateLeavesTheTaskCompleted(self):
        self.task.setCompletionDate(date.Yesterday())
        self.failUnless(self.task.completed())


class TaskCompletedInTheFutureTest(TaskTestCase, CommonTaskTests):
    def taskCreationKeywordArguments(self):
        return [{'completionDate': date.Tomorrow()}]
        
    def testThatATaskWithAFutureCompletionDateIsCompleted(self):
        self.failUnless(self.task.completed())


class InactiveTaskTest(TaskTestCase, CommonTaskTests):
    def taskCreationKeywordArguments(self):
        return [{'startDate': date.Tomorrow()}]

    def testThatTaskWithStartDateInTheFutureIsInactive(self):
        self.failUnless(self.task.inactive())
        
    def testThatACompletedTaskWithStartDateInTheFutureIsNotInactive(self):
        self.task.setCompletionDate()
        self.failIf(self.task.inactive())

    def testStartDate(self):
        self.assertEqual(date.Tomorrow(), self.task.startDate())

    def testSetStartDateToTodayMakesTaskActive(self):
        self.task.setStartDate(date.Today())
        self.failUnless(self.task.active())


class TaskWithSubject(TaskTestCase, CommonTaskTests):
    eventTypes = ['task.subject']

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


class TaskWithId(TaskTestCase, CommonTaskTests):
    def taskCreationKeywordArguments(self):
        return [{'id_': 'id'}]
        
    def testTaskId(self):
        self.assertEqual('id', self.task.id())

                
class TwoTasksTest(TaskTestCase):
    def taskCreationKeywordArguments(self):
        return [{}, {}]
        
    def testTwoTasksHaveDifferentIds(self):
        self.assertNotEqual(self.task1.id(), self.task2.id())

    def testTwoDefaultTasksAreNotEqual(self):
        self.assertNotEqual(self.task1, self.task2)

    def testEqualStatesDoesNotImplyEqualTasks(self):
        state = self.task1.__getstate__()
        self.task2.__setstate__(state)
        self.assertNotEqual(self.task1, self.task2)


class NewSubTaskTestCase(TaskTestCase):
    def setUp(self):
        super(NewSubTaskTestCase, self).setUp()
        self.child = self.task.newSubTask()


class NewSubTaskOfDefaultTaskTest(NewSubTaskTestCase):
    def taskCreationKeywordArguments(self):
        return [{}]
    
    def testNewSubTaskParent(self):
        self.assertEqual(self.task, self.child.parent())
                
    def testNewSubTaskIsNotAutomaticallyAddedAsChild(self):
        self.failIf(self.child in self.task.children())

    def testNewSubTaskHasSameDueDateAsParent(self):
        self.assertEqual(self.task.dueDate(), self.child.dueDate())
                
    def testNewSubTaskHasStartDateToday(self):
        self.assertEqual(date.Today(), self.child.startDate())

    def testNewSubTaskIsNotCompleted(self):
        self.failIf(self.child.completed())


class NewSubTaskOfInactiveTask(NewSubTaskTestCase):
    def taskCreationKeywordArguments(self):
        return [{'startDate': date.Tomorrow()}]
    
    def testNewSubTaskHasSameStartDateAsParent(self):
        self.assertEqual(self.task.startDate(), self.child.startDate())


class NewSubTaskOfActiveTask(NewSubTaskTestCase):
    def taskCreationKeywordArguments(self):
        return [{'startDate': date.Yesterday()}]

    def testNewSubTaskHasStartDateToday(self):
        self.assertEqual(date.Today(), self.child.startDate())
        

class TaskWithChildTest(TaskTestCase, CommonTaskTests, NoBudgetTests):
    def taskCreationKeywordArguments(self):
        return [{}, {}]
    
    def setUp(self):
        super(TaskWithChildTest, self).setUp()
        self.task1.addChild(self.task2)
    
    def testParentHasChild(self):
        self.failUnless([self.task2], self.task1.children())
        
    def testChildHasParent(self):
        self.assertEqual(self.task1, self.task2.parent())
        
    def testRemoveChild(self):
        self.task1.removeChild(self.task2)
        self.failIf(self.task1.children())

    def testRemoveChildNotification(self):
        self.task1.registerObserver(self.onEvent, 'task.child.remove')
        self.task1.removeChild(self.task2)
        self.assertEqual('task.child.remove', self.events[0].type())
        self.assertEqual(self.task2, self.events[0].value())

    def testNotAllChildrenAreCompleted(self):
        self.failIf(self.task1.allChildrenCompleted())
        
    def testAllChildrenAreCompletedAfterMarkingTheOnlyChildAsCompleted(self):
        self.task2.setCompletionDate()
        self.failUnless(self.task1.allChildrenCompleted())

    def testGetAllChildren(self):
        self.assertEqual([self.task2], self.task1.allChildren())

    def testGetFamily(self):
        for task in self.tasks:
            self.assertEqual(self.tasks, task.family())

    def testAncestors(self):
        self.assertEqual([self.task1], self.task2.ancestors())

    def testTimeLeftRecursivelyIsInfinite(self):
        self.assertEqual(date.TimeDelta.max, 
            self.task1.timeLeft(recursive=True))

    def testTimeSpentRecursivelyIsZero(self):
        self.assertEqual(date.TimeDelta(), self.task.timeSpent(recursive=True))

    def testRecursiveBudgetWhenParentHasNoBudgetWhileChildDoes(self):
        self.task2.setBudget(oneHour)
        self.assertEqual(oneHour, self.task.budget(recursive=True))

    def testRecursiveBudgetLeftWhenParentHasNoBudgetWhileChildDoes(self):
        self.task2.setBudget(oneHour)
        self.assertEqual(oneHour, self.task.budgetLeft(recursive=True))

    def testRecursiveBudgetWhenBothHaveBudget(self):
        self.task2.setBudget(oneHour)
        self.task.setBudget(oneHour)
        self.assertEqual(twoHours, self.task.budget(recursive=True))

    def testRecursiveBudgetLeftWhenBothHaveBudget(self):
        self.task2.setBudget(oneHour)
        self.task.setBudget(oneHour)
        self.assertEqual(twoHours, self.task.budgetLeft(recursive=True))
        
    def testRecursiveBudgetLeftWhenChildBudgetIsAllSpent(self):
        self.task2.setBudget(oneHour)
        self.addEffort(oneHour, self.task2)
        self.assertEqual(zeroHour, self.task.budgetLeft(recursive=True))

    def testTotalBudgetNotification(self):
        self.task1.registerObserver(self.onEvent, 'task.totalBudget')
        self.task2.setBudget(oneHour)
        self.assertEqual(oneHour, self.events[0].value())

    def testTotalBudgetLeftNotification_WhenChildBudgetChanges(self):
        self.task1.registerObserver(self.onEvent, 'task.totalBudgetLeft')
        self.task2.setBudget(oneHour)
        self.assertEqual(oneHour, self.events[0].value())

    def testTotalBudgetLeftNotification_WhenChildTimeSpentChanges(self):
        self.task2.setBudget(twoHours)
        self.task1.registerObserver(self.onEvent, 'task.totalBudgetLeft')
        self.task2.addEffort(effort.Effort(self.task2,
            date.DateTime(2005,1,1,10,0,0), date.DateTime(2005,1,1,11,0,0)))
        self.assertEqual(oneHour, self.events[0].value())

    def testTotalTimeSpentNotification(self):
        self.task1.registerObserver(self.onEvent, 'task.totalTimeSpent')
        self.task2.addEffort(effort.Effort(self.task2,
            date.DateTime(2005,1,1,10,0,0), date.DateTime(2005,1,1,11,0,0)))
        self.assertEqual(oneHour, self.events[0].value())

    def testTotalPriorityNotification(self):
        self.task1.registerObserver(self.onEvent, 'task.totalPriority')
        self.task2.setPriority(10)
        self.assertEqual(10, self.events[0].value())

    def testTotalPriorityNotification_WithLowerChildPriority(self):
        self.task1.registerObserver(self.onEvent, 'task.totalPriority')
        self.task2.setPriority(-1)
        self.failIf(self.events)

    def testTotalRevenueNotification(self):
        self.task1.registerObserver(self.onEvent, 'task.totalRevenue')
        self.task2.setHourlyFee(100)
        self.task2.addEffort(effort.Effort(self.task2,
            date.DateTime(2005,1,1,10,0,0), date.DateTime(2005,1,1,12,0,0)))
        self.assertEqual(200, self.events[0].value())


class TaskWithGrandChildTest(TaskTestCase, CommonTaskTests, NoBudgetTests):
    def taskCreationKeywordArguments(self):
        return [{}, {}, {}]
    
    def setUp(self):
        super(TaskWithGrandChildTest, self).setUp()
        self.task1.addChild(self.task2)
        self.task2.addChild(self.task3)

    def testGetAllChildren(self):
        self.assertEqual([self.task2, self.task3], self.task1.allChildren())

    def testGetAncestors(self):
        self.assertEqual([self.task1, self.task2], self.task3.ancestors())

    def testGetFamily(self):
        for task in self.tasks:
            self.assertEqual(self.tasks, task.family())

    def testTimeSpentRecursivelyIsZero(self):
        self.assertEqual(date.TimeDelta(), self.task.timeSpent(recursive=True))
        

class TaskWithEffortTestCase(TaskTestCase):
    def setUp(self):
        super(TaskWithEffortTestCase, self).setUp()
        for effort in self.createEfforts():
            effort.task().addEffort(effort)
            

class TaskWithOneEffortTest(TaskWithEffortTestCase, CommonTaskTests):
    def createEfforts(self):
        self.effort = effort.Effort(self.task, date.DateTime(2005,1,1), date.DateTime(2005,1,2))
        return [self.effort]

    def testTimeSpentOnTaskEqualsEffortDuration(self):
        self.assertEqual(self.effort.duration(), self.task.timeSpent())
        
    def testTimeSpentRecursivelyOnTaskEqualsEffortDuration(self):
        self.assertEqual(self.effort.duration(), self.task.timeSpent(recursive=True))

    def testTimeSpentOnTaskIsZeroAfterRemovalOfEffort(self):
        self.task.removeEffort(self.effort)
        self.assertEqual(date.TimeDelta(), self.task.timeSpent())
        
    def testTaskEffortListContainsTheOneEffortAdded(self):
        self.assertEqual([self.effort], self.task.efforts())


class TaskWithTwoEffortsTest(TaskWithEffortTestCase, CommonTaskTests):
    def createEfforts(self):
        self.effort1 = effort.Effort(self.task, date.DateTime(2005,1,1), date.DateTime(2005,1,2))
        self.effort2 = effort.Effort(self.task, date.DateTime(2005,2,1), date.DateTime(2005,2,2))
        self.totalDuration = self.effort1.duration() + self.effort2.duration()
        return [self.effort1, self.effort2]
        
    def testTimeSpentOnTaskEqualsEffortDuration(self):
        self.assertEqual(self.totalDuration, self.task.timeSpent())

    def testTimeSpentRecursivelyOnTaskEqualsEffortDuration(self):
        self.assertEqual(self.totalDuration, self.task.timeSpent(recursive=True))


class TaskWithActiveEffort(TaskWithEffortTestCase, CommonTaskTests):
    eventTypes = ['task.track.start', 'task.track.stop']

    def createEfforts(self):
        return [effort.Effort(self.task, date.DateTime.now())]
    
    def testTaskIsBeingTracked(self):
        self.failUnless(self.task.isBeingTracked())
        
    def testStopTracking(self):
        self.task.stopTracking()
        self.failIf(self.task.isBeingTracked())
        
    def testStartTrackingEvent(self):
        self.assertEqual('task.track.start', self.events[0].type())

    def testNoStartTrackingEventAfterAddingASecondActiveEffort(self):
        self.task.addEffort(effort.Effort(self.task))
        self.assertEqual(1, len(self.events))

    def testNoStopTrackingEventAfterRemovingFirstOfTwoActiveEfforts(self):
        secondEffort = effort.Effort(self.task)
        self.task.addEffort(secondEffort)
        self.task.removeEffort(secondEffort)
        self.assertEqual(1, len(self.events))

    def testRemoveActiveEffortShouldCauseStopTrackingEvent(self):
        self.task.removeEffort(self.task.efforts()[0])
        self.assertEqual('task.track.stop', self.events[1].type())

    def testStopTrackingEvent(self):
        self.task.stopTracking()
        self.assertEqual('task.track.stop', self.events[1].type())


class TaskWithChildAndEffortTest(TaskWithEffortTestCase, CommonTaskTests):
    def taskCreationKeywordArguments(self):
        return [{}, {}]

    def setUp(self):
        super(TaskWithChildAndEffortTest, self).setUp()
        self.task1.addChild(self.task2)

    def createEfforts(self):
        self.effort1 = effort.Effort(self.task1, date.DateTime(2005,1,1), date.DateTime(2005,1,2))
        self.effort2 = effort.Effort(self.task2, date.DateTime(2005,2,1), date.DateTime(2005,2,2))
        return [self.effort1, self.effort2]

    def testTimeSpentOnTaskEqualsEffortDuration(self):
        self.assertEqual(self.effort1.duration(), self.task1.timeSpent())

    def testTimeSpentRecursivelyOnTaskEqualsTotalEffortDuration(self):
        self.assertEqual(self.effort1.duration() + self.effort2.duration(), 
                         self.task1.timeSpent(recursive=True))

    def testEffortsRecursive(self):
        self.assertEqual([self.effort1, self.effort2],
            self.task1.efforts(recursive=True))


class TaskWithGrandChildAndEffortTest(TaskWithEffortTestCase, CommonTaskTests):
    def taskCreationKeywordArguments(self):
        return [{}, {}, {}]
    
    def setUp(self):
        super(TaskWithGrandChildAndEffortTest, self).setUp()
        self.task1.addChild(self.task2)
        self.task2.addChild(self.task3)

    def createEfforts(self):
        self.effort1 = effort.Effort(self.task1, date.DateTime(2005,1,1), date.DateTime(2005,1,2))
        self.effort2 = effort.Effort(self.task2, date.DateTime(2005,2,1), date.DateTime(2005,2,2))
        self.effort3 = effort.Effort(self.task3, date.DateTime(2005,3,1), date.DateTime(2005,3,2))
        return [self.effort1, self.effort2, self.effort3]

    def testTimeSpentRecursivelyOnTaskEqualsTotalEffortDuration(self):
        self.assertEqual(self.effort1.duration() + self.effort2.duration() + self.effort3.duration(), 
                         self.task1.timeSpent(recursive=True))

    def testEffortsRecursive(self):
        self.assertEqual([self.effort1, self.effort2, self.effort3],
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
        self.task.registerObserver(self.onEvent, 'task.budgetLeft')
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


class TaskReminderTestCase(TaskTestCase):
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


class TaskSettingTestCase(TaskTestCase):
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
        

class AttachmentTestCase(TaskTestCase):
    eventTypes = ['task.attachment.add', 'task.attachment.remove']


class TaskWithoutAttachmentFixture(AttachmentTestCase):
    def testRemoveNonExistingAttachmentRaisesNoException(self):
        self.task.removeAttachments('Non-existing attachment')
        
    def testRemoveAllAttachmentsCausesNoNotification(self):
        self.task.removeAllAttachments()
        self.failIf(self.events)

    def testAddEmptyListOfAttachments(self):
        self.task.addAttachments()
        self.failIf(self.events)
        
    
class TaskWithAttachmentFixture(AttachmentTestCase):
    def taskCreationKeywordArguments(self):
        return [{'attachments': ['/home/frank/attachment.txt']}]

    def testAttachments(self):
        self.assertEqual(self.taskCreationKeywordArguments()[0]['attachments'],
                         self.task.attachments())
                                 
    def testRemoveNonExistingAttachment(self):
        self.task.removeAttachments('Non-existing attachment')
        self.assertEqual(self.taskCreationKeywordArguments()[0]['attachments'],
                         self.task.attachments())


class TaskWithAttachmentAddedTestCase(AttachmentTestCase):
    def setUp(self):
        super(TaskWithAttachmentAddedTestCase, self).setUp()
        self.attachment = './test.txt'
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


class TaskWithAllAttachmentsRemovedFixture(TaskWithAttachmentAddedTestCase):
    def setUp(self):
        super(TaskWithAllAttachmentsRemovedFixture, self).setUp()
        self.task.removeAllAttachments()

    def testRemoveAllAttachments(self):
        self.assertEqual([], self.task.attachments())

    def testRemoveAllAttachmentsCausesNotification(self):
        self.assertEqual(2, len(self.events))


class TaskWithOneCategoryFixture(TaskTestCase):
    def setUp(self):
        super(TaskWithOneCategoryFixture, self).setUp()
        self.task.addCategory('category a')

    def testCategories(self):
        self.assertEqual(sets.Set(['category a']), self.task.categories())

    def testAddCategory(self):
        self.task.addCategory('category b')
        self.assertEqual(sets.Set(['category a', 'category b']), 
            self.task.categories())

    def testAddCategoryNotification(self):
        self.task.registerObserver(self.onEvent, 'task.category.add')
        self.task.addCategory('category b')
        self.assertEqual('category b', self.events[0].value())

    def testAddCategoryTwice(self):
        self.task.addCategory('category a')
        self.assertEqual(sets.Set(['category a']), self.task.categories())

    def testAddCategoryTwiceCausesNoNotification(self):
        self.task.addCategory('category a')
        self.failIf(self.events)

    def testRemoveCategory(self):
        self.task.removeCategory('category a')
        self.assertEqual(sets.Set(), self.task.categories())

    def testRemoveCategoryNotification(self):
        self.task.registerObserver(self.onEvent, 'task.category.remove')
        self.task.removeCategory('category a')
        self.assertEqual('category a', self.events[0].value())

    def testRemoveCategoryTwice(self):
        self.task.removeCategory('category a')
        self.task.removeCategory('category a')
        self.assertEqual(sets.Set(), self.task.categories())

    def testRemoveCategoryTwiceNotification(self):
        self.task.registerObserver(self.onEvent, 'task.category.remove')
        self.task.removeCategory('category a')
        self.task.removeCategory('category a')
        self.assertEqual(1, len(self.events))


class ChildAndParentWithOneCategoryFixture(TaskTestCase):
    def setUp(self):
        super(ChildAndParentWithOneCategoryFixture, self).setUp()
        self.task.addCategory('category a')
        self.child = task.Task()
        self.task.addChild(self.child)

    def testGetCategoriesRecursiveFromParent(self):
        self.assertEqual(sets.Set(['category a']), 
            self.child.categories(recursive=True))

    def testGetCategoriesNotRecursive(self):
        self.assertEqual(sets.Set(), self.child.categories(recursive=False))
        
    def testGetCategoriesRecursiveFromGrandParent(self):
        grandchild = task.Task()
        self.child.addChild(grandchild)
        self.assertEqual(sets.Set(['category a']), 
            grandchild.categories(recursive=True))


class RecursivePriorityFixture(TaskTestCase):
    def taskCreationKeywordArguments(self):
        return [{'priority': 1}, {'priority': 2}]

    def setUp(self):
        super(RecursivePriorityFixture, self).setUp()
        self.task1.addChild(self.task2)

    def testPriority_RecursiveWhenChildHasLowestPriority(self):
        self.task2.setPriority(0)
        self.assertEqual(1, self.task1.priority(recursive=True))

    def testPriority_RecursiveWhenParentHasLowestPriority(self):
        self.assertEqual(2, self.task1.priority(recursive=True))


# FIXME: tests below still need to be reorganized by fixture.
        
        
class TaskLastModificationTimeTest(test.TestCase):
    def setUp(self):
        self.time = date.DateTime(2004,1,1)
        self.task = task.Task(lastModificationTime=self.time)
    
    def assertEqualTimes(self, time1, time2):
        delta = time1 - time2
        self.failUnless(abs(delta) < date.TimeDelta(seconds=1))
        
    def assertLastModificationTimeIsNow(self, task, recursive=False):
        self.assertEqualTimes(date.DateTime.now(), task.lastModificationTime(recursive))
        
    def testNewlyCreatedTask(self):
        self.assertLastModificationTimeIsNow(task.Task())
        
    def testSetLastModificationTime(self):
        self.task.setLastModificationTime(date.DateTime.now())
        self.assertLastModificationTimeIsNow(self.task)
        
    def testSetLastModificationTime_ThroughConstructor(self):
        self.assertEqualTimes(self.time, self.task.lastModificationTime())
        
    def testChangeSubjectAffectsLastModificationTime(self):
        self.task.setSubject('New subject')
        self.assertLastModificationTimeIsNow(self.task)
        
    def testChangeDescriptionAffectsLastModificationTime(self):
        self.task.setDescription('New description')
        self.assertLastModificationTimeIsNow(self.task)
        
    def testChangeStartDateAffectsLastModificationTime(self):
        self.task.setStartDate(date.Yesterday())
        self.assertLastModificationTimeIsNow(self.task)
        
    def testChangeDueDateAffectsLastModificationTime(self):
        self.task.setDueDate(date.Tomorrow())
        self.assertLastModificationTimeIsNow(self.task)
        
    def testChangeCompletionDateAffectsLastModificationTime(self):
        self.task.setCompletionDate()
        self.assertLastModificationTimeIsNow(self.task)
        
    def testChangeBudgetAffectsLastModificationTime(self):
        self.task.setBudget(date.TimeDelta(hours=100))
        self.assertLastModificationTimeIsNow(self.task)
        
    def testChangePriorityAffectsLastModificationTime(self):
        self.task.setPriority(42)
        self.assertLastModificationTimeIsNow(self.task)
        
    def testAddCategoryAffectsLastModificationTime(self):
        self.task.addCategory('New category')
        self.assertLastModificationTimeIsNow(self.task)

    def testRemoveCategoryAffectsLastModificationTime(self):
        self.task.addCategory('New category')
        self.task.setLastModificationTime(date.DateTime(2004,1,1))
        self.task.removeCategory('New category')
        self.assertLastModificationTimeIsNow(self.task)
        
    def testAddEffortAffectsLastModificationTime(self):
        self.task.addEffort(effort.Effort(self.task))
        self.assertLastModificationTimeIsNow(self.task)
        
    def testRemoveEffortAffectsLastModificationTime(self):
        anEffort = effort.Effort(self.task)
        self.task.addEffort(anEffort)
        self.task.setLastModificationTime(self.time)
        self.task.removeEffort(anEffort)
        self.assertLastModificationTimeIsNow(self.task)
        
    def testChangeEffortDoesNotAffectLastModificationTime(self):
        anEffort = effort.Effort(self.task)
        self.task.addEffort(anEffort)
        self.task.setLastModificationTime(self.time)
        anEffort.setStop()
        self.assertEqualTimes(self.time, self.task.lastModificationTime())
        
    def testStopTrackingAffectsLastModificationTime(self):
        anEffort = effort.Effort(self.task)
        self.task.addEffort(anEffort)
        self.task.setLastModificationTime(self.time)
        self.task.stopTracking()
        self.assertLastModificationTimeIsNow(self.task)
        
    def testAddChildAffectsLastModificationTime(self):
        self.task.addChild(task.Task())
        self.assertLastModificationTimeIsNow(self.task)
        
    def testRemoveChildAffectsLastModificationTime(self):
        child = task.Task()
        self.task.addChild(child)
        self.task.setLastModificationTime(self.time)
        self.task.removeChild(child)
        self.assertLastModificationTimeIsNow(self.task)
        
    def testChangeChildSubjectDoesNotAffectLastModificationTime(self):
        child = task.Task()
        self.task.addChild(child)
        self.task.setLastModificationTime(self.time)
        child.setSubject('New subject')
        self.assertEqualTimes(self.time, self.task.lastModificationTime())
        
    def testAddChildEffortDoesNotAffectLastModificationTime(self):
        child = task.Task()
        self.task.addChild(child)
        self.task.setLastModificationTime(self.time)
        child.addEffort(effort.Effort(child))
        self.assertEqualTimes(self.time, self.task.lastModificationTime())
        
    def testSetReminderAffectsLastModificationTime(self):
        self.task.setReminder(date.DateTime.now())
        self.assertLastModificationTimeIsNow(self.task)
        
    def testGetLastModifictionTimeRecursively(self):
        child = task.Task()
        self.task.addChild(child)
        self.task.setLastModificationTime(self.time)
        self.assertLastModificationTimeIsNow(self.task, recursive=True)
   
    def testAddAttachmentAffectsLastModificationTime(self):
        self.task.addAttachments('attachment')
        self.assertLastModificationTimeIsNow(self.task)
        
    def testRemoveAttachmentAffectsLastModificationTime(self):
        self.task.addAttachments('attachment')
        self.task.setLastModificationTime(self.time)
        self.task.removeAttachments('attachment')
        self.assertLastModificationTimeIsNow(self.task)
        
    def testRemoveAllAttachmentsAffectsLastModificationTime(self):
        self.task.addAttachments('attachment')
        self.task.setLastModificationTime(self.time)
        self.task.removeAllAttachments()
        self.assertLastModificationTimeIsNow(self.task)

    def testSetHourlyFeeAffectsLastModificationTime(self):
        self.task.setHourlyFee(100)
        self.assertLastModificationTimeIsNow(self.task)

    def testSetFixedFeeAffectsLastModificationTime(self):
        self.task.setFixedFee(1000)
        self.assertLastModificationTimeIsNow(self.task)
        

class TaskRevenueTest(TaskTestCase):
    def createTask(self):
        return task.Task()

    def createEffort(self, task=None):
        return effort.Effort(task or self.task, 
            date.DateTime(2005, 1, 1, 10, 0), date.DateTime(2005, 1, 1, 11, 0))
            
    def testDefaultHourlyFee(self):
        self.assertEqual(0, self.task.hourlyFee())
        
    def testSetHourlyFeeViaConstructor(self):
        t = task.Task(hourlyFee=100)
        self.assertEqual(100, t.hourlyFee())
        
    def testSetHourlyFeeViaSetter(self):
        self.task.setHourlyFee(100)
        self.assertEqual(100, self.task.hourlyFee())

    def testSetHourlyFeeCausesNotification(self):
        self.task.registerObserver(self.onEvent, 'task.hourlyFee')
        self.task.setHourlyFee(100)
        self.assertEqual(100, self.events[0].value())
        
    def testGetHourlyFeeAcceptsRecursiveKeywordArgument(self):
        self.assertEqual(0, self.task.hourlyFee(recursive=False))
        
    def testDefaultRevenue(self):
        self.assertEqual(0, self.task.revenue())
        
    def testRevenueWithEffortButWithZeroFee(self):
        self.task.addEffort(self.createEffort())
        self.assertEqual(0, self.task.revenue())
        
    def testRevenue(self):
        self.task.setHourlyFee(100)
        self.task.addEffort(self.createEffort())
        self.assertEqual(100, self.task.revenue())

    def testRevenueNotification(self):
        self.task.registerObserver(self.onEvent, 'task.revenue')
        self.task.addEffort(self.createEffort())
        self.task.setHourlyFee(100)
        self.assertEqual(100, self.events[0].value())
        
    def testRecursiveRevenue(self):
        self.task.setHourlyFee(100)
        self.task.addEffort(self.createEffort())
        child = task.Task()
        self.task.addChild(child)
        child.setHourlyFee(100)
        child.addEffort(self.createEffort(child))
        self.assertEqual(200, self.task.revenue(recursive=True))
        
    def testDefaultFixedFee(self):
        self.assertEqual(0, self.task.fixedFee())
        
    def testSetFixedFeeViaContructor(self):
        t = task.Task(fixedFee=1000)
        self.assertEqual(1000, t.fixedFee())
        
    def testSetFixedFeeViaSetter(self):
        self.task.setFixedFee(1000)
        self.assertEqual(1000, self.task.fixedFee())
        
    def testSetFixedFeeCausesNotification(self):
        self.task.registerObserver(self.onEvent, 'task.fixedFee')
        self.task.setFixedFee(1000)
        self.assertEqual(1000, self.events[0].value())
    
    def testRevenueFromFixedFee(self):
        self.task.setFixedFee(1000)
        self.assertEqual(1000, self.task.revenue())
        
    def testRecursiveRevenueFromFixedFee(self):
        self.task.setFixedFee(2000)
        child = task.Task()
        self.task.addChild(child)
        child.setFixedFee(1000)
        self.assertEqual(3000, self.task.revenue(recursive=True))
        
    def testGetFixedFeeRecursive(self):
        self.task.setFixedFee(2000)
        child = task.Task()
        self.task.addChild(child)
        child.setFixedFee(1000)
        self.assertEqual(3000, self.task.fixedFee(recursive=True))
