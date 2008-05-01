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

import test
from unittests import asserts 
from taskcoachlib import patterns
from taskcoachlib.domain import task, effort, date


class EffortTest(test.TestCase, asserts.Mixin):
    def setUp(self):
        self.task = task.Task()
        self.effort = effort.Effort(self.task, start=date.DateTime(2004, 1, 1),
            stop=date.DateTime(2004,1,2))
        self.events = []
    
    def onEvent(self, event):
        self.events.append(event)
        
    def testCreate(self):
        self.assertEqual(self.task, self.effort.task())
        self.assertEqual('', self.effort.getDescription())
        
    def testStr(self):
        self.assertEqual('Effort(%s, %s, %s)'%(self.effort.task(), 
            self.effort.getStart(), self.effort.getStop()), str(self.effort))
        
    def testDuration(self):
        self.assertEqual(date.TimeDelta(days=1), self.effort.duration())

    def testNotificationForSetStart(self):
        patterns.Publisher().registerObserver(self.onEvent,
            eventType='effort.start')
        start = date.DateTime.now()
        self.effort.setStart(start)
        self.assertEqual(start, self.events[0].value())
        
    def testNotificationForSetStop(self):
        patterns.Publisher().registerObserver(self.onEvent,
            eventType='effort.stop')
        stop = date.DateTime.now()
        self.effort.setStop(stop)
        self.assertEqual(stop, self.events[0].value())

    def testDurationNotificationForSetStart(self):
        patterns.Publisher().registerObserver(self.onEvent,
            eventType='effort.duration')
        start = date.DateTime.now()
        self.effort.setStart(start)
        self.assertEqual(patterns.Event(self.effort, 'effort.duration',
            self.effort.duration()), self.events[0])

    def testDurationNotificationForSetStop(self):
        patterns.Publisher().registerObserver(self.onEvent,
            eventType='effort.duration')
        stop = date.DateTime.now()
        self.effort.setStop(stop)
        self.assertEqual(patterns.Event(self.effort, 'effort.duration',
            self.effort.duration()), self.events[0])
        
    def testNotificationForSetDescription(self):
        patterns.Publisher().registerObserver(self.onEvent,
            eventType='effort.description')
        self.effort.setDescription('description')
        self.assertEqual('description', self.events[0].value())

    def testNotificationForSetTask(self):
        patterns.Publisher().registerObserver(self.onEvent,
            eventType='effort.task')
        task2 = task.Task()
        self.effort.setTask(task2)
        self.assertEqual(task2, self.events[0].value())

    def testNotificationForStartTracking(self):
        patterns.Publisher().registerObserver(self.onEvent,
            eventType='effort.track.start')
        self.effort.setStop(date.Date())
        self.assertEqual('effort.track.start', self.events[0].type())

    def testNotificationForStopTracking(self):
        patterns.Publisher().registerObserver(self.onEvent,
            eventType='effort.track.stop')
        self.effort.setStop(date.Date())
        self.effort.setStop(date.DateTime.now())
        self.assertEqual('effort.track.stop', self.events[0].type())

    def testDefaultStartAndStop(self):
        effortPeriod = effort.Effort(self.task)
        currentTime = date.DateTime.now()
        now = lambda: currentTime
        self.assertEqual(now()-effortPeriod.getStart(), 
            effortPeriod.duration(now=now))
     
    def testState(self):
        state = self.effort.__getstate__()
        newEffort = effort.Effort(task.Task())
        newEffort.__setstate__(state)
        self.assertEqualEfforts(newEffort, self.effort)
        
    def testCopy(self):
        copyEffort = self.effort.copy()
        self.assertEqualEfforts(copyEffort, self.effort)
        self.assertEqual(copyEffort.getDescription(), 
            self.effort.getDescription())
        
    def testDescription(self):
        self.effort.setDescription('description')
        self.assertEqual('description', self.effort.getDescription())
        
    def testDescription_Constructor(self):
        newEffort = effort.Effort(self.task, description='description')
        self.assertEqual('description', newEffort.getDescription())
        
    def testSetStop_None(self):
        self.effort.setStop()
        self.assertEqual(date.Today(), self.effort.getStop().date())
        
    def testSetStop_Infinite(self):
        self.effort.setStop(date.DateTime.max)
        self.assertEqual(None, self.effort.getStop())

    def testSetStop_SpecificDateTime(self):
        self.effort.setStop(date.DateTime(2005,1,1))
        self.assertEqual(date.DateTime(2005,1,1), self.effort.getStop())
        
    def testIsNotBeingTracked_(self): 
        self.failIf(self.effort.isBeingTracked())

    def testIsBeingTracked(self): 
        self.effort.setStop(date.DateTime.max)
        self.failUnless(self.effort.isBeingTracked())
        
    def testSetTaskToNewTaskWillAddItToNewTask(self):
        task2 = task.Task()
        self.effort.setTask(task2)
        self.assertEqual([self.effort], task2.efforts())
        
    def testSetTaskToNewTaskWillRemoveItFromOldTask(self):
        self.task.addEffort(self.effort)
        task2 = task.Task()
        self.effort.setTask(task2)
        self.assertEqual([self.effort], task2.efforts())
        self.failIf(self.effort in self.task.efforts())

    def testSetTaskToOldTaskTwice(self):
        self.task.addEffort(self.effort)
        self.effort.setTask(self.task)
        self.assertEqual([self.effort], self.task.efforts())
        
    def testRevenueWithoutFee(self):
        self.task.addEffort(self.effort)
        self.assertEqual(0, self.effort.revenue())
        
    def testRevenue_HourlyFee(self):
        self.task.setHourlyFee(100)
        self.task.addEffort(self.effort)
        self.assertEqual(self.effort.duration().hours()*100, 
            self.effort.revenue())
        
    def testRevenue_FixedFee_OneEffort(self):
        self.task.setFixedFee(1000)
        self.task.addEffort(self.effort)
        self.assertEqual(1000, self.effort.revenue())
        
    def testRevenue_FixedFee_TwoEfforts(self):
        self.task.setFixedFee(1000)
        self.task.addEffort(self.effort)
        self.task.addEffort(effort.Effort(self.task, 
            date.DateTime(2005,1,1,10,0), date.DateTime(2005,1,1,22,0)))
        self.assertEqual(2./3*1000., self.effort.revenue())

    def testSubject(self):
        self.assertEqual(self.task.subject(), self.effort.subject())


class EffortWithoutTaskTest(test.TestCase):   
    def setUp(self):
        self.effort = effort.Effort(None, start=date.DateTime(2005,1,1))
        self.task = task.Task()
        self.events = []
        
    def onEvent(self, event):
        self.events.append(event)
        
    def testCreatingAnEffortWithoutTask(self):
        self.assertEqual(None, self.effort.task())
        
    def testSettingTask(self):
        self.effort.setTask(self.task)
        self.assertEqual(self.task, self.effort.task())
    
    def testSettingTask_CausesNoNotification(self):
        patterns.Publisher().registerObserver(self.onEvent, 'effort.task')
        self.effort.setTask(self.task)
        self.failIf(self.events)

