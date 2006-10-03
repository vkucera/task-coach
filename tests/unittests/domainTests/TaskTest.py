import test, wx, sets, patterns
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
        self.events = []
        for index, task in enumerate(self.tasks):
            taskLabel = 'task%d'%(index+1)
            setattr(self, taskLabel, task)
            self.labelTaskChildrenAndEffort(task, taskLabel)
            self.labelEfforts(task, taskLabel)
        for eventType in self.eventTypes:
            patterns.Publisher().registerObserver(self.onEvent,
                eventType=eventType)
            
    def createTasks(self):
        return [task.Task(**kwargs) for kwargs in \
                self.taskCreationKeywordArguments()]

    def taskCreationKeywordArguments(self):
        return [{}]

    def onEvent(self, event):
        self.events.append(event)
        
    def registerObserver(self, eventType):
        patterns.Publisher().registerObserver(self.onEvent, eventType=eventType)
    
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

    def testTaskHasNoChildrenByDefaultSoNotAllChildrenAreCompleted(self):
        self.failIf(self.task.allChildrenCompleted())

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
        
    def testTaskHasNoFixedFeeByDefault(self):
        self.assertEqual(0, self.task.fixedFee())
        
    def testTaskHasNoRevenueByDefault(self):
        self.assertEqual(0, self.task.revenue())
        
    def testTaskHasNoRecursiveRevenueByDefault(self):
        self.assertEqual(0, self.task.revenue(recursive=True))
        
    def testTaskHasNoHourlyFeeByDefault(self):
        self.assertEqual(0, self.task.hourlyFee())
        
    def testTaskHasNoRecursiveHourlyFeeByDefault(self):
        self.assertEqual(0, self.task.hourlyFee(recursive=True))
                    
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
        self.registerObserver('task.description')
        self.task.setDescription('A new description')
        self.failUnless('A new description', self.events[0].value())

    def testSetDescriptionUnchangedCausesNoNotification(self):
        self.registerObserver('task.description')
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
    
    def testSetFixedFeeCausesRevenueChangeNotification(self):
        self.registerObserver('task.revenue')
        self.task.setFixedFee(1000)
        self.assertEqual([patterns.Event(self.task, 'task.revenue',
            1000)], self.events)
  
    def testSetHourlyFeeViaSetter(self):
        self.task.setHourlyFee(100)
        self.assertEqual(100, self.task.hourlyFee())
  
    def testSetHourlyFeeCausesNotification(self):
        self.registerObserver('task.hourlyFee')
        self.task.setHourlyFee(100)
        self.assertEqual([patterns.Event(self.task, 'task.hourlyFee',
            100)], self.events)
  
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

    def testNewSubTask_WithSubject(self):
        child = self.task.newSubTask(subject='Test')
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


class TaskWithOneCategoryFixture(TaskTestCase, CommonTaskTests):
    def taskCreationKeywordArguments(self):
        return [{'categories': ['category a']}]

    def testCategories(self):
        self.assertEqual(set(['category a']), self.task.categories())

    def testAddCategory(self):
        self.task.addCategory('category b')
        self.assertEqual(set(['category a', 'category b']), 
            self.task.categories())

    def testAddCategoryNotification(self):
        self.registerObserver('task.category.add')
        self.task.addCategory('category b')
        self.assertEqual('category b', self.events[0].value())

    def testAddCategoryTwice(self):
        self.task.addCategory('category a')
        self.assertEqual(set(['category a']), self.task.categories())

    def testAddCategoryTwiceCausesNoNotification(self):
        self.task.addCategory('category a')
        self.failIf(self.events)

    def testRemoveCategory(self):
        self.task.removeCategory('category a')
        self.assertEqual(set(), self.task.categories())

    def testRemoveCategoryNotification(self):
        self.registerObserver('task.category.remove')
        self.task.removeCategory('category a')
        self.assertEqual('category a', self.events[0].value())

    def testRemoveCategoryTwice(self):
        self.task.removeCategory('category a')
        self.task.removeCategory('category a')
        self.assertEqual(set(), self.task.categories())

    def testRemoveCategoryTwiceNotification(self):
        self.registerObserver('task.category.remove')
        self.task.removeCategory('category a')
        self.task.removeCategory('category a')
        self.assertEqual(1, len(self.events))


class ChildAndParentWithOneCategoryFixture(TaskTestCase, CommonTaskTests):
    def taskCreationKeywordArguments(self):
        return [{'categories': ['category a'], 'children': [task.Task()]}]
    
    def testGetCategoriesRecursiveFromParent(self):
        self.assertEqual(set(['category a']), 
            self.task1_1.categories(recursive=True))

    def testGetCategoriesNotRecursive(self):
        self.assertEqual(set(), self.task1_1.categories(recursive=False))
        
    def testGetCategoriesRecursiveFromGrandParent(self):
        grandchild = task.Task()
        self.task1_1.addChild(grandchild)
        self.assertEqual(set(['category a']), 
            grandchild.categories(recursive=True))


class RecursivePriorityFixture(TaskTestCase, CommonTaskTests):
    def taskCreationKeywordArguments(self):
        return [{'priority': 1, 'children': [task.Task(priority=2)]}]

    def testPriority_RecursiveWhenChildHasLowestPriority(self):
        self.task1_1.setPriority(0)
        self.assertEqual(1, self.task1.priority(recursive=True))

    def testPriority_RecursiveWhenParentHasLowestPriority(self):
        self.assertEqual(2, self.task1.priority(recursive=True))


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
        
    def testChangeEffortAffectsLastModificationTime(self):
        anEffort = effort.Effort(self.task)
        self.task.addEffort(anEffort)
        self.task.setLastModificationTime(self.time)
        anEffort.setStop()
        self.assertLastModificationTimeIsNow(self.task)
        
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

            