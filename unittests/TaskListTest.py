import test, asserts, task, date

class TaskListTest(test.TestCase, asserts.TaskListAsserts):
    def setUp(self):
        self.taskList = task.TaskList()
        self.taskList.registerObserver(self.notify, self.notify, self.notify)
        self.task1 = task.Task(duedate=date.Date(2010,1,1))
        self.task2 = task.Task(duedate=date.Date(2011,1,1))
        self.task3 = task.Task()
        self.notifications = 0

    def notify(self, observable):
        self.notifications += 1

    def testCreate(self):
        self.assertEmptyTaskList()

    def testCreateWithArgs(self):
        self.taskList = task.TaskList([self.task1])
        self.assertTaskList([self.task1])

    def testGetItem(self):
        self.taskList.append(self.task1)
        self.assertTaskList([self.task1])

    def testCompareEmptyList(self):
        self.assertEqual(self.taskList, self.taskList)

    def testCompareEqualLists(self):
        self.taskList.append(self.task1)
        self.assertEqual(self.taskList, self.taskList)

    def testCompareDifferentLists(self):
        self.taskList.append(self.task1)
        anotherList = task.TaskList()
        self.failIf(self.taskList == anotherList)

    def testAppend(self):
        self.taskList.append(self.task1)
        self.assertTaskList([self.task1])

    def testAppendTaskAlreadyInList(self):
        self.taskList.append(self.task1)
        self.taskList.append(self.task1)
        self.assertTaskList([self.task1, self.task1])

    def testAppendCausesNotification(self):
        self.taskList.append(self.task2)
        self.taskList.append(self.task1)
        self.assertEqual(2, self.notifications)

    def testAppendTaskWithChild(self):
        self.task1.addChild(self.task2)
        self.taskList.append(self.task1)
        self.assertTaskList([self.task1, self.task2])
    
    def testTaskChangeCausesNotification(self):
        self.taskList.append(self.task1)
        self.task1.setSubject('Test')
        self.assertEqual(2, self.notifications)

    def testNrCompleted(self):
        self.assertEqual(0, self.taskList.nrCompleted())
        self.taskList.append(self.task1)
        self.assertEqual(0, self.taskList.nrCompleted())
        self.task1.setCompletionDate()
        self.assertEqual(1, self.taskList.nrCompleted())
    
    def testNrOverdue(self):
        self.assertEqual(0, self.taskList.nrOverdue())
        self.taskList.append(self.task1)
        self.assertEqual(0, self.taskList.nrOverdue())
        self.task1.setDueDate(date.Date(1990, 1, 1))
        self.assertEqual(1, self.taskList.nrOverdue())

    def testAllCompleted(self):
        self.failIf(self.taskList.allCompleted())
        self.task1.setCompletionDate()
        self.taskList.append(self.task1)
        self.failUnless(self.taskList.allCompleted())

    def testNrDueToday(self):
        self.assertEqual(0, self.taskList.nrDueToday())
        self.taskList.append(task.Task(duedate=date.Today()))
        self.assertEqual(1, self.taskList.nrDueToday())

    def testRootTasks(self):
        self.assertEqual([], self.taskList.rootTasks())
        self.taskList.append(self.task1)
        self.assertEqual([self.task1], self.taskList.rootTasks())
        self.task2.addChild(self.task3)
        self.taskList.append(self.task2)
        self.assertEqual([self.task1, self.task2], self.taskList.rootTasks())

class NotificationTimingTest(test.TestCase):
    def setUp(self):
        self.task1 = task.Task()
        self.task2 = task.Task()
        self.taskList = task.TaskList([self.task1])
        self.taskList.registerObserver(self.notify, self.notify, self.notify)
        self.notifications = 0
        self.assertions = {}

    def notify(self, observable):
        self.notifications += 1
        self.assertions.get(self.notifications, lambda: 1)()

    def testAddChild(self):
        self.task2.setParent(self.task1)
        self.assertions = {1: lambda: self.assertEqual(2, len(self.taskList)), 
            2: lambda: self.assertEqual([self.task2], self.task1.children()) }
        self.taskList.append(self.task2)
        self.assertEqual(1, self.notifications)

    def testRemoveChild(self):
        self.task2.setParent(self.task1)
        self.assertions = {3 : lambda: self.assertEqual(1, len(self.taskList)),
            4: lambda: self.assertEqual([], self.task1.children()) }
        self.taskList.append(self.task2)
        self.taskList.remove(self.task2)
        self.assertEqual(3, self.notifications)

class RemoveTasksFromTaskListTest(test.TestCase, asserts.TaskListAsserts, 
        asserts.TaskAsserts):
    def setUp(self):
        self.task1 = task.Task()
        self.task2 = task.Task()
        self.task1.addChild(self.task2)
        self.task3 = task.Task()
        self.task2.addChild(self.task3)
        self.task4 = task.Task()
        self.taskList = task.TaskList([self.task1, self.task4])
        self.originalList = [self.task1, self.task2, self.task3, self.task4]
        self.taskList.registerObserver(self.notify, self.notify, self.notify)
        self.notifications = 0

    def notify(self, observable):
        self.notifications += 1

    def testRemoveTask(self):
        self.taskList.remove(self.task3)
        self.assertTaskList([self.task1, self.task2, self.task4])
        self.assertEqual(2, self.notifications)
        self.failIf(self.task2.children())

    def testRemoveTaskWithChild(self):
        self.taskList.remove(self.task2)
        self.assertTaskList([self.task1, self.task4])
        self.assertEqual(3, self.notifications)
        self.failIf(self.task1.children())

    def testRemoveTaskWithGrandchild(self):
        self.taskList.remove(self.task1)
        self.assertTaskList([self.task4])
        self.assertEqual(3, self.notifications)

    def testUpdateRemovedTask(self):
        self.taskList.remove(self.task3)
        self.task3.setSubject('Test')
        self.assertEqual(2, self.notifications)

    def testAddRemovedTask(self):
        self.taskList.remove(self.task4)
        self.taskList.append(self.task4)
        self.task3.setSubject('Test')
        self.assertEqual(3, self.notifications)

    def testAddRemovedTaskWithChild(self):
        self.taskList.remove(self.task2)
        self.taskList.append(self.task2)
        self.assertTaskList(self.originalList)
        self.assertEqual(4, self.notifications)
        self.task3.setSubject('Test')
        self.assertEqual(5, self.notifications)
        self.failUnlessParentAndChild(self.task2, self.task3)
        self.failUnlessParentAndChild(self.task1, self.task2)

    def testAddRemovedTaskWithGrandchild(self):
        self.taskList.remove(self.task1)
        self.taskList.append(self.task1)
        self.assertTaskList(self.originalList)
        self.assertEqual(4, self.notifications)
        self.task3.setSubject('Test')
        self.assertEqual(5, self.notifications)

    def testExtendWithRemovedTasks(self):
        self.taskList.remove(self.task1)
        self.taskList.remove(self.task4)
        self.taskList.extend([self.task1, self.task4])
        self.assertTaskList(self.originalList)
        self.failUnlessParentAndChild(self.task2, self.task3)
        self.failUnlessParentAndChild(self.task1, self.task2)

    def testRemoveTaskNotInList(self):
        task5 = task.Task()
        self.taskList.remove(task5)
        self.assertTaskList(self.originalList)

    def testRemoveTasks_ParentOnly(self):
        self.taskList.removeItems([self.task1])
        self.assertTaskList([self.task4])
        self.assertEqual(3, self.notifications)

    def testRemoveTasks_GrandchildOnly(self):
        self.taskList.removeItems([self.task3])
        self.assertTaskList([self.task1, self.task2, self.task4])
        self.failIfParentHasChild(self.task2, self.task3)
        self.assertEqual(2, self.notifications)

    def testRemoveTasks_ChildOnly(self):
        self.taskList.removeItems([self.task2])
        self.assertTaskList([self.task1, self.task4])
        self.failIfParentHasChild(self.task1, self.task2)
        self.failUnlessParentAndChild(self.task2, self.task3)
        self.assertEqual(3, self.notifications)

    def testRemoveTasks_ChildAndOtherTask(self):
        self.taskList.removeItems([self.task2, self.task4])
        self.assertTaskList([self.task1])
        self.failIfParentHasChild(self.task1, self.task2)
        self.failUnlessParentAndChild(self.task2, self.task3)
        self.assertEqual(4, self.notifications)

