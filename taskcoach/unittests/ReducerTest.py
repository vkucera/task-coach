import test, effort, date, task

__coverage__ = [effort.EffortPerDay, effort.EffortPerWeek, effort.EffortPerMonth]

# FIXME: rename to EffortReducerTest.py

class ReducerTestCase(test.TestCase):
    def setUp(self):
        self.notifications = 0
        self.taskList = task.TaskList()
        self.effortList = effort.EffortList(self.taskList)
        self.task1 = task.Task()
        self.effort1_1 = effort.Effort(self.task1, date.DateTime(2004,1,1,15,0,0), 
            date.DateTime(2004,1,1,16,0,0))
        self.effort1_2 = effort.Effort(self.task1, date.DateTime(2004,1,1,17,0,0), 
            date.DateTime(2004,1,1,18,0,0))
        self.effort1_3 = effort.Effort(self.task1, date.DateTime(2004,2,1,10,0,0),
            date.DateTime(2004,2,1,11,0,0))
        self.effort1_4 = effort.Effort(self.task1, date.DateTime(2004,2,1,23,0,0),
            date.DateTime(2004,2,2,1,0,0))
        self.effort1_5 = effort.Effort(self.task1, date.DateTime(2004,1,2,0,0,0),
            date.DateTime(2004,1,2,1,0,0))
        self.task2 = task.Task()
        self.effort2_1 = effort.Effort(self.task2, date.DateTime(2004,2,1,10,0,0),
            date.DateTime(2004,2,1,11,0,0))
        self.taskList.extend([self.task1, self.task2])
        self.reducer = self.createReducer()
        self.reducer.registerObserver(self.onNotify)
        
    def onNotify(self, notification, *args, **kwargs):
        self.notifications += 1
        self.notification = notification
        
    def assertCompositeEffort(self, compositeEffort, *efforts):
        for effort in efforts:
            self.failUnless(compositeEffort.getStart() <= effort.getStart() <= compositeEffort.getStop())
            self.failUnless(effort in compositeEffort)

class CommonTests:
    def testEmptyEffortList(self):
        self.assertEqual(0, len(self.reducer))

    def testOneEffortForOneTaskOnOneDay(self):
        self.task1.addEffort(self.effort1_1)
        self.assertCompositeEffort(self.reducer[0], self.effort1_1)        

    def testTwoEffortsForOneTaskOnOneDay(self):
        self.task1.addEffort(self.effort1_1)
        self.task1.addEffort(self.effort1_2)
        self.assertCompositeEffort(self.reducer[0], self.effort1_1, self.effort1_2)

    def testTwoEffortsForTwoTasksOnOneDay(self):
        self.task1.addEffort(self.effort1_1)
        self.task2.addEffort(self.effort2_1)
        self.assertCompositeEffort(self.reducer[0], self.effort1_1)
        self.assertCompositeEffort(self.reducer[1], self.effort2_1)

    def testTwoEffortsForOneTaskInTwoDifferentMonths(self):
        self.task1.addEffort(self.effort1_1)
        self.task1.addEffort(self.effort1_3)
        self.assertCompositeEffort(self.reducer[0], self.effort1_1)
        self.assertCompositeEffort(self.reducer[1], self.effort1_3)
        
    def testEffortOfChildBringsInParent(self):
        self.task1.addChild(self.task2)
        self.task2.addEffort(self.effort2_1)
        self.assertCompositeEffort(self.reducer[0], self.effort2_1)
        self.assertCompositeEffort(self.reducer[1], self.effort2_1)

    def testRemoveOneEffortOfOneTask(self):
        self.task1.addEffort(self.effort1_1)
        self.task1.removeEffort(self.effort1_1)
        self.assertEqual(0, len(self.reducer))                            

    def testRemoveOneEffortOfTwoEffortsOfOneTask(self):
        self.task1.addEffort(self.effort1_1)
        self.task1.addEffort(self.effort1_2)
        self.task1.removeEffort(self.effort1_1)
        self.assertEqual(1, len(self.reducer))

    def testRemoveOneEffortsOfTwoEffortsOfTwoTasks(self):
        self.task1.addEffort(self.effort1_1)
        self.task2.addEffort(self.effort2_1)
        self.task1.removeEffort(self.effort1_1)
        self.assertEqual(1, len(self.reducer))

    def testChangeEffort(self):
        self.task1.addEffort(self.effort1_1)
        self.effort1_1.setStop(date.DateTime(2004,1,1,17,0,0))
        self.assertCompositeEffort(self.reducer[0], self.effort1_1)
        self.assertEqual(2, self.notifications)

    def testChangeEffort_ToAnotherYear_SameMonthSameWeekNumber(self):
        self.task1.addEffort(self.effort1_1)
        self.task1.addEffort(self.effort1_2)
        self.effort1_1.setStart(date.DateTime(2000,1,4,15,0,0))
        self.assertEqual(2, len(self.reducer))

    def testNotification_Add(self):
        self.task1.addEffort(self.effort1_1)
        self.assertEqual(1, self.notifications)
        self.assertEqual(self.reducer[0], self.notification.itemsAdded[0])
        
    def testNotification_Remove(self):
        self.task1.addEffort(self.effort1_1)
        self.task1.removeEffort(self.effort1_1)
        self.assertEqual(2, self.notifications)
        
    def testNotification_Change(self):
        self.task1.addEffort(self.effort1_1)
        self.effort1_1.setStart(date.DateTime(2005,1,1,15,0,0))
        self.assertEqual(1, len(self.reducer))
        self.assertEqual(2, self.notifications)

    def testCreateWithInitialEffort(self):
        self.task1.addEffort(self.effort1_1)
        reducer = self.createReducer()
        self.assertEqual(1, len(reducer))
        

class EffortPerDayTest(ReducerTestCase, CommonTests):  
    def createReducer(self):
        return effort.EffortPerDay(self.effortList)
        
    def testOneEffortThatSpansTwoDays(self):
        self.task1.addEffort(self.effort1_4)
        self.assertEqual(1, len(self.reducer)) # FIXME: would be better to split the effort
                 
        
class EffortPerWeekTest(ReducerTestCase, CommonTests):        
    def createReducer(self):
        return effort.EffortPerWeek(self.effortList)

    def testTwoEffortsForOneTaskInOneWeek(self):
        self.assertEqual(self.effort1_1.getStart().weeknumber(),
            self.effort1_5.getStart().weeknumber())
        self.task1.addEffort(self.effort1_1)
        self.task1.addEffort(self.effort1_5)
        self.assertCompositeEffort(self.reducer[0], self.effort1_1, self.effort1_5)
        self.assertEqual(1, len(self.reducer))

class EffortPerMonthTest(ReducerTestCase, CommonTests):
    def createReducer(self):
        return effort.EffortPerMonth(self.effortList)