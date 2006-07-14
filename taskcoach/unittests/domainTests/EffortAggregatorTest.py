import test
import domain.task as task
import domain.effort as effort
import domain.date as date

class EffortAggregatorTestCase(test.TestCase):
    def setUp(self):
        self.taskList = task.TaskList()
        self.effortPerPeriod = self.createEffortPerPeriod()
        self.effortPerPeriod.registerObserver(self.onEvent, 'list.add',
            'list.remove')
        self.task1 = task.Task(subject='task 1')
        self.task2 = task.Task(subject='task 2')
        self.task3 = task.Task(subject='child')
        self.task1.addChild(self.task3)
        self.effort1period1a = effort.Effort(self.task1, 
            date.DateTime(2004,1,1,11,0,0), date.DateTime(2004,1,1,12,0,0))
        self.effort2period1a = effort.Effort(self.task2, 
            date.DateTime(2004,1,1,11,0,0), date.DateTime(2004,1,1,12,0,0))
        self.effort1period1b = effort.Effort(self.task1, 
            date.DateTime(2004,1,1,13,0,0), date.DateTime(2004,1,1,14,0,0))
        self.effort2period1b = effort.Effort(self.task2, 
            date.DateTime(2004,1,1,13,0,0), date.DateTime(2004,1,1,14,0,0))
        self.effort1period2 = effort.Effort(self.task1, 
            date.DateTime(2004,2,2,13,0,0), date.DateTime(2004,2,2,14,0,0))
        self.effort1period3 = effort.Effort(self.task1,
            date.DateTime(2004,1,1,10,0,0), date.DateTime(2005,1,1,10,0,0))
        self.effort3period1a = effort.Effort(self.task3, 
            date.DateTime(2004,1,1,14,0,0), date.DateTime(2004,1,1,15,0,0))
        self.events = []

    def onEvent(self, event):
        self.events.append(event)

        
class CommonTests(object):
    def testEmptyTaskList(self):
        self.assertEqual(0, len(self.effortPerPeriod))
        
    def testOneTaskWithoutEffort(self):
        self.taskList.append(self.task1)
        self.assertEqual(0, len(self.effortPerPeriod))
        
    def testOneTaskWithOneEffort(self):
        self.taskList.append(self.task1)
        self.task1.addEffort(effort.Effort(self.task1))
        self.assertEqual(1, len(self.effortPerPeriod))
        
    def testOneTaskWithTwoEffortsOneSameDay(self):
        self.taskList.append(self.task1)
        self.task1.addEffort(self.effort1period1a)
        self.task1.addEffort(self.effort1period1b)
        self.assertEqual(1, len(self.effortPerPeriod))
        
    def testOneTaskWithTwoEffortsInDifferentPeriods(self):
        self.taskList.append(self.task1)
        self.task1.addEffort(self.effort1period1a)
        self.task1.addEffort(self.effort1period2)
        self.assertEqual(2, len(self.effortPerPeriod))

    def testTwoTasksWithEffortOnTheSameDay(self):
        self.taskList.extend([self.task1, self.task2])
        self.task1.addEffort(self.effort1period1a)
        self.task2.addEffort(self.effort2period1a)
        self.assertEqual(2, len(self.effortPerPeriod))

    def testAddEffortToChild(self):
        self.taskList.extend([self.task1, self.task2])
        self.task1.addChild(self.task2)
        self.task2.addEffort(self.effort2period1a)
        self.assertEqual(2, len(self.effortPerPeriod))

    def testRemoveChildWithEffortFromParent(self):
        self.taskList.extend([self.task1, self.task2])
        self.task1.addChild(self.task2)
        self.task2.addEffort(self.effort2period1a)
        self.task2.setParent(None)
        self.task1.removeChild(self.task2)
        self.assertEqual(1, len(self.effortPerPeriod))

    def testAddChildWithEffort(self):
        self.taskList.extend([self.task1, self.task2])
        self.task2.addEffort(self.effort2period1a)
        self.task1.addChild(self.task2)
        self.assertEqual(2, len(self.effortPerPeriod))

    def testRemoveEffort(self):
        self.taskList.append(self.task1)
        self.task1.addEffort(self.effort1period1a)
        self.task1.removeEffort(self.effort1period1a)
        self.assertEqual(0, len(self.effortPerPeriod))

    def testRemoveOneOfTwoEfforts(self):
        self.taskList.append(self.task1)
        self.task1.addEffort(self.effort1period1a)
        self.task1.addEffort(self.effort1period1b)
        self.task1.removeEffort(self.effort1period1a)
        self.assertEqual(1, len(self.effortPerPeriod))

    def testRemoveOneOfTwoEffortsOfDifferentTasks(self):
        self.taskList.extend([self.task1, self.task2])
        self.task1.addEffort(self.effort1period1a)
        self.task2.addEffort(self.effort2period1a)
        self.task1.removeEffort(self.effort1period1a)
        self.assertEqual(1, len(self.effortPerPeriod))

    def testRemoveTwoOfTwoEfforts(self):
        self.taskList.append(self.task1)
        self.task1.addEffort(self.effort1period1a)
        self.task1.addEffort(self.effort1period1b)
        self.task1.removeEffort(self.effort1period1a)
        self.task1.removeEffort(self.effort1period1b)
        self.assertEqual(0, len(self.effortPerPeriod))

    def testRemoveEffortFromChild(self):
        self.taskList.extend([self.task1, self.task2])
        self.task2.addEffort(self.effort2period1a)
        self.task1.addChild(self.task2)
        self.task2.removeEffort(self.effort2period1a)
        self.assertEqual(0, len(self.effortPerPeriod))

    def testRemoveTasks(self):
        self.taskList.extend([self.task1, self.task3])
        self.task3.addEffort(self.effort3period1a)
        self.taskList.removeItems([self.task1, self.task3])
        self.assertEqual(0, len(self.effortPerPeriod))

    def testRemoveAllTasks(self):
        self.taskList.extend([self.task1, self.task2, self.task3])
        self.task3.addEffort(self.effort3period1a)
        self.taskList.removeItems([self.task1, self.task2, self.task3])
        self.assertEqual(0, len(self.effortPerPeriod))
 
    def testRemoveChildTask(self):
        self.taskList.extend([self.task1])
        self.task3.addEffort(self.effort3period1a)
        self.taskList.removeItems([self.task3])
        self.assertEqual(0, len(self.effortPerPeriod))
 
    def testChangeStart(self):
        self.taskList.append(self.task1)
        self.task1.addEffort(self.effort1period1a)
        self.effort1period1a.setStart(date.DateTime.now())
        self.assertEqual(self.startOfPeriod(),
            self.effortPerPeriod[0].getStart())

    def testChangeStartOfOneOfTwoEfforts(self):
        self.taskList.append(self.task1)
        self.task1.addEffort(self.effort1period1a)
        self.task1.addEffort(self.effort1period1b)
        self.effort1period1a.setStart(date.DateTime.now())
        self.assertEqual(2, len(self.effortPerPeriod))

    def testChangeStopDoesNotAffectPeriod(self):
        self.taskList.append(self.task1)
        self.task1.addEffort(self.effort1period1a)
        start = self.effortPerPeriod[0].getStart()
        self.effort1period1a.setStop(date.DateTime.now())
        self.assertEqual(start, self.effortPerPeriod[0].getStart())

    def testChangeStartOfOneOfTwoEffortsToOneYearLater(self):
        self.taskList.append(self.task1)
        self.task1.addEffort(self.effort1period1a)
        self.task1.addEffort(self.effort1period1b)
        self.effort1period1a.setStart(date.DateTime(2005,1,1,11,0,0))
        self.assertEqual(2, len(self.effortPerPeriod))

    def testNotification_Add(self):
        self.taskList.append(self.task1)
        self.task1.addEffort(self.effort1period1a)
        self.assertEqual(1, len(self.events))
        self.assertEqual(self.effortPerPeriod[0], self.events[0].value())

    def testNotification_Remove(self):
        self.taskList.append(self.task1)
        self.task1.addEffort(self.effort1period1a)
        self.task1.removeEffort(self.effort1period1a)
        self.assertEqual(2, len(self.events))

    def testCreateWithInitialEffort(self):
        self.taskList.append(self.task1)
        self.task1.addEffort(self.effort1period1a)
        aggregator = self.createEffortPerPeriod()
        self.assertEqual(1, len(aggregator))

    def testLongEffortIsStillOneCompositeEffort(self):
        self.taskList.append(self.task1)
        self.task1.addEffort(self.effort1period3)
        self.assertEqual(1, len(self.effortPerPeriod))


class EffortPerDayTest(EffortAggregatorTestCase, CommonTests):
    def createEffortPerPeriod(self):
        return effort.EffortPerDay(self.taskList)

    def startOfPeriod(self):
        return date.DateTime.now().startOfDay()


class EffortPerWeekTest(EffortAggregatorTestCase, CommonTests):
    def createEffortPerPeriod(self):
        return effort.EffortPerWeek(self.taskList)

    def startOfPeriod(self):
        return date.DateTime.now().startOfWeek()


class EffortPerMonthTest(EffortAggregatorTestCase, CommonTests):
    def createEffortPerPeriod(self):
        return effort.EffortPerMonth(self.taskList)

    def startOfPeriod(self):
        return date.DateTime.now().startOfMonth()
