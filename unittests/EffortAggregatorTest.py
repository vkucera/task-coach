import test, effort, task, date

class EffortAggregatorTest(test.TestCase):
    def setUp(self):
        self.taskList = task.TaskList()
        self.effortList = effort.EffortList(self.taskList)
        self.effortPerDay = effort.EffortPerDay(self.effortList)
        self.task = task.Task()
        self.effort1a = effort.Effort(self.task, date.DateTime(2004,1,1,11,0,0), date.DateTime(2004,1,1,12,0,0))
        self.effort1b = effort.Effort(self.task, date.DateTime(2004,1,1,13,0,0), date.DateTime(2004,1,1,14,0,0))
        self.effort2 = effort.Effort(self.task, date.DateTime(2004,1,2,13,0,0), date.DateTime(2004,1,2,14,0,0))
        
    def testEmptyTaskList(self):
        self.assertEqual(0, len(self.effortPerDay))
        
    def testOneTaskWithoutEffort(self):
        self.taskList.append(self.task)
        self.assertEqual(0, len(self.effortPerDay))
        
    def testOneTaskWithOneEffort(self):
        self.taskList.append(self.task)
        self.task.addEffort(effort.Effort(self.task))
        self.assertEqual(1, len(self.effortPerDay))
        
    def testOneTaskWithTwoEffortsOneSameDay(self):
        self.taskList.append(self.task)
        self.task.addEffort(self.effort1a)
        self.task.addEffort(self.effort1b)
        self.assertEqual(1, len(self.effortPerDay))
        
    def testOneTaskWithTwoEffortsOneDifferentDays(self):
        self.taskList.append(self.task)
        self.task.addEffort(self.effort1a)
        self.task.addEffort(self.effort2)
        self.assertEqual(2, len(self.effortPerDay))
