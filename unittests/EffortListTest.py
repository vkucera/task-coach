import test, effort, task, date

__coverage__ = [effort.EffortList, effort.SingleTaskEffortList]

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
        
    def testAppend(self):
        self.task.addEffort(self.effort)
        self.assertEqual(self.effort, self.effortList[0])
        
    def testRemove(self):
        self.task.addEffort(self.effort)
        self.task.removeEffort(self.effort)
        self.assertEqual(0, len(self.effortList))
        

class SingleTaskEffortListTest(test.TestCase):
    def setUp(self):
        self.notifications = 0
        self.task = task.Task()
        self.child = task.Task()
        self.effort = effort.Effort(self.task, date.DateTime.now())
        self.childEffort = effort.Effort(self.child, date.DateTime.now())
        self.singleTaskEffortList = effort.SingleTaskEffortList(self.task)
        self.singleTaskEffortList.registerObserver(self.notify, self.notify, self.notify)
        
    def notify(self, *args):
        self.notifications += 1
        
    def assertResult(self, expectedLength, expectedNotifications):
        self.assertEqual(expectedLength, len(self.singleTaskEffortList))
        self.assertEqual(expectedNotifications, self.notifications)
    
    def addChild(self):
        self.task.addChild(self.child)
        self.child.addEffort(self.childEffort)
        
    def testCreate(self):
        self.assertResult(0, 0)
        
    def testAddEffort(self):
        self.task.addEffort(self.effort)
        self.assertResult(1, 1)
                
    def testChangeEffort(self):
        self.task.addEffort(self.effort)
        self.effort.setStop(date.DateTime.now())
        self.assertResult(1, 2)
        
    def testRemoveEffort(self):
        self.task.addEffort(self.effort)
        self.task.removeEffort(self.effort)
        self.assertResult(0, 2)
        
    def testCreateWhenEffortListIsFilled(self):
        self.addChild()
        self.task.addEffort(self.effort)
        self.singleTaskEffortList = effort.SingleTaskEffortList(self.task)
        self.assertResult(2, 2)
        
    def testChildrensEffortIsIncludedToo(self):
        self.addChild()
        self.task.addEffort(self.effort)
        self.assertResult(2, 2)
        
    def testChildrensEffortIsIncludedTooEvenWhenParentHasNoEffort(self):
        self.addChild()
        self.assertResult(1, 1)