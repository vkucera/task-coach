import test, patterns
import domain.task as task
import domain.effort as effort
import domain.date as date


class CompositeEffortTest(test.TestCase):
    def setUp(self):
        self.task = task.Task(subject='task')
        self.child = task.Task(subject='child')
        self.task.addChild(self.child)
        self.effort1 = effort.Effort(self.task, 
            date.DateTime(2004,1,1,11,0,0), date.DateTime(2004,1,1,12,0,0))
        self.effort2 = effort.Effort(self.task, 
            date.DateTime(2004,1,1,13,0,0), date.DateTime(2004,1,1,14,0,0))
        self.effort3 = effort.Effort(self.task, 
            date.DateTime(2004,1,11,13,0,0), date.DateTime(2004,1,11,14,0,0))
        self.trackedEffort = effort.Effort(self.task, 
            date.DateTime(2004,1,1,9,0,0))
        self.composite = effort.CompositeEffort(self.task,
            date.DateTime(2004,1,1,0,0,0), date.DateTime(2004,1,1,23,59,59))
        self.events = []
    
    def onEvent(self, event):
        self.events.append(event)

    def testInitialLength(self):
        self.assertEqual(0, len(self.composite))

    def testInitialDuration(self):
        self.assertEqual(date.TimeDelta(), self.composite.duration())

    def testAddEffortToTask(self):
        self.task.addEffort(self.effort1)
        self.failUnless(self.effort1 in self.composite)

    def testDurationForSingleEffort(self):
        self.task.addEffort(self.effort1)
        self.assertEqual(self.effort1.duration(), self.composite.duration())

    def testAddEffortOutsidePeriodToTask(self):
        effortOutsidePeriod = effort.Effort(self.task, 
            date.DateTime(2004,1,11,13,0,0), date.DateTime(2004,1,11,14,0,0))
        self.task.addEffort(effortOutsidePeriod)
        self.failIf(effortOutsidePeriod in self.composite)

    def testAddEffortWithStartTimeEqualToStartOfPeriodToTask(self):
        effortSameStartTime = effort.Effort(self.task, 
            date.DateTime(2004,1,1,0,0,0), date.DateTime(2004,1,1,14,0,0))
        self.task.addEffort(effortSameStartTime)
        self.failUnless(effortSameStartTime in self.composite)

    def testAddEffortWithStartTimeEqualToEndOfPeriodToTask(self):
        effortSameStopTime = effort.Effort(self.task, 
            date.DateTime(2004,1,1,23,59,59), date.DateTime(2004,1,2,1,0,0))
        self.task.addEffort(effortSameStopTime)
        self.failUnless(effortSameStopTime in self.composite)

    def testAddTrackedEffortToTask(self):
        self.composite.registerObserver(self.onEvent, 'effort.track.start')
        self.task.addEffort(self.trackedEffort)
        self.assertEqual(patterns.Event(self.composite, 'effort.track.start'), 
            self.events[0])

    def testAddSecondTrackedEffortToTask(self):
        self.task.addEffort(self.trackedEffort)
        self.composite.registerObserver(self.onEvent, 'effort.track.start')
        self.task.addEffort(self.trackedEffort)
        self.failIf(self.events)

    def testAddEffortNotification(self):
        self.composite.registerObserver(self.onEvent, 'effort.duration')
        self.task.addEffort(self.effort1)
        self.assertEqual(patterns.Event(self.composite, 'effort.duration', 
            self.composite.duration()), self.events[0])

    def testRemoveEffortFromTask(self):
        self.task.addEffort(self.effort1)
        self.task.removeEffort(self.effort1)
        self.failIf(self.effort1 in self.composite)

    def testRemoveEffortNotification(self):
        self.task.addEffort(self.effort1)
        self.composite.registerObserver(self.onEvent, 'effort.duration')
        self.task.removeEffort(self.effort1)
        self.assertEqual(patterns.Event(self.composite, 'effort.duration', 
            self.composite.duration()), self.events[0])

    def testRemoveTrackedEffortFromTask(self):
        self.task.addEffort(self.trackedEffort)
        self.composite.registerObserver(self.onEvent, 'effort.track.stop')
        self.task.removeEffort(self.trackedEffort)
        self.assertEqual(patterns.Event(self.composite, 'effort.track.stop'),
            self.events[0])

    def testRemoveFirstFromTwoTrackedEffortsFromTask(self):
        self.task.addEffort(self.trackedEffort)
        self.task.addEffort(self.trackedEffort.copy())
        self.composite.registerObserver(self.onEvent, 'effort.track.stop')
        self.task.removeEffort(self.trackedEffort)
        self.failIf(self.events)

    def testDuration(self):
        self.task.addEffort(self.effort1)
        self.assertEqual(self.effort1.duration(), self.composite.duration())

    def testDurationTwoEfforts(self):
        self.task.addEffort(self.effort1)
        self.task.addEffort(self.effort2)
        self.assertEqual(self.effort1.duration() + self.effort2.duration(), 
            self.composite.duration())

    def testRevenue(self):
        self.task.setHourlyFee(100)
        self.task.addEffort(self.effort1)
        self.assertEqual(100, self.composite.revenue())

    def testRevenueTwoEfforts(self):
        self.task.setHourlyFee(100)
        self.task.addEffort(self.effort1)
        self.task.addEffort(self.effort2)
        self.assertEqual(200, self.composite.revenue())

    def testIsBeingTracked(self):
        self.task.addEffort(self.effort1)
        self.effort1.setStop(date.Date())
        self.failUnless(self.composite.isBeingTracked())

    def testNotificationForStartTracking(self):
        self.composite.registerObserver(self.onEvent, 'effort.track.start')
        self.task.addEffort(self.effort1)
        self.effort1.setStop(date.Date())
        self.assertEqual('effort.track.start', self.events[0].type())

    def testNotificationForStopTracking(self):
        self.task.addEffort(self.effort1)
        self.effort1.setStop(date.Date())
        self.composite.registerObserver(self.onEvent, 'effort.track.stop')
        self.effort1.setStop()
        self.assertEqual(patterns.Event(self.composite, 'effort.track.stop'), 
            self.events[0])

    def testChangeStartTimeOfEffort_KeepWithinPeriod(self):
        self.task.addEffort(self.effort1)
        self.effort1.setStart(self.effort1.getStart() + date.TimeDelta(hours=1))
        self.failUnless(self.effort1 in self.composite)

    def testChangeStartTimeOfEffort_KeepWithinPeriod_Notification(self):
        self.task.addEffort(self.effort1)
        self.composite.registerObserver(self.onEvent, 'effort.duration')
        self.effort1.setStart(self.effort1.getStart() + date.TimeDelta(hours=1))
        self.assertEqual(patterns.Event(self.composite, 'effort.duration', 
            self.composite.duration()), self.events[0])

    def testChangeStartTimeOfEffort_MoveOutsidePeriode(self):
        self.task.addEffort(self.effort1)
        self.effort1.setStart(self.effort1.getStart() + date.TimeDelta(days=2))
        self.failIf(self.effort1 in self.composite)

    def testChangeStopTimeOfEffort_KeepWithinPeriod(self):
        self.task.addEffort(self.effort1)
        self.effort1.setStop(self.effort1.getStop() + date.TimeDelta(hours=1))
        self.failUnless(self.effort1 in self.composite)

    def testChangeStoptimeOfEffort_MoveOutsidePeriod(self):
        self.task.addEffort(self.effort1)
        self.effort1.setStop(self.effort1.getStop() + date.TimeDelta(days=2))
        self.failUnless(self.effort1 in self.composite)

    def testChangeStartTimeOfEffort_Notification(self):
        self.task.addEffort(self.effort1)
        self.composite.registerObserver(self.onEvent, 'effort.duration')
        self.effort1.setStop(self.effort1.getStop() + date.TimeDelta(hours=1))
        self.assertEqual(patterns.Event(self.composite, 'effort.duration', 
            self.composite.duration()), self.events[0])

    def testChangeStartTimeOfEffort_MoveInsidePeriod(self):
        self.task.addEffort(self.effort3)
        self.effort3.setStart(self.composite.getStart())
        self.failUnless(self.effort3 in self.composite)

    def testEmptyNotification(self):
        self.composite.registerObserver(self.onEvent, 'list.empty')
        self.task.addEffort(self.effort1)
        self.task.removeEffort(self.effort1)
        self.assertEqual(patterns.Event(self.composite, 'list.empty'),
            self.events[0])

    def testCompare_Smaller(self):
        composite2 = effort.CompositeEffort(self.task,
            date.DateTime(2004,2,1,0,0,0), date.DateTime(2004,2,1,23,59,59))
        self.failUnless(self.composite < composite2)

    def testCompare_Bigger(self):
        composite2 = effort.CompositeEffort(self.task,
            date.DateTime(2004,2,1,0,0,0), date.DateTime(2004,2,1,23,59,59))
        self.failUnless(composite2 > self.composite)

    def testCompare_EqualStartDifferentTasks(self):
        composite2 = effort.CompositeEffort(self.child,
            self.composite.getStart(), self.composite.getStop())
        self.failUnless(composite2 < self.composite)
        

class CompositeEffortWithSubTasksTest(test.TestCase):
    def setUp(self):
        self.task = task.Task(subject='task')
        self.child = task.Task(subject='child')
        self.child2 = task.Task(subject='child2')
        self.task.addChild(self.child)
        self.taskEffort = effort.Effort(self.task, 
            date.DateTime(2004,1,1,11,0,0), date.DateTime(2004,1,1,12,0,0))
        self.childEffort = effort.Effort(self.child, 
            date.DateTime(2004,1,1,11,0,0), date.DateTime(2004,1,1,12,0,0))
        self.child2Effort = effort.Effort(self.child2, 
            date.DateTime(2004,1,1,11,0,0), date.DateTime(2004,1,1,12,0,0))
        self.trackedEffort = effort.Effort(self.child, 
            date.DateTime(2004,1,1,9,0,0))
        self.composite = effort.CompositeEffort(self.task,
            date.DateTime(2004,1,1,0,0,0), date.DateTime(2004,1,1,23,59,59))
        self.events = []

    def onEvent(self, event):
        self.events.append(event)

    def testAddEffortToChildTask(self):
        self.child.addEffort(self.childEffort)
        self.failUnless(self.childEffort in self.composite)

    def testAddEffortToChildTaskNotification(self):
        self.composite.registerObserver(self.onEvent, 'effort.duration')
        self.child.addEffort(self.childEffort)
        self.assertEqual(patterns.Event(self.composite, 'effort.duration', 
            self.composite.duration()), self.events[0])

    def testAddTrackedEffortToChildTask(self):
        self.composite.registerObserver(self.onEvent, 'effort.track.start')
        self.child.addEffort(self.trackedEffort)
        self.assertEqual(patterns.Event(self.composite, 'effort.track.start'), 
            self.events[0])

    def testRemoveEffortFromChildTask(self):
        self.child.addEffort(self.childEffort)
        self.child.removeEffort(self.childEffort)
        self.failIf(self.childEffort in self.composite)

    def testRemoveEffortFromChildNotification(self):
        self.child.addEffort(self.childEffort)
        self.composite.registerObserver(self.onEvent, 'effort.duration')
        self.child.removeEffort(self.childEffort)
        self.assertEqual(patterns.Event(self.composite, 'effort.duration', 
            self.composite.duration()), self.events[0])

    def testRemoveTrackedEffortFromChildTask(self):
        self.child.addEffort(self.trackedEffort)
        self.composite.registerObserver(self.onEvent, 'effort.track.stop')
        self.child.removeEffort(self.trackedEffort)
        self.assertEqual(patterns.Event(self.composite, 'effort.track.stop'),
            self.events[0])

    def testDuration(self):
        self.child.addEffort(self.childEffort)
        self.assertEqual(date.TimeDelta(), self.composite.duration())

    def testRecursiveDuration(self):
        self.child.addEffort(self.childEffort)
        self.assertEqual(self.childEffort.duration(), 
            self.composite.duration(recursive=True))

    def testDurationWithTaskAndChildEffort(self):
        self.task.addEffort(self.taskEffort)
        self.child.addEffort(self.childEffort)
        self.assertEqual(self.taskEffort.duration() + \
            self.childEffort.duration(), 
            self.composite.duration(recursive=True))

    def testAddEffortToNewChild(self):
        self.task.addChild(self.child2)
        self.child2.addEffort(self.child2Effort)
        self.assertEqual(self.child2Effort.duration(), 
            self.composite.duration(recursive=True))

    def testAddChildWithEffort(self):
        self.child2.addEffort(self.child2Effort)
        self.task.addChild(self.child2)
        self.assertEqual(self.child2Effort.duration(), 
            self.composite.duration(recursive=True))

    def testAddEffortToGrandChild(self):
        self.task.addChild(self.child2)
        grandChild = task.Task(subject='grandchild')
        self.child2.addChild(grandChild)
        grandChildEffort = effort.Effort(grandChild, self.composite.getStart())
        grandChild.addEffort(grandChildEffort)
        self.failUnless(grandChildEffort in self.composite)

    def testAddGrandChildWithEffort(self):
        self.task.addChild(self.child2)
        grandChild = task.Task(subject='grandchild')
        grandChildEffort = effort.Effort(grandChild, self.composite.getStart())
        grandChild.addEffort(grandChildEffort)
        self.child2.addChild(grandChild)
        self.failUnless(grandChildEffort in self.composite)

    def testRemoveEffortFromAddedChild(self):
        self.task.addChild(self.child2)
        self.child2.addEffort(self.child2Effort)
        self.child2.removeEffort(self.child2Effort)
        self.failIf(self.child2Effort in self.composite)

    def testRemoveChildWithEffort(self):
        self.child.addEffort(self.childEffort)
        self.task.removeChild(self.child)
        self.failIf(self.childEffort in self.composite)

    def testChangeStartTimeOfChildEffort_MoveInsidePeriod(self):
        childEffort = effort.Effort(self.child)
        self.child.addEffort(childEffort)
        childEffort.setStart(self.composite.getStart())
        self.failUnless(childEffort in self.composite)


class CompositeEffortWithSubTasksRevenueTest(test.TestCase):
    def setUp(self):
        self.task = task.Task(subject='task')
        self.child = task.Task(subject='child')
        self.task.addChild(self.child)
        self.taskEffort = effort.Effort(self.task, 
            date.DateTime(2004,1,1,11,0,0), date.DateTime(2004,1,1,12,0,0))
        self.childEffort = effort.Effort(self.child, 
            date.DateTime(2004,1,1,11,0,0), date.DateTime(2004,1,1,12,0,0))
        self.composite = effort.CompositeEffort(self.task,
            date.DateTime(2004,1,1,0,0,0), date.DateTime(2004,1,1,23,59,59))
        self.task.addEffort(self.taskEffort)
        self.child.addEffort(self.childEffort)
 
    def testRevenueWhenParentHasHourlyFee(self):
        self.task.setHourlyFee(100)
        self.assertEqual(self.taskEffort.duration().hours()*100,
            self.composite.revenue())

    def testRecursiveRevenueWhenParentHasHourlyFee(self):
        self.task.setHourlyFee(100)
        self.assertEqual(self.taskEffort.duration().hours()*100,
            self.composite.revenue(recursive=True))

    def testRevenueWhenChildHasHourlyFee(self):
        self.child.setHourlyFee(100)
        self.assertEqual(0, self.composite.revenue())

    def testRecursiveRevenueWhenChildHasHourlyFee(self):
        self.child.setHourlyFee(100)
        self.assertEqual(self.childEffort.duration().hours()*100, 
            self.composite.revenue(recursive=True))

    def testRevenueWhenChildAndParentHaveHourlyFees(self):
        self.child.setHourlyFee(100)
        self.task.setHourlyFee(200)
        self.assertEqual(self.taskEffort.duration().hours()*200, 
            self.composite.revenue())

    def testRecursiveRevenueWhenChildAndParentHaveHourlyFees(self):
        self.child.setHourlyFee(100)
        self.task.setHourlyFee(200)
        self.assertEqual(self.taskEffort.duration().hours()*200 + \
            self.childEffort.duration().hours()*100, 
            self.composite.revenue(recursive=True))

    def testRevenueWhenParentHasFixedFee(self):
        self.task.setFixedFee(1000)
        self.assertEqual(1000, self.composite.revenue())

    def testRecursiveRevenueWhenParentHasFixedFee(self):
        self.task.setFixedFee(1000)
        self.assertEqual(1000, self.composite.revenue(recursive=True))

    def testRevenueWhenChildHasFixedFee(self):
        self.child.setFixedFee(1000)
        self.assertEqual(0, self.composite.revenue())

    def testRecursiveRevenueWhenChildHasFixedFee(self):
        self.child.setFixedFee(1000)
        self.assertEqual(1000, self.composite.revenue(recursive=True))

    def testRevenueWhenParentHasFixedFeeAndMultipleEfforts(self):
        self.task.setFixedFee(1000)
        self.task.addEffort(effort.Effort(self.task, 
            date.DateTime(2005,12,12,10,0,0), date.DateTime(2005,12,12,12,0,0)))
        self.assertEqual(1./3*1000, self.composite.revenue())

    def testRevenueWhenChildHasFixedFeeAndMultipleEfforts(self):
        self.child.setFixedFee(1000)
        self.child.addEffort(effort.Effort(self.child, 
            date.DateTime(2005,12,12,10,0,0), date.DateTime(2005,12,12,12,0,0)))
        self.assertEqual(0, self.composite.revenue())

    def testRecursiveRevenueWhenChildHasFixedFeeAndMultipleEfforts(self):
        self.child.setFixedFee(1000)
        self.child.addEffort(effort.Effort(self.child, 
            date.DateTime(2005,12,12,10,0,0), date.DateTime(2005,12,12,12,0,0)))
        self.assertEqual(1./3*1000, self.composite.revenue(recursive=True))

    def testRevenueWithMixture(self):
        self.child.setFixedFee(100)
        self.task.setHourlyFee(1000)
        self.assertEqual(1100, self.composite.revenue(recursive=True))
