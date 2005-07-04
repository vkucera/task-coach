import test, asserts, task, date, time, wx, effort, sets

__coverage__ = [task.Task]

class TaskTest(test.TestCase, asserts.TaskAsserts):
    def setUp(self):
        self.task = task.Task(subject='Todo')
        self.date = date.Date(2003, 1, 1)

    def testSubject(self):
        self.assertEqual('Todo', self.task.subject())

    def testSetSubject(self):
        self.task.setSubject('Done')
        self.assertEqual('Done', self.task.subject())

    def testId(self):
        self.assertEqual(str(id(self.task)), self.task.id().split(':')[0])

    def testId_HasStringType(self):
        self.assertEqual(type(''), type(self.task.id()))

    def testId_DifferentTasks(self):
        task2 = task.Task()
        self.failIf(task2.id() == self.task.id())

    def testNoDueDate(self):
        self.assertEqual(date.Date(), self.task.dueDate())

    def testDueDate(self):
        anotherTask = task.Task(duedate=self.date)
        self.assertEqual(self.date, anotherTask.dueDate())

    def testSetDueDate(self):
        self.task.setDueDate(self.date)
        self.assertEqual(self.date, self.task.dueDate())

    def testStartDate(self):
        self.assertEqual(date.Today(), self.task.startDate())
        anotherTask = task.Task(startdate=self.date)
        self.assertEqual(self.date, anotherTask.startDate())

    def testSetStartDate(self):
        self.task.setStartDate(self.date)
        self.assertEqual(self.date, self.task.startDate())

    def testCompleted(self):
        self.failIf(self.task.completed())
        self.task.setCompletionDate()
        self.failUnless(self.task.completed())
        self.task.setCompletionDate(date.Date())
        self.failIf(self.task.completed())

    def testCompletionDate(self):
        self.assertEqual(date.Date(), self.task.completionDate())

    def testSetCompletionDate(self):
        self.task.setCompletionDate()
        self.assertEqual(date.Today(), self.task.completionDate())

    def testSetCompletionDateWithDate(self):
        self.task.setCompletionDate(self.date)
        self.assertEqual(self.date, self.task.completionDate())

    def testOverdue(self):
        oldTask = task.Task(duedate=date.Date(1990,1,1))
        self.failUnless(oldTask.overdue())
        oldTask = task.Task(duedate=date.Date(1990,1,1))
        oldTask.setCompletionDate()
        self.failIf(oldTask.overdue())

    def testInactive(self):
        futureTask = task.Task(startdate=date.Tomorrow())
        self.failUnless(futureTask.inactive())
        futureTask = task.Task(startdate=date.Tomorrow())
        futureTask.setCompletionDate()
        self.failIf(futureTask.inactive())

    def testActive(self):
        self.failUnless(task.Task().active())
        
    def testNotDueToday(self):
        self.failIf(self.task.dueToday())

    def testDueToday(self):
        dueToday = task.Task(duedate=date.Today())
        self.failUnless(dueToday.dueToday())

    def testNotDueTomorrow(self):
        self.failIf(self.task.dueTomorrow())

    def testDueTomorrow(self):
        dueTomorrow = task.Task(duedate=date.Tomorrow())
        self.failUnless(dueTomorrow.dueTomorrow())

    def testDaysLeft_DueToday(self):
        dueToday = task.Task(duedate=date.Today())
        self.assertEqual(0, dueToday.timeLeft().days)

    def testDaysLeft_DueTomorrow(self):
        dueTomorrow = task.Task(duedate=date.Tomorrow())
        self.assertEqual(1, dueTomorrow.timeLeft().days)

    def testCopyTask(self):
        original = task.Task(subject='Original', duedate=date.Tomorrow(),
            startdate=date.Tomorrow())
        original.setCompletionDate(date.Tomorrow())
        self.task.addChild(original)
        for childIndex in range(2):
            child = task.Task(subject='Child %d'%childIndex)
            original.addChild(child)
            for grandchildIndex in range(2):
                grandChild = task.Task(subject='Grandchild %d.%d'%(childIndex, 
                    grandchildIndex))
                child.addChild(grandChild)
        copy = original.copy()
        self.assertCopy(original, copy)
        self.assertEqual(original.parent(), copy.parent())

    def testDescription_Default(self):
        self.assertEqual('', self.task.description())

    def testDescription_SetThroughConstructor(self):
        newTask = task.Task(description='Description')
        self.assertEqual('Description', newTask.description())

    def testDescription_SetDescription(self):
        self.task.setDescription('Description')
        self.assertEqual('Description', self.task.description())
        
    def testState(self):
        state = self.task.__getstate__()
        newTask = task.Task()
        newTask.__setstate__(state)
        self.assertEqual(newTask, self.task)
        
    def testRepr(self):
        self.assertEqual(self.task.subject(), repr(self.task))


class TaskNotificationTestCase(test.TestCase):
    def setUp(self):
        self.task = self.createTask()
        self.task.registerObserver(self.onNotify)
        self.__notifications = 0

    def onNotify(self, *args, **kwargs):
        self.__notifications += 1

    def failUnlessNotified(self, notificationsExpected=1):
        self.assertEqual(notificationsExpected, self.__notifications)
        
    def failIfNotified(self):
        self.assertEqual(0, self.__notifications)
        


class TaskNotificationTest(TaskNotificationTestCase):
    def createTask(self):
        return task.Task(subject='Todo')
                
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
        

class SubTaskTest(TaskNotificationTestCase, asserts.TaskAsserts):
    def createTask(self):
        return task.Task(subject='Todo', duedate=date.Tomorrow(),
            startdate=date.Yesterday())

    def testNoChildren(self):
        self.assertEqual([], self.task.children())

    def testNoParent(self):
        self.assertEqual(None, self.task.parent())

    def testAddChild(self):
        child = task.Task()
        self.task.addChild(child)
        self.failUnlessParentAndChild(self.task, child)
        self.failUnlessNotified()

    def testAddCompletedChild(self):
        child = task.Task()
        child.setCompletionDate()
        self.task.addChild(child)
        self.failUnless(self.task.completed())

    def testRemoveChild(self):
        child = task.Task()
        self.task.addChild(child)
        self.task.removeChild(child)
        self.failIfParentHasChild(self.task, child)
        self.failUnlessNotified(2)

    def testRemoveLastNotCompletedChild(self):
        child = task.Task()
        self.task.addChild(child)
        completedChild = task.Task()
        completedChild.setCompletionDate()
        self.task.addChild(completedChild)
        self.task.removeChild(child)
        self.failUnless(self.task.completed())

    def testSetParentInConstructor_DoesNotAffectParent(self):
        child = task.Task(parent=self.task)
        self.failIf(child in self.task.children())
        self.assertEqual(self.task, child.parent())
        self.failIfNotified()

    def testNewSubTask(self):
        child = self.task.newSubTask()
        self.assertEqual(self.task.dueDate(), child.dueDate())
        self.assertEqual(self.task, child.parent())
        self.assertEqual(date.Today(), child.startDate())
        self.failIf(child in self.task.children())
        
    def testNewSubTask_WithSubject(self):
        child = self.task.newSubTask(subject='Test')
        self.assertEqual('Test', child.subject())

    def testAllChildrenCompleted(self):
        self.failIf(self.task.allChildrenCompleted())
        child = task.Task()
        self.task.addChild(child)
        self.failIf(self.task.allChildrenCompleted())
        child.setCompletionDate()
        self.failUnless(self.task.allChildrenCompleted())
        
    def testSetCompletionDate_CompletesChild(self):
        child = task.Task()
        self.task.addChild(child)
        self.task.setCompletionDate()
        self.failUnless(child.completed())
        
    def testSetCompletionDate_WhenChildCompleted(self):
        child = task.Task()
        child.setCompletionDate(date.Yesterday())
        self.task.addChild(child)
        self.task.setCompletionDate()
        self.assertEqual(date.Yesterday(), child.completionDate())

    def testSetCompletionDate_CompletesParent(self):
        child = task.Task()
        self.task.addChild(child)
        child.setCompletionDate()
        self.failUnless(self.task.completed())

    def testSetCompletionDate_UncompletesParent(self):
        child = task.Task()
        self.task.addChild(child)
        self.task.setCompletionDate()
        child.setCompletionDate(date.Date())
        self.failIf(self.task.completed())


class SubTaskDateRelationsTest(test.TestCase, asserts.TaskAsserts):
    def setUp(self):
        self.task = task.Task(subject='Todo', duedate=date.Tomorrow(),
            startdate=date.Yesterday())

    def _createChildren(self, dateFunction, dates):
        for date in dates:
            child = task.Task()
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

    def testStartDateParent_EqualsStartDateOfChildWhenChildHasEarliestStartDate(self):
        self.createChildrenWithStartDate([date.Yesterday(), date.Tomorrow()])
        self.task.setStartDate(date.Today())
        self.assertStartDate(date.Yesterday())

    def testStartDateParent_IgnoreCompletedChildren(self):
        self.createChildrenWithStartDate([date.Today(), date.Tomorrow()])
        self.task.setStartDate(date.Date())
        self.task.children()[0].setCompletionDate()
        self.assertStartDate(date.Tomorrow())

    def testStartDateParent_EqualsParentStartDateWhenAllChildrenCompleted(self):
        self.createChildrenWithStartDate([date.Yesterday(), date.Tomorrow()])
        self.task.setStartDate(date.Today())
        for child in self.task.children():
            child.setCompletionDate()
        self.assertStartDate(date.Today())


class SubTaskRelationsTest(test.TestCase):
    def setUp(self):
        self.parent = task.Task(subject='Parent')
        self.child = task.Task(subject='Child')
        self.parent.addChild(self.child)
        self.grandChild = task.Task(subject='Grandchild')
        self.child.addChild(self.grandChild)

    def testGetAllChildren(self):
        self.assertEqual([self.child, self.grandChild], 
            self.parent.allChildren())

    def testGetAncestors(self):
        self.assertEqual([self.parent, self.child], self.grandChild.ancestors())

    def testGetFamily(self):
        for task in self.parent, self.child, self.grandChild:
            self.assertEqual([self.parent, self.child, self.grandChild], task.family())


class TaskEffortTest(test.TestCase):
    def setUp(self):
        self.task = task.Task()
        self.effort = effort.Effort(self.task, date.DateTime(2005,1,1), date.DateTime(2005,1,2))
        
    def testNoEffort(self):
        self.assertEqual(date.TimeDelta(), self.task.timeSpent())
        
    def testAddEffort(self):
        self.task.addEffort(self.effort)
        self.assertEqual(self.effort.duration(), self.task.timeSpent())
        
    def testRemoveEffort(self):
        self.task.addEffort(self.effort)
        self.task.removeEffort(self.effort)
        self.assertEqual(date.TimeDelta(), self.task.timeSpent())
        
    def testTimeSpent(self):
        self.task.addEffort(self.effort)
        anotherEffort = effort.Effort(self.task, date.DateTime(2005,2,1), date.DateTime(2005,2,2))
        self.task.addEffort(anotherEffort)
        self.assertEqual(self.effort.duration() + anotherEffort.duration(), self.task.timeSpent())
        
    def addChild(self, parent):
        child = task.Task()
        parent.addChild(child)
        childEffort = effort.Effort(child, date.DateTime(2005,2,1), date.DateTime(2005,2,2))
        child.addEffort(childEffort)
        return child, childEffort
        
    def testTimeSpent_Recursively(self):
        self.task.addEffort(self.effort)
        child, childEffort = self.addChild(self.task)
        self.assertEqual(self.effort.duration() + childEffort.duration(),
            self.task.timeSpent(recursive=True))
            
    def testTimespent_RecursivelyWithGrandChild(self):
        self.task.addEffort(self.effort)
        child, childEffort = self.addChild(self.task)
        grandChild, grandChildEffort = self.addChild(child)
        self.assertEqual(self.effort.duration() + childEffort.duration() +
            grandChildEffort.duration(), self.task.timeSpent(recursive=True))
            
    def testIsBeingTracked(self):
        self.task.addEffort(effort.Effort(self.task, date.DateTime.now()))
        self.failUnless(self.task.isBeingTracked())
        
    def testStopTracking(self):
        self.task.addEffort(effort.Effort(self.task, date.DateTime.now()))
        self.task.stopTracking()
        self.failIf(self.task.isBeingTracked())
        
    def testEffortsRecursive(self):
        self.task.addEffort(self.effort)
        child, childEffort = self.addChild(self.task)
        self.assertEqual([self.effort, childEffort],
            self.task.efforts(recursive=True))

    
class TaskBudgetTest(TaskNotificationTestCase):
    def createTask(self):
        self.task = task.Task(subject='Todo')
        self.zero = date.TimeDelta()
        self.oneHour = date.TimeDelta(hours=1)
        self.twoHours = date.TimeDelta(hours=2)
        self.oneHourEffort = effort.Effort(self.task, 
            date.DateTime(2005,1,1,13,0,0), date.DateTime(2005,1,1,14,0,0))
        self.child = task.Task(subject='child')
        self.childEffort = effort.Effort(self.child,
            date.DateTime(2005,1,2,10,0,0), date.DateTime(2005,1,2,11,0,0))
        return self.task
            
    def testBudget_Default(self):
        self.assertEqual(self.zero, self.task.budget())
        
    def testBudget_SetThroughConstructor(self):
        newTask = task.Task(budget=self.oneHour)
        self.assertEqual(self.oneHour, newTask.budget())
        
    def testBudget_SetBudget(self):
        self.task.setBudget(self.oneHour)
        self.assertEqual(self.oneHour, self.task.budget())
    
    def testBudget_Recursive_None(self):
        self.task.addChild(self.child)
        self.assertEqual(self.zero, self.task.budget(recursive=True))
        
    def testBudget_Recursive_ChildWithoutBudget(self):
        self.task.addChild(self.child)
        self.task.setBudget(self.oneHour)
        self.assertEqual(self.oneHour, self.task.budget(recursive=True))
        
    def testBudget_Recursive_ParentWithoutBudget(self):
        self.task.addChild(self.child)
        self.child.setBudget(self.oneHour)
        self.assertEqual(self.oneHour, self.task.budget(recursive=True))
        
    def testBudget_Recursive_BothHaveBudget(self):
        self.task.addChild(self.child)
        self.child.setBudget(self.oneHour)
        self.task.setBudget(self.oneHour)
        self.assertEqual(self.twoHours, self.task.budget(recursive=True))
    
    def testBudgetLeft(self):
        self.task.setBudget(self.oneHour)
        self.assertEqual(self.oneHour, self.task.budgetLeft())
        
    def testBudgetLeft_NoBudget(self):
        self.assertEqual(self.zero, self.task.budgetLeft())
        
    def testBudgetLeft_HalfSpent(self):
        self.task.setBudget(self.twoHours)
        self.task.addEffort(self.oneHourEffort)
        self.assertEqual(self.oneHour, self.task.budgetLeft())
        
    def testBudgetLeft_AllSpent(self):
        self.task.setBudget(self.twoHours)
        self.task.addEffort(self.oneHourEffort)
        self.task.addEffort(self.oneHourEffort)
        self.assertEqual(self.zero, self.task.budgetLeft())
    
    def testBudgetLeft_OverBudget(self):
        self.task.setBudget(self.oneHour)
        self.task.addEffort(self.oneHourEffort)
        self.task.addEffort(self.oneHourEffort)
        self.assertEqual(-self.oneHour, self.task.budgetLeft())
        
    def testBudgetLeft_Recursive_NoBudget(self):
        self.task.addChild(self.child)
        self.assertEqual(self.zero, self.task.budgetLeft(recursive=True))
        
    def testBudgetLeft_Recursive_BudgetNoEffort(self):
        self.task.addChild(self.child)
        self.child.setBudget(self.oneHour)
        self.assertEqual(self.oneHour, self.task.budgetLeft(recursive=True))
        
    def testBudgetLeft_Recursive_BudgetSpent(self):
        self.task.addChild(self.child)
        self.child.setBudget(self.oneHour)
        self.child.addEffort(self.childEffort)
        self.assertEqual(self.zero, self.task.budgetLeft(recursive=True))
        
    def testBudgetIsCopiedWhenTaskIsCopied(self):
        self.task.setBudget(self.oneHour)
        copy = self.task.copy()
        self.assertEqual(copy.budget(), self.task.budget())
        self.task.setBudget(self.twoHours)
        self.assertEqual(self.oneHour, copy.budget())
        
    def testSetBudgetCausesNotification(self):
        self.task.setBudget(self.oneHour)
        self.failUnlessNotified()
        
    def testSetBudgetEqualToCurrentBudgetDoesNotCauseNotification(self):
        self.task.setBudget(self.task.budget())
        self.failIfNotified()

        
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
    def createTask(self):
        self.priority = 5
        self.childPriority = self.priority - 1
        self.child = task.Task(priority=self.childPriority)
        parent = task.Task(priority=self.priority)
        parent.addChild(self.child)
        return parent
        
    def testDefaultPriority(self):
        self.assertEqual(0, task.Task().priority())
        
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
        