import test, effort, task, date

class EffortListTest(test.TestCase):
    def setUp(self):
        self.notifications = 0
        self.task = task.Task()
        self.taskList = task.TaskList()
        self.taskList.append(self.task)
        self.effortList = effort.EffortList(self.taskList)
        self.effortList.registerObserver(self.notify, self.notify, self.notify)
        self.effort = effort.Effort(self.task, date.DateTime(2004, 1, 1), date.DateTime(2004, 1, 2))
        
    def testCreate(self):
        self.assertEqual(0, len(self.effortList))
    
    def notify(self, *args):
        self.notifications += 1
            
    def testNotificationAfterAppend(self):
        self.task.addEffort(self.effort)
        self.assertEqual(1, self.notifications)
        
    def testNotificationAfterEffortChange(self):
        self.task.addEffort(self.effort)
        self.effort.setStop(date.DateTime.now())
        self.assertEqual(2, self.notifications)
        
    def testGetEffortForTask(self):
        self.task.addEffort(self.effort)
        self.assertEqual([self.effort], self.effortList.getEffortForTask(self.task))
    
    def testGetEffortForTasks(self):
        self.task.addEffort(self.effort)
        self.assertEqual([self.effort], self.effortList.getEffortForTasks([self.task]))
        
    def testGetEffortForTasks_Recursive(self):
        child = task.Task()
        self.task.addChild(child)
        self.taskList.append(child)
        childEffort = effort.Effort(child, date.DateTime(2004, 1, 1), date.DateTime(2004, 1, 2))
        self.task.addEffort(self.effort)
        child.addEffort(childEffort)
        self.assertEqual([self.effort, childEffort], self.effortList.getEffortForTasks([self.task], 
            recursive=True))
        
    def testGetTimeSpentForTask(self):
        self.task.addEffort(self.effort)
        self.assertEqual(self.effort.duration(), self.effortList.getTimeSpentForTask(self.task))
        
    def testGetTotalTimeSpentForTask(self):
        child = task.Task()
        self.task.addChild(child)
        self.taskList.append(child)
        childEffort = effort.Effort(child, date.DateTime(2004, 3, 1), date.DateTime(2004, 3, 2))
        self.task.addEffort(self.effort)
        child.addEffort(childEffort)
        self.assertEqual(self.effort.duration()+childEffort.duration(), 
            self.effortList.getTotalTimeSpentForTask(self.task))

    def testMaxDateTime_EmptyList(self):
        self.assertEqual(None, self.effortList.maxDateTime())
        
    def testMaxDateTime_OneEffort(self):
        self.task.addEffort(self.effort)
        self.assertEqual(self.effort.getStop(), self.effortList.maxDateTime())
        
    def testMaxDateTime_TwoEfforts(self):
        self.task.addEffort(self.effort)
        recentEffort = effort.Effort(self.task, date.DateTime.now(), date.DateTime.now())
        self.task.addEffort(recentEffort)
        self.assertEqual(recentEffort.getStop(), self.effortList.maxDateTime())
        

class EffortListCacheTest(test.TestCase):
    def setUp(self):
        self.taskList = task.TaskList()
        self.effortList = effort.EffortList(self.taskList)
        self.task1 = task.Task()
        self.task2 = task.Task()
        self.taskList.extend([self.task1, self.task2])
        self.effort1A = effort.Effort(self.task1, date.DateTime.now())
        self.effort1B = effort.Effort(self.task1, date.DateTime.now())
        self.task1.addEffort(self.effort1A)
        self.effort2 = effort.Effort(self.task2, date.DateTime.now())
        
    def assertCache(self, cacheExpected):
        self.assertEqual(cacheExpected, self.effortList._timeSpentCache)
            
    def testCache_AfterAppend(self):
        self.assertCache({})
        
    def testCache_AfterGetEffortForTask(self):
        result = self.effortList.getTimeSpentForTask(self.task1)
        self.assertCache({(self.task1,) : result})
        
    def testCache_AfterChange(self):
        result = self.effortList.getTimeSpentForTask(self.task1)
        self.effort1A._notifyObserversOfChange()
        self.assertCache({})
        
    def testCache_AfterChangeToAnotherEffort(self):
        self.task2.addEffort(self.effort2)
        result = self.effortList.getTimeSpentForTask(self.task1)
        self.effort2._notifyObserversOfChange()
        self.assertCache({(self.task1,) : result})
        
    def testCache_AfterAddEffortForSameTask(self):
        result = self.effortList.getTimeSpentForTask(self.task1)
        self.task1.addEffort(self.effort1B)
        self.assertCache({})

    def testCache_AfterAddEffortForOtherTask(self):
        result = self.effortList.getTimeSpentForTask(self.task1)
        self.task2.addEffort(self.effort2)
        self.assertCache({(self.task1,) : result})
        
    def testCache_AfterRemoveEffortForSameTask(self):
        self.task1.addEffort(self.effort1B)
        result = self.effortList.getTimeSpentForTask(self.task1)
        self.task1.removeEffort(self.effort1B)
        self.assertCache({})

    def testCache_AfterRemoveEffortForOtherTask(self):
        self.task2.addEffort(self.effort2)
        result = self.effortList.getTimeSpentForTask(self.task1)
        self.task2.removeEffort(self.effort2)
        self.assertCache({(self.task1,) : result})
        
    def testCache_AfterRemoveOfTwoEffortsForTheSameTask(self):
        self.task1.addEffort(self.effort1B)
        result = self.effortList.getTimeSpentForTask(self.task1)
        self.task1.removeEffort(self.effort1A)
        self.task1.removeEffort(self.effort1B)
        self.assertCache({})


class SingleTaskEffortListTest(test.TestCase):
    def setUp(self):
        self.notifications = 0
        self.taskList = task.TaskList()
        self.task1 = task.Task()
        self.task2 = task.Task()
        self.taskList.extend([self.task1, self.task2])
        self.effortList = effort.EffortList(self.taskList)
        self.effort1 = effort.Effort(self.task1, date.DateTime.now())
        self.effort2 = effort.Effort(self.task2, date.DateTime.now())
        self.singleTaskEffortList = effort.SingleTaskEffortList(self.task1, self.effortList)
        self.singleTaskEffortList.registerObserver(self.notify, self.notify, self.notify)
        
    def notify(self, *args):
        self.notifications += 1
        
    def assertResult(self, expectedLength, expectedNotifications):
        self.assertEqual(expectedLength, len(self.singleTaskEffortList))
        self.assertEqual(expectedNotifications, self.notifications)
        
    def testCreate(self):
        self.assertResult(0, 0)
        
    def testAddEffortToOriginalForTheTask(self):
        self.task1.addEffort(self.effort1)
        self.assertResult(1, 1)
        
    def testAddEffortToOriginalForAnotherTask(self):
        self.task2.addEffort(self.effort2)
        self.assertResult(0, 0)
        
    def testChangeEffortForTheTask(self):
        self.task1.addEffort(self.effort1)
        self.effort1.setStop(date.DateTime.now())
        self.assertResult(1, 2)
        
    def testChangeEffortForAnotherTask(self):
        self.task2.addEffort(self.effort2)
        self.effort2.setStop(date.DateTime.now())
        self.assertResult(0, 0)
        
    def testRemoveEffortForTheTask(self):
        self.task1.addEffort(self.effort1)
        self.task1.removeEffort(self.effort1)
        self.assertResult(0, 2)
        
    def testRemoveEffortForAnotherTask(self):
        self.task2.addEffort(self.effort2)
        self.task2.removeEffort(self.effort2)
        self.assertResult(0, 0)
        
    def testCreateWhenEffortListIsFilled(self):
        self.task1.addEffort(self.effort1)
        singleTaskEffortList = effort.SingleTaskEffortList(self.task1, self.effortList)
        self.assertResult(1, 1)
        
    def testChildrensEffortIsIncludedToo(self):
        self.task1.addChild(self.task2)
        self.task1.addEffort(self.effort1)
        self.task2.addEffort(self.effort2)
        self.assertResult(2, 2)
        
    def testChildrensEffortIsIncludedTooEvenWhenParentHasNoEffort(self):
        self.task1.addChild(self.task2)
        self.task2.addEffort(self.effort2)
        self.assertResult(1, 1)