import test
import domain.task as task
import domain.effort as effort
import domain.date as date


class CompositeEffortTest(test.TestCase):
    def setUp(self):
        self.task = task.Task(subject='ABC')
        self.datetime = date.DateTime(2004,1,1)
        self.compositeEffort = effort.CompositeEffort(self.task, self.datetime, self.datetime.endOfDay())
        self.effort = effort.Effort(self.task, self.datetime, self.datetime + date.TimeDelta(days=1))
                
    def testEmptyCompositeEffort(self):
        self.assertEqual(date.TimeDelta(), self.compositeEffort.duration())
        
    def testAppendEffort(self):
        self.compositeEffort.append(self.effort)
        self.assertEqual(self.effort.duration(), self.compositeEffort.duration())
                
    def testGetStart(self):
        self.assertEqual(self.datetime, self.compositeEffort.getStart())
        
    def testGetStop(self):
        self.assertEqual(self.datetime.endOfDay(), self.compositeEffort.getStop())
        
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
        composite2 = effort.CompositeEffort(self.task, date.DateTime(2004,2,1), date.DateTime(2004,2,1).endOfDay(), [effort2])
        self.failUnless(self.compositeEffort > composite2)
        self.failUnless(composite2 < self.compositeEffort)
        
    def testCompare_EqualStartDifferentTasks(self):
        self.compositeEffort.append(self.effort)
        task2 = task.Task(subject='XYZ')
        effort2 = effort.Effort(task2, date.DateTime(2004,1,1), date.DateTime(2004,1,2))
        composite2 = effort.CompositeEffort(task2, date.DateTime(2004,1,1), date.DateTime(2004,1,1).endOfDay(), [effort2])
        self.failUnless(self.compositeEffort < composite2)
        
    def testDuration(self):
        self.compositeEffort.append(self.effort)
        child = task.Task()
        self.task.addChild(child)
        childEffort = effort.Effort(child, date.DateTime(2004,3,1), date.DateTime(2004,3,2))
        child.addEffort(childEffort)
        self.compositeEffort.append(childEffort)
        self.assertEqual(self.effort.duration(), self.compositeEffort.duration())
        
    def testRevenue_WithoutFee(self):
        self.task.addEffort(self.effort)
        self.compositeEffort.append(self.effort)
        self.assertEqual(0, self.compositeEffort.revenue())
        
    def testRevenue_HourlyFee(self):
        self.task.setHourlyFee(100)
        self.task.addEffort(self.effort)
        self.compositeEffort.append(self.effort)
        self.assertEqual(self.effort.duration().hours()*100, self.compositeEffort.revenue())
        
    def testRevenue_FixedFee_OneEffort(self):
        self.task.setFixedFee(1000)
        self.task.addEffort(self.effort)
        self.compositeEffort.append(self.effort)
        self.assertEqual(1000, self.compositeEffort.revenue())
        
    def testRevenue_FixedFee_TwoEfforts(self):
        self.task.setFixedFee(1000)
        self.task.addEffort(self.effort)
        self.compositeEffort.append(self.effort)
        effort2 = effort.Effort(self.task, date.DateTime(2005,1,1,10,0),
                                date.DateTime(2005,1,1,22,0))
        self.task.addEffort(effort2)
        self.assertEqual(2./3*1000., self.compositeEffort.revenue())
        
    def testRevenue_Recursive(self):
        self.task.setHourlyFee(100)
        child = task.Task()
        self.task.addChild(child)
        child.setHourlyFee(200)
        self.task.addEffort(self.effort)
        childEffort = effort.Effort(child, self.datetime, self.datetime + date.TimeDelta(hours=1))
        child.addEffort(childEffort)
        self.compositeEffort.extend([self.effort, childEffort])
        self.assertEqual(2400 + 200, self.compositeEffort.revenue(recursive=True))
