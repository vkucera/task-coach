import test, effort, date, task

class CompositeEffortTest(test.TestCase):
    def setUp(self):
        self.compositeEffort = effort.CompositeEffort()
        self.task = task.Task(subject='ABC')
        self.effort = effort.Effort(self.task, date.DateTime(2004,1,1), date.DateTime(2004,1,2))
                
    def testEmptyCompositeEffort(self):
        self.assertEqual(date.TimeDelta(), self.compositeEffort.duration())
        
    def testAppendEffort(self):
        self.compositeEffort.append(self.effort)
        self.assertEqual(self.effort.duration(), self.compositeEffort.duration())
                
    def testGetStart(self):
        self.compositeEffort.append(self.effort)
        self.assertEqual(self.effort.getStart(), self.compositeEffort.getStart())
        
    def testGetStart_EmptyCompositeEffort(self):
        self.assertEqual(None, self.compositeEffort.getStart())
        
    def testGetStop(self):
        self.compositeEffort.append(self.effort)
        self.assertEqual(self.effort.getStop(), self.compositeEffort.getStop())
        
    def testGetStop_EmptyCompositeEffort(self):
        self.assertEqual(None, self.compositeEffort.getStop())
        
    def testGetTask_EmptyCompositeEffort(self):
        self.assertEqual(None, self.compositeEffort.task())
        
    def testGetTask(self):
        self.compositeEffort.append(self.effort)
        self.assertEqual(self.effort.task(), self.compositeEffort.task())
        
    def testGetTask_MultipleEffortsForOneTask(self):
        self.compositeEffort.append(self.effort)
        self.compositeEffort.append(effort.Effort(self.task))
        self.assertEqual(self.effort.task(), self.compositeEffort.task())
        
    def testCompare_Equal(self):
        self.compositeEffort.append(self.effort)
        self.assertEqual(self.compositeEffort, self.compositeEffort)
        
    def testCompare_SmallerStart(self):
        self.compositeEffort.append(self.effort)
        effort2 = effort.Effort(self.task, date.DateTime(2004,2,1), date.DateTime(2004,2,2))
        composite2 = effort.CompositeEffort([effort2])
        self.failUnless(self.compositeEffort < composite2)
        self.failUnless(composite2 > self.compositeEffort)
        
    def testCompare_EqualStartDifferentTasks(self):
        self.compositeEffort.append(self.effort)
        task2 = task.Task(subject='XYZ')
        effort2 = effort.Effort(task2, date.DateTime(2004,1,1), date.DateTime(2004,1,2))
        composite2 = effort.CompositeEffort([effort2])
        self.failUnless(self.compositeEffort < composite2)