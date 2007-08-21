import test, patterns
import domain.task as task
import domain.effort as effort
import domain.date as date


class EffortListTest(test.TestCase):
    def setUp(self):
        self.events = []
        self.task = task.Task()
        self.taskList = task.TaskList()
        self.effortList = effort.EffortList(self.taskList)
        self.taskList.append(self.task)
        patterns.Publisher().registerObserver(self.onEvent,
            eventType=self.effortList.addItemEventType())
        patterns.Publisher().registerObserver(self.onEvent,
            eventType=self.effortList.removeItemEventType())
        self.effort = effort.Effort(self.task, date.DateTime(2004, 1, 1), 
            date.DateTime(2004, 1, 2))
        
    def testCreate(self):
        self.assertEqual(0, len(self.effortList))
    
    def onEvent(self, event):
        self.events.append(event)

    def testNotificationAfterAppend(self):
        self.task.addEffort(self.effort)
        self.assertEqual(self.effort, self.events[0].value())
        
    def testAppend(self):
        self.task.addEffort(self.effort)
        self.assertEqual(1, len(self.effortList))
        self.failUnless(self.effort in self.effortList)

    def testNotificationAfterRemove(self):
        self.task.addEffort(self.effort)
        self.task.removeEffort(self.effort)
        self.assertEqual(self.effort, self.events[0].value())
        
    def testRemove(self):
        self.task.addEffort(self.effort)
        self.task.removeEffort(self.effort)
        self.assertEqual(0, len(self.effortList))
    
    def testAppendTaskWithEffort(self):
        newTask = task.Task()
        newTask.addEffort(effort.Effort(newTask))
        self.taskList.append(newTask)
        self.assertEqual(1, len(self.effortList))    

    def testCreateWhenTaskListIsFilled(self):
        self.task.addEffort(self.effort)
        effortList = effort.EffortList(task.TaskList([self.task]))
        self.assertEqual(1, len(effortList))

    def testAddEffortToChild(self):
        child = task.Task(parent=self.task)
        self.taskList.append(child)
        child.addEffort(effort.Effort(child))
        self.assertEqual(1, len(self.effortList))

    def testMaxDateTime(self):
        self.assertEqual(None, self.effortList.maxDateTime())
        
    def testMaxDateTime_OneEffort(self):
        self.task.addEffort(self.effort)
        self.assertEqual(self.effort.getStop(), self.effortList.maxDateTime())

    def testMaxDateTime_OneTrackingEffort(self):
        self.task.addEffort(effort.Effort(self.task))
        self.assertEqual(None, self.effortList.maxDateTime())
        
    def testMaxDateTime_TwoEfforts(self):
        self.task.addEffort(self.effort)
        now = date.DateTime.now()
        self.task.addEffort(effort.Effort(self.task, None, now))
        self.assertEqual(now, self.effortList.maxDateTime())
    
    def testNrTracking(self):
        self.assertEqual(0, self.effortList.nrBeingTracked())
        
    def testOriginalLength(self):
        self.assertEqual(0, self.effortList.originalLength())
        
    def testRemoveItems(self):
        self.task.addEffort(self.effort)
        self.effortList.removeItems([self.effort])
        self.assertEqual(0, len(self.effortList))
        self.assertEqual(0, len(self.task.efforts()))

    def testExtend(self):
        self.effortList.extend([self.effort])
        self.assertEqual(1, len(self.effortList))
        self.failUnless(self.effort in self.effortList)
        self.assertEqual(1, len(self.task.efforts()))
        self.assertEqual(self.effort, self.task.efforts()[0])
