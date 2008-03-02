'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>

Task Coach is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Task Coach is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import test, patterns
from domain import task, effort, date


class EffortAggregatorTestCase(test.TestCase):
    def setUp(self):
        self.taskList = task.TaskList()
        self.effortPerPeriod = self.createEffortPerPeriod()
        patterns.Publisher().registerObserver(self.onEvent, 
            eventType=self.effortPerPeriod.addItemEventType())
        patterns.Publisher().registerObserver(self.onEvent,
            eventType=self.effortPerPeriod.removeItemEventType())
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
        
    def testAddTaskWithoutEffort(self):
        self.taskList.append(self.task1)
        self.assertEqual(0, len(self.effortPerPeriod))
        
    def testAddTaskWithEffort(self):
        self.task1.addEffort(self.effort1period1a)
        self.taskList.append(self.task1)
        self.assertEqual(1, len(self.effortPerPeriod))

    def testAddEffort(self):
        self.taskList.append(self.task1)
        self.task1.addEffort(effort.Effort(self.task1))
        self.assertEqual(1, len(self.effortPerPeriod))
        
    def testAddTwoEffortsOnSameDay(self):
        self.taskList.append(self.task1)
        self.task1.addEffort(self.effort1period1a)
        self.task1.addEffort(self.effort1period1b)
        self.assertEqual(1, len(self.effortPerPeriod))

    def testAddTaskWithTwoEffortsOnSameDay(self):
        self.task1.addEffort(self.effort1period1a)
        self.task1.addEffort(self.effort1period1b)
        self.taskList.append(self.task1)
        self.assertEqual(1, len(self.effortPerPeriod))
        
    def testAddTwoEffortsInDifferentPeriods(self):
        self.taskList.append(self.task1)
        self.task1.addEffort(self.effort1period1a)
        self.task1.addEffort(self.effort1period2)
        self.assertEqual(2, len(self.effortPerPeriod))

    def testAddTwoEffortsOnTheSameDayToTwoDifferentTasks(self):
        self.taskList.extend([self.task1, self.task2])
        self.task1.addEffort(self.effort1period1a)
        self.task2.addEffort(self.effort2period1a)
        self.assertEqual(2, len(self.effortPerPeriod))

    def testAddEffortToChild(self):
        self.taskList.extend([self.task1, self.task2])
        self.task1.addChild(self.task2)
        self.task2.addEffort(self.effort2period1a)
        self.assertEqual(2, len(self.effortPerPeriod))

    def testAddChildWithEffort(self):
        self.taskList.extend([self.task1, self.task2])
        self.task2.addEffort(self.effort2period1a)
        self.task1.addChild(self.task2)
        self.assertEqual(2, len(self.effortPerPeriod))

    def testAddParentAndChildWithEffortToTaskList(self):
        self.task3.addEffort(self.effort3period1a)
        self.taskList.append(self.task1)
        self.assertEqual(2, len(self.effortPerPeriod))

    def testAddEffortToGrandChild(self):
        self.taskList.extend([self.task1, self.task2])
        self.task3.addChild(self.task2)
        self.task2.addEffort(self.effort2period1a)
        self.assertEqual(3, len(self.effortPerPeriod))

    def testAddGrandChildWithEffort(self):
        self.taskList.extend([self.task1, self.task2])
        self.task2.addEffort(self.effort2period1a)
        self.task3.addChild(self.task2)
        self.assertEqual(3, len(self.effortPerPeriod))

    def testRemoveChildWithEffortFromParent(self):
        self.taskList.extend([self.task1, self.task2])
        self.task1.addChild(self.task2)
        self.task2.addEffort(self.effort2period1a)
        self.task2.setParent(None)
        self.task1.removeChild(self.task2)
        self.assertEqual(1, len(self.effortPerPeriod))

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

    def testRemoveTasksWithOverlappingEffort(self):
        self.taskList.extend([self.task1, self.task3])
        self.task3.addEffort(self.effort3period1a)
        self.task1.addEffort(self.effort1period1a)
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
        self.assertEqual(1, len(self.effortPerPeriod))

    def testChangeStartOfOneOfTwoEfforts(self):
        self.taskList.append(self.task1)
        self.task1.addEffort(self.effort1period1a)
        self.task1.addEffort(self.effort1period1b)
        self.effort1period1a.setStart(date.DateTime.now())
        self.assertEqual(2, len(self.effortPerPeriod))

    def testChangeStart_WithinPeriod(self):
        self.taskList.append(self.task1)
        self.task1.addEffort(self.effort1period1a)
        self.effort1period1a.setStart(self.effort1period1a.getStart() + \
            date.TimeDelta(seconds=1))
        self.assertEqual(1, len(self.effortPerPeriod))

    def testChangeStopDoesNotAffectPeriod(self):
        self.taskList.append(self.task1)
        self.task1.addEffort(self.effort1period1a)
        composite = list(self.effortPerPeriod)[0]
        start = composite.getStart()
        self.effort1period1a.setStop(date.DateTime.now())
        self.assertEqual(start, composite.getStart())

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
        self.assertEqual(list(self.effortPerPeriod)[0], self.events[0].value())

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

    def testChangeTask(self):
        self.taskList.extend([self.task1, self.task2])
        self.task1.addEffort(self.effort1period1a)
        self.effort1period1a.setTask(self.task2)
        self.assertEqual(1, len(self.effortPerPeriod))
        self.assertEqual(self.task2, list(self.effortPerPeriod)[0].task())

    def testChangeTaskOfChildEffort(self):
        self.taskList.extend([self.task1, self.task2])
        self.task3.addEffort(self.effort3period1a)
        self.effort3period1a.setTask(self.task2)
        self.assertEqual(1, len(self.effortPerPeriod))
        self.assertEqual(self.task2, list(self.effortPerPeriod)[0].task())

    def testRemoveTaskAfterChangeTaskOfEffort(self):
        self.taskList.extend([self.task1, self.task2])
        self.task1.addEffort(self.effort1period1a)
        self.effort1period1a.setTask(self.task2)
        self.taskList.remove(self.task1)
        self.assertEqual(1, len(self.effortPerPeriod))
        self.assertEqual(self.task2, list(self.effortPerPeriod)[0].task())

    def testRemoveAndAddEffortToSamePeriod(self):
        self.taskList.append(self.task1)
        self.task1.addEffort(self.effort1period1a)
        self.task1.removeEffort(self.effort1period1a)
        self.task1.addEffort(self.effort1period1a)
        self.assertEqual(1, len(self.effortPerPeriod))
        self.assertEqual(self.effort1period1a, list(self.effortPerPeriod)[0][0])

    def testMaxDateTime(self):
        self.assertEqual(None, self.effortPerPeriod.maxDateTime())

    def testMaxDateTime_OneEffort(self):
        self.taskList.append(self.task1)
        self.task1.addEffort(self.effort1period1a)
        self.assertEqual(self.effort1period1a.getStop(), 
            self.effortPerPeriod.maxDateTime())

    def testMaxDateTime_OneTrackingEffort(self):
        self.taskList.append(self.task1)
        self.task1.addEffort(effort.Effort(self.task1))
        self.assertEqual(None, self.effortPerPeriod.maxDateTime())

    def testMaxDateTime_TwoEfforts(self):
        self.taskList.append(self.task1)
        self.task1.addEffort(self.effort1period1a)
        now = date.DateTime.now()
        self.task1.addEffort(effort.Effort(self.task1, 
            self.effort1period1a.getStart(), now))
        self.assertEqual(now, self.effortPerPeriod.maxDateTime())
   
    def testNrTracking(self):
        self.assertEqual(0, self.effortPerPeriod.nrBeingTracked())

    def testOriginalLength(self):
        self.assertEqual(0, self.effortPerPeriod.originalLength())


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

        
class MultipleAggregatorsTest(test.TestCase):
    def setUp(self):
        self.taskList = task.TaskList()
        self.effortPerDay = effort.EffortSorter(effort.EffortPerDay(self.taskList))
        self.effortPerWeek = effort.EffortSorter(effort.EffortPerWeek(self.taskList))
        
    def testDeleteEffort_StartOfBothPeriods(self):
        self.task = task.Task()
        self.taskList.append(self.task)
        # Make sure the start of the day and week are the same, 
        # in other words, use a Monday
        self.effort = effort.Effort(self.task, date.DateTime(2006,8,28), 
                            date.DateTime(2006,8,29))
        self.task.addEffort(self.effort)
        self.task.removeEffort(self.effort)
        self.failIf(self.effortPerDay)

