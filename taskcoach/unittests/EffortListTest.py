import test, effort, task, date

class EffortListTest(test.TestCase):
    def setUp(self):
        self.notifications = 0
        self.effortList = effort.EffortList()
        self.effortList.registerObserver(self.notify, self.notify, self.notify)
        self.task = task.Task()
        self.effort = effort.Effort(self.task, date.DateTime(2004,1,1), date.DateTime(2004,1,2))
        
    def testCreate(self):
        self.assertEqual(0, len(self.effortList))
    
    def notify(self, *args):
        self.notifications += 1
            
    def testNotificationAfterAppend(self):
        self.effortList.append(self.effort)
        self.assertEqual(1, self.notifications)
        
    def testNotificationAfterEffortChange(self):
        self.effortList.append(self.effort)
        self.effort.setStop(date.DateTime.now())
        self.assertEqual(2, self.notifications)
        
    def testGetEffortForTask(self):
        self.effortList.append(self.effort)
        self.assertEqual([self.effort], self.effortList.getEffortForTask(self.task))
        
    def testGetEffortSpentForTask(self):
        self.effortList.append(self.effort)
        self.assertEqual(self.effort.duration(), self.effortList.getTimeSpentForTask(self.task))
        
    def testGetTotalEffortSpentForTask(self):
        child = task.Task()
        self.task.addChild(child)
        childEffort = effort.Effort(child, date.DateTime(2004,3,1), date.DateTime(2004,3,2))
        self.effortList.append(self.effort)
        self.effortList.append(childEffort)
        self.assertEqual(self.effort.duration()+childEffort.duration(), 
            self.effortList.getTotalTimeSpentForTask(self.task))

    def testMaxDateTime_EmptyList(self):
        self.assertEqual(None, self.effortList.maxDateTime())
        
    def testMaxDateTime_OneEffort(self):
        self.effortList.append(self.effort)
        self.assertEqual(self.effort.getStop(), self.effortList.maxDateTime())
        
    def testMaxDateTime_TwoEfforts(self):
        self.effortList.append(self.effort)
        recentEffort = effort.Effort(self.task)
        self.effortList.append(recentEffort)
        self.assertEqual(recentEffort.getStop(), self.effortList.maxDateTime())
        

class EffortListCacheTest(test.TestCase):
    def setUp(self):
        self.effortList = effort.EffortList()
        self.task1 = task.Task()
        self.task2 = task.Task()
        self.effort1A = effort.Effort(self.task1, date.DateTime.now())
        self.effort1B = effort.Effort(self.task1, date.DateTime.now())
        self.effort2 = effort.Effort(self.task2, date.DateTime.now())
        self.effortList.append(self.effort1A)
        
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
        self.effortList.append(self.effort2)
        result = self.effortList.getTimeSpentForTask(self.task1)
        self.effort2._notifyObserversOfChange()
        self.assertCache({(self.task1,) : result})
        
    def testCache_AfterAddEffortForSameTask(self):
        result = self.effortList.getTimeSpentForTask(self.task1)
        self.effortList.append(self.effort1B)
        self.assertCache({})

    def testCache_AfterAddEffortForOtherTask(self):
        result = self.effortList.getTimeSpentForTask(self.task1)
        self.effortList.append(self.effort2)
        self.assertCache({(self.task1,) : result})
        
    def testCache_AfterRemoveEffortForSameTask(self):
        self.effortList.append(self.effort1B)
        result = self.effortList.getTimeSpentForTask(self.task1)
        self.effortList.remove(self.effort1B)
        self.assertCache({})

    def testCache_AfterRemoveEffortForOtherTask(self):
        self.effortList.append(self.effort2)
        result = self.effortList.getTimeSpentForTask(self.task1)
        self.effortList.remove(self.effort2)
        self.assertCache({(self.task1,) : result})
        
    def testCache_AfterRemoveOfTwoEffortsForTheSameTask(self):
        self.effortList.append(self.effort1B)
        result = self.effortList.getTimeSpentForTask(self.task1)
        self.effortList.removeItems([self.effort1A, self.effort1B])
        self.assertCache({})

class SingleTaskEffortListTest(test.TestCase):
    def setUp(self):
        self.notifications = 0
        self.effortList = effort.EffortList()
        self.task1 = task.Task()
        self.task2 = task.Task()
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
        self.effortList.append(self.effort1)
        self.assertResult(1, 1)
        
    def testAddEffortToOriginalForAnotherTask(self):
        self.effortList.append(self.effort2)
        self.assertResult(0, 0)
        
    def testChangeEffortForTheTask(self):
        self.effortList.append(self.effort1)
        self.effort1.setStop(date.DateTime.now())
        self.assertResult(1, 2)
        
    def testChangeEffortForAnotherTask(self):
        self.effortList.append(self.effort2)
        self.effort2.setStop(date.DateTime.now())
        self.assertResult(0, 0)
        
    def testRemoveEffortForTheTask(self):
        self.effortList.append(self.effort1)
        self.effortList.remove(self.effort1)
        self.assertResult(0, 2)
        
    def testRemoveEffortForAnotherTask(self):
        self.effortList.append(self.effort2)
        self.effortList.remove(self.effort2)
        self.assertResult(0, 0)
        
    def testCreateWhenEffortListIsFilled(self):
        self.effortList.append(self.effort1)
        singleTaskEffortList = effort.SingleTaskEffortList(self.task1, self.effortList)
        self.assertResult(1, 1)
        
    def testChildrensEffortIsIncludedToo(self):
        self.task1.addChild(self.task2)
        self.effortList.extend([self.effort1, self.effort2])
        self.assertResult(2, 1)
        
    def testChildrensEffortIsIncludedTooEvenWhenParentHasNoEffort(self):
        self.task1.addChild(self.task2)
        self.effortList.append(self.effort2)
        self.assertResult(1, 1)