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
    taskCreationKeywordArguments = [{}]
    
    def setUp(self):
        self.tasks = self.createTasks()
        self.task = self.tasks[0]
        for index, task in enumerate(self.tasks):
            setattr(self, 'task%d'%(index+1), task)
        
    def createTasks(self):
        return [task.Task(**kwargs) for kwargs in self.taskCreationKeywordArguments]

    def addEffort(self, hours, task=None):
        task = task or self.task
        start = date.DateTime(2005,1,1)
        task.addEffort(effort.Effort(task, start, start+hours))

        
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
        
    def testTaskIsNotInActiveByDefault(self):
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


        
    # move these to another fixture?
    def testSetCompletionDateMakesTaskCompleted(self):
        self.task.setCompletionDate()
        self.failUnless(self.task.completed())

    def testSetCompletionDateDefaultsToToday(self):
        self.task.setCompletionDate()
        self.assertEqual(date.Today(), self.task.completionDate())

    def testSetCompletionDateWithDate(self):
        self.task.setCompletionDate(date.Tomorrow())
        self.assertEqual(date.Tomorrow(), self.task.completionDate())

    def testSetDueDate(self):
        self.date = date.Tomorrow()
        self.task.setDueDate(self.date)
        self.assertEqual(self.date, self.task.dueDate())

    def testSetBudget(self):
        budget = date.TimeDelta(hours=1)
        self.task.setBudget(budget)
        self.assertEqual(budget, self.task.budget())
        

class TaskDueTodayTest(TaskTestCase, CommonTaskTests):
    taskCreationKeywordArguments = [{'duedate': date.Today()}]
    
    def testIsDueToday(self):
        self.failUnless(self.task.dueToday())

    def testDaysLeft(self):
        self.assertEqual(0, self.task.timeLeft().days)

    def testDueDate(self):
        self.assertEqual(self.taskCreationKeywordArguments[0]['duedate'], self.task.dueDate())


class TaskDueTomorrowTest(TaskTestCase, CommonTaskTests):
    taskCreationKeywordArguments = [{'duedate': date.Tomorrow()}]
        
    def testIsDueTomorrow(self):
        self.failUnless(self.task.dueTomorrow())

    def testDaysLeft(self):
        self.assertEqual(1, self.task.timeLeft().days)

    def testDueDate(self):
        self.assertEqual(self.taskCreationKeywordArguments[0]['duedate'], self.task.dueDate())


class OverdueTaskTest(TaskTestCase, CommonTaskTests):
    taskCreationKeywordArguments = [{'duedate' : date.Yesterday()}]

    def testIsOverdue(self):
        self.failUnless(self.task.overdue())
        
    def testCompletedOverdueTaskIsNoLongerOverdue(self):
        self.task.setCompletionDate()
        self.failIf(self.task.overdue())

    def testDueDate(self):
        self.assertEqual(self.taskCreationKeywordArguments[0]['duedate'], self.task.dueDate())


class CompletedTaskTest(TaskTestCase, CommonTaskTests):
    taskCreationKeywordArguments = [{'completiondate': date.Today()}]
        
    def testThatATaskWithACompletionDateIsCompleted(self):
        self.failUnless(self.task.completed())

    def testThatSettingTheCompletionDateToInfiniteMakesTheTaskUncompleted(self):
        self.task.setCompletionDate(date.Date())
        self.failIf(self.task.completed())

    def testThatSettingTheCompletionDateToAnotherDateLeavesTheTaskCompleted(self):
        self.task.setCompletionDate(date.Yesterday())
        self.failUnless(self.task.completed())


class TaskCompletedInTheFutureTest(TaskTestCase, CommonTaskTests):
    taskCreationKeywordArguments = [{'completiondate': date.Tomorrow()}]
        
    def testThatATaskWithAFutureCompletionDateIsCompleted(self):
        self.failUnless(self.task.completed())


class InactiveTaskTest(TaskTestCase, CommonTaskTests):
    taskCreationKeywordArguments = [{'startdate': date.Tomorrow()}]

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
    taskCreationKeywordArguments = [{'subject': 'Subject'}]
        
    def testSubject(self):
        self.assertEqual('Subject', self.task.subject())

    def testSetSubject(self):
        self.task.setSubject('Done')
        self.assertEqual('Done', self.task.subject())

    def testRepresentationEqualsSubject(self):
        self.assertEqual(self.task.subject(), repr(self.task))


class TaskWithDescriptionTest(TaskTestCase, CommonTaskTests):
    taskCreationKeywordArguments = [{'description': 'Description'}]

    def testDescription(self):
        self.assertEqual('Description', self.task.description())

    def testSetDescription(self):
        self.task.setDescription('New description')
        self.assertEqual('New description', self.task.description())


class TaskWithId(TaskTestCase, CommonTaskTests):
    taskCreationKeywordArguments = [{'id_': 'id'}]
        
    def testTaskId(self):
        self.assertEqual('id', self.task.id())

                
class TwoTasksTest(TaskTestCase):
    taskCreationKeywordArguments = [{}, {}]
        
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
    taskCreationKeywordArguments = [{}]
    
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
    taskCreationKeywordArguments = [{'startdate': date.Tomorrow()}]
    
    def testNewSubTaskHasSameStartDateAsParent(self):
        self.assertEqual(self.task.startDate(), self.child.startDate())


class NewSubTaskOfActiveTask(NewSubTaskTestCase):
    taskCreationKeywordArguments = [{'startdate': date.Yesterday()}]

    def testNewSubTaskHasStartDateToday(self):
        self.assertEqual(date.Today(), self.child.startDate())
        

class TaskWithChildTest(TaskTestCase, CommonTaskTests, NoBudgetTests):
    taskCreationKeywordArguments = [{}, {}]
    
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
        


class TaskWithGrandChildTest(TaskTestCase, CommonTaskTests, NoBudgetTests):
    taskCreationKeywordArguments = [{}, {}, {}]
    
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
    def createEfforts(self):
        return [effort.Effort(self.task, date.DateTime.now())]
    
    def testTaskIsBeingTracked(self):
        self.failUnless(self.task.isBeingTracked())
        
    def testStopTracking(self):
        self.task.stopTracking()
        self.failIf(self.task.isBeingTracked())
        
    def testMarkTaskCompletedStopsEffortTracking(self):
        self.task.setCompletionDate()
        self.failIf(self.task.isBeingTracked())


class TaskWithChildAndEffortTest(TaskWithEffortTestCase, CommonTaskTests):
    taskCreationKeywordArguments = [{}, {}]

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
    taskCreationKeywordArguments = [{}, {}, {}]
    
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
    taskCreationKeywordArguments = [{'budget': twoHours}]
    
    def setUp(self):
        super(TaskWithBudgetTest, self).setUp()
        self.oneHourEffort = effort.Effort(self.task, date.DateTime(2005,1,1,13,0),
                                          date.DateTime(2005,1,1,14,0))
                                          
    def expectedBudget(self):
        return self.taskCreationKeywordArguments[0]['budget']
    
    
    def testBudget(self):
        self.assertEqual(self.expectedBudget(), self.task.budget())

    def testBudgetLeft(self):
        self.assertEqual(self.expectedBudget(), self.task.budgetLeft())

    def testBudgetLeftAfterHalfSpent(self):
        self.addEffort(oneHour)
        self.assertEqual(oneHour, self.task.budgetLeft())

    def testBudgetLeftAfterAllSpent(self):
        self.addEffort(twoHours)
        self.assertEqual(zeroHour, self.task.budgetLeft())

    def testBudgetLeftWhenOverBudget(self):
        self.addEffort(threeHours)
        self.assertEqual(-oneHour, self.task.budgetLeft())

    def testRecursiveBudget(self):
        self.assertEqual(self.expectedBudget(), self.task.budget(recursive=True))
        
    def testRecursiveBudgetWithChildWithoutBudget(self):
        self.task.addChild(task.Task())
        self.assertEqual(self.expectedBudget(), self.task.budget(recursive=True))

    def testBudgetIsCopiedWhenTaskIsCopied(self):
        copy = self.task.copy()
        self.assertEqual(copy.budget(), self.task.budget())
        self.task.setBudget(oneHour)
        self.assertEqual(twoHours, copy.budget())
        

                         
                         
##################

class TaskNotificationTestCase(TaskTestCase):
    def setUp(self):
        super(TaskNotificationTestCase, self).setUp()
        self.task.registerObserver(self.onNotify)
        self.__notifications = 0

    def onNotify(self, *args, **kwargs):
        self.__notifications += 1

    def failUnlessNotified(self, notificationsExpected=1):
        self.assertEqual(notificationsExpected, self.__notifications)
        
    def failIfNotified(self):
        self.assertEqual(0, self.__notifications)
        


class TaskNotificationTest(TaskNotificationTestCase):
    taskCreationKeywordArguments = [{'subject': 'Todo'}]
                
    def testSetSubject(self):
        self.task.setSubject('New')
        self.failUnlessNotified()
        
    def testSubject_Unchanged(self):
        self.task.setSubject('Todo')
        self.failIfNotified()
        
    def testSetStartDate(self):
        self.task.setStartDate(date.Tomorrow())
        self.failUnlessNotified()
        
    def testSetStartDate_Unchanged(self):
        self.task.setStartDate(self.task.startDate())
        self.failIfNotified()
        
    def testSetDueDate(self):
        self.task.setDueDate(date.Tomorrow())
        self.failUnlessNotified()
        
    def testSetDueDate_Unchanged(self):
        self.task.setDueDate(self.task.dueDate())
        self.failIfNotified()
        
    def testSetCompletionDate(self):
        self.task.setCompletionDate(date.Today())
        self.failUnlessNotified()
        
    def testSetCompletionDate_Unchanged(self):
        self.task.setCompletionDate(self.task.completionDate())
        self.failIfNotified()
        
    def testSetDescription(self):
        self.task.setDescription('new description')
        self.failUnlessNotified()

    def testSetBudgetCausesNotification(self):
        self.task.setBudget(oneHour)
        self.failUnlessNotified()
        
    def testSetBudgetEqualToCurrentBudgetDoesNotCauseNotification(self):
        self.task.setBudget(self.task.budget())
        self.failIfNotified()
        

class SubTaskTest(TaskNotificationTestCase, asserts.TaskAsserts):
    taskCreationKeywordArguments = [{'subject': 'Todo', 'duedate': date.Tomorrow(),
                            'startdate': date.Yesterday()}]

    def testAddChild(self):
        child = self.task.newSubTask()
        self.task.addChild(child)
        self.failUnlessParentAndChild(self.task, child)
        self.failUnlessNotified()

    def testRemoveChild(self):
        child = self.task.newSubTask()
        self.task.addChild(child)
        self.task.removeChild(child)
        self.failIfParentHasChild(self.task, child)
        self.failUnlessNotified(2)

    def testSetParentInConstructor_DoesNotAffectParent(self):
        child = task.Task(parent=self.task)
        self.failIf(child in self.task.children())
        self.assertEqual(self.task, child.parent())
        self.failIfNotified()
                
    def testNewSubTask_WithSubject(self):
        child = self.task.newSubTask(subject='Test')
        self.assertEqual('Test', child.subject())
    
    def testTimeLeftRecursive(self):
        child = task.Task(duedate=date.Today())
        self.task.addChild(child)
        self.assertEqual(date.TimeDelta(), self.task.timeLeft(recursive=True))


class SubTaskDateRelationsTest(test.TestCase, asserts.TaskAsserts):
    ''' FIXME: to be deleted because of duplication with TaskRelationshipManager? '''
    def setUp(self):
        self.task = task.Task(subject='Todo', duedate=date.Tomorrow(),
            startdate=date.Yesterday())

    def _createChildren(self, dateFunction, dates):
        for date in dates:
            child = self.task.newSubTask()
            self.task.addChild(child)
            getattr(child, dateFunction)(date)

    def createChildrenWithDueDate(self, dueDates):
        self._createChildren('setDueDate', dueDates)

    def createChildrenWithStartDate(self, startDates):
        self._createChildren('setStartDate', startDates)

    def assertDueDate(self, expectedDueDate):
        self.assertEqual(expectedDueDate, self.task.dueDate(recursive=True))
    
    def assertStartDate(self, expectedStartDate):
        self.assertEqual(expectedStartDate, self.task.startDate(recursive=True))
        
    def testDueDateParent_EqualsDueDateChild(self):
        self.createChildrenWithDueDate([date.Today()])
        self.assertDueDate(date.Today())

    def testDueDateParent_EqualsMinDueDateChildren(self):
        self.createChildrenWithDueDate([date.Today(), date.Tomorrow()])
        self.assertDueDate(date.Today())

    def testDueDateParent_IgnoresCompletedChildren(self):
        self.createChildrenWithDueDate([date.Today(), date.Tomorrow()])
        self.task.children()[-1].setCompletionDate()
        self.assertDueDate(date.Today())

    def testDueDateParent_EqualsParentDueDateWhenAllChildrenCompleted(self):
        self.createChildrenWithDueDate([date.Yesterday(), date.Today()])
        for child in self.task.children():
            child.setCompletionDate()
        self.assertDueDate(date.Tomorrow())

    def testStartDateParent_EqualsStartOfParentWhenParentHasEarliestStartDate(self):
        self.createChildrenWithStartDate([date.Today()])
        self.assertStartDate(date.Yesterday())

    def testStartDateParent_EqualsParentStartDateWhenAllChildrenCompleted(self):
        self.createChildrenWithStartDate([date.Yesterday(), date.Tomorrow()])
        self.task.setStartDate(date.Today())
        for child in self.task.children():
            child.setCompletionDate()
        self.assertStartDate(date.Today())
        
        
class TaskCategoryTest(test.TestCase):
    def setUp(self):
        self.task = task.Task()
        self.task.addCategory('test')
        self.child = task.Task()
        self.task.addChild(self.child)
        
    def assertCategories(self, task, *categories):
        self.assertEqual(sets.Set(*categories), task.categories())
        
    def testInitialCategories(self):
        self.assertCategories(task.Task())
        
    def testAddCategory(self):
        self.assertEqual(sets.Set(['test']), self.task.categories())
        
    def testAddCategoryTwice(self):
        self.task.addCategory('test')
        self.assertEqual(sets.Set(['test']), self.task.categories())
        
    def testGetCategoriesRecursiveFromParent(self):
        self.assertEqual(sets.Set(['test']), self.child.categories(recursive=True))
        
    def testGetCategoriesNotRecursive(self):
        self.assertEqual(sets.Set(), self.child.categories())
        
    def testGetCategoriesRecursiveFromGrandParent(self):
        grandchild = task.Task()
        self.child.addChild(grandchild)
        self.assertEqual(sets.Set(['test']), grandchild.categories(recursive=True))
        
    def testRemoveCategory(self):
        self.task.removeCategory('test')
        self.assertEqual(sets.Set(), self.task.categories())
        
    def testRemoveCategoryTwice(self):
        self.task.removeCategory('test')
        self.task.removeCategory('test')
        self.assertEqual(sets.Set(), self.task.categories())
    
    def testCategoriesAreCopiedWhenTaskIsCopied(self):
        copy = self.task.copy()
        self.assertEqual(copy.categories(), self.task.categories())
        
        
class TaskPriorityTest(TaskNotificationTestCase):
    def createTasks(self):
        self.priority = 5
        self.childPriority = self.priority - 1
        self.child = task.Task(priority=self.childPriority)
        parent = task.Task(priority=self.priority)
        parent.addChild(self.child)
        return [parent]
        
    def testSetPriorityOnConstruction(self):
        self.assertEqual(self.priority, self.task.priority())
        
    def testPriorityIsCopiedWhenTaskIsCopied(self):
        copy = self.task.copy()
        self.assertEqual(self.task.priority(), copy.priority())
        
    def testTaskStateIncludesPriority(self):
        state = self.task.__getstate__()
        self.task.setPriority(self.priority+1)
        self.task.__setstate__(state)
        self.assertEqual(self.priority, self.task.priority())
        
    def testSetPriorityCausesNotification(self):
        self.task.setPriority(self.priority+1)
        self.failUnlessNotified()
        
    def testSetPriorityEqualToCurrentPriorityDoesNotCauseNotification(self):
        self.task.setPriority(self.priority)
        self.failIfNotified()
                
    def testPriority_RecursiveWhenChildHasLowestPriority(self):
        self.child.setPriority(0)
        self.assertEqual(self.priority, self.task.priority(recursive=True))

    def testPriority_RecursiveWhenParentHasLowestPriority(self):
        self.task.setPriority(0)
        self.assertEqual(self.childPriority, self.task.priority(recursive=True))
        
    def testNegativePriority(self):
        self.task.setPriority(-1)
        self.assertEqual(-1, self.task.priority())

        
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
        
    def testActiveEffortDoesNotAffectLastModificationTime(self):
        anEffort = effort.Effort(self.task)
        self.task.addEffort(anEffort)
        self.task.setLastModificationTime(self.time)
        anEffort.onEverySecond()
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
        
    def testGetLastModifictionTimeRecursively(self):
        child = task.Task()
        self.task.addChild(child)
        self.task.setLastModificationTime(self.time)
        self.assertLastModificationTimeIsNow(self.task, recursive=True)
        
        
class TaskRevenueTest(TaskNotificationTestCase):
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
        self.task.setHourlyFee(100)
        self.failUnlessNotified()
        
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
        self.task.setFixedFee(1000)
        self.failUnlessNotified()
    
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
