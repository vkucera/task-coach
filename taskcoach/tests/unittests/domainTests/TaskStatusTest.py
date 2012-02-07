'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2012 Task Coach developers <developers@taskcoach.org>

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
from taskcoachlib.domain import task, date
from taskcoachlib import config


class TaskStatusTest(test.TestCase):    
    def setUp(self):
        self.settings = task.Task.settings = config.Settings(load=False)
        self.now = date.Now()
        self.yesterday = self.now - date.oneDay
        self.tomorrow = self.now + date.oneDay
        self.dates = (self.yesterday, self.tomorrow)
        self.dayAfterTomorrow = self.tomorrow + date.oneDay

    def assertTaskStatus(self, status, **taskKwArgs):
        self.assertEqual(status, task.Task(**taskKwArgs).status())
        
    # No dates/times
    
    def testDefaultTaskIsInactive(self):
        self.assertTaskStatus(task.status.inactive)
    
    # One date/time
        
    def testTaskWithCompletionInThePastIsCompleted(self):
        self.assertTaskStatus(task.status.completed, completionDateTime=self.yesterday)
        
    def testTaskWithCompletionInTheFutureIsCompleted(self):
        # Maybe keep the task inactive until the completion date passes? 
        # That would be more consistent with the other date/times
        self.assertTaskStatus(task.status.completed, completionDateTime=self.tomorrow)

    def testTaskWithPlannedStartInThePastIsLate(self):
        self.assertTaskStatus(task.status.late, plannedStartDateTime=self.yesterday)
                
    def testTaskWithPlannedStartInTheFutureIsInactive(self):
        self.assertTaskStatus(task.status.inactive, plannedStartDateTime=self.tomorrow)
        
    def testTaskWithActualStartInThePastIsActive(self):
        self.assertTaskStatus(task.status.active, actualStartDateTime=self.yesterday)

    def testTaskWithActualStartInTheFutureIsInactive(self):
        self.assertTaskStatus(task.status.inactive, actualStartDateTime=self.tomorrow)
        
    def testTaskWithDueInThePastIsOverdue(self):
        self.assertTaskStatus(task.status.overdue, dueDateTime=self.yesterday)

    def testTaskWithDueInTheFutureIsInactive(self):
        self.assertTaskStatus(task.status.inactive, dueDateTime=self.dayAfterTomorrow)
        
    def testTaskWithDueInTheNearFutureIsDueSoon(self):
        self.assertTaskStatus(task.status.duesoon, dueDateTime=self.tomorrow)
    
    # Two dates/times
    
    # planned start date/time and actual start date/time
        
    def testTaskWithPlannedAndActualStartInThePastIsActive(self):
        self.assertTaskStatus(task.status.active, 
                              plannedStartDateTime=self.yesterday,
                              actualStartDateTime=self.yesterday)
        
    def testTaskWithPlannedStartInThePastAndActualStartInTheFutureIsLate(self):
        self.assertTaskStatus(task.status.late, 
                              plannedStartDateTime=self.yesterday,
                              actualStartDateTime=self.tomorrow)
        
    def testTaskWithPlannedStartInTheFutureAndActualStartInThePastIsActive(self):
        self.assertTaskStatus(task.status.active, 
                              plannedStartDateTime=self.tomorrow,
                              actualStartDateTime=self.yesterday)

    def testTaskWithPlannedAndActualStartInTheFutureIsInactive(self):
        self.assertTaskStatus(task.status.inactive, 
                              plannedStartDateTime=self.tomorrow,
                              actualStartDateTime=self.tomorrow)
    
    # planned start date/time and due date/time
        
    def testTaskWithPlannedStartAndDueInThePastIsOverdue(self):
        self.assertTaskStatus(task.status.overdue, 
                              plannedStartDateTime=self.yesterday,
                              dueDateTime=self.yesterday)

    def testTaskWithPlannedStartInThePastAndDueInTheFutureIsLate(self):
        self.assertTaskStatus(task.status.late, 
                              plannedStartDateTime=self.yesterday,
                              dueDateTime=self.dayAfterTomorrow)
       
    def testTaskWithPlannedStartInThePastAndDueInTheNearFutureIsDueSoon(self):
        self.assertTaskStatus(task.status.duesoon, 
                              plannedStartDateTime=self.yesterday,
                              dueDateTime=self.tomorrow)
       
    def testTaskWithPlannedStartInTheFutureAndDueInThePastIsOverdue(self):
        self.assertTaskStatus(task.status.overdue, 
                              plannedStartDateTime=self.tomorrow,
                              dueDateTime=self.yesterday)

    def testTaskWithPlannedStartInTheFutureAndDueInTheFutureIsLate(self):
        self.assertTaskStatus(task.status.inactive, 
                              plannedStartDateTime=self.tomorrow,
                              dueDateTime=self.dayAfterTomorrow)
       
    def testTaskWithPlannedStartInTheFutureAndDueInTheNearFutureIsDueSoon(self):
        self.assertTaskStatus(task.status.duesoon, 
                              plannedStartDateTime=self.tomorrow,
                              dueDateTime=self.tomorrow)

    # planned start date/time and completion date/time
    
    def testTaskWithPlannedStartAndCompletionInThePastIsCompleted(self):
        self.assertTaskStatus(task.status.completed, 
                              plannedStartDateTime=self.yesterday,
                              completionDateTime=self.yesterday)

    def testTaskWithPlannedStartInThePastAndCompletionInTheFutureIsCompleted(self):
        self.assertTaskStatus(task.status.completed, 
                              plannedStartDateTime=self.yesterday,
                              completionDateTime=self.tomorrow)

    def testTaskWithPlannedStartInTheFutureAndCompletionInThePastIsCompleted(self):
        self.assertTaskStatus(task.status.completed, 
                              plannedStartDateTime=self.tomorrow,
                              completionDateTime=self.yesterday)

    def testTaskWithPlannedStartInTheFutureAndCompletionInTheFutureIsComplete(self):
        self.assertTaskStatus(task.status.completed, 
                              plannedStartDateTime=self.tomorrow,
                              completionDateTime=self.tomorrow)
    
    # actual start date/time and due date/time
    
    def testTaskWithActualStartAndDueInThePastIsOverdue(self):
        self.assertTaskStatus(task.status.overdue, 
                              actualStartDateTime=self.yesterday,
                              dueDateTime=self.yesterday)

    def testTaskWithActualStartInThePastAndDueInTheFutureIsActive(self):
        self.assertTaskStatus(task.status.active, 
                              actualStartDateTime=self.yesterday,
                              dueDateTime=self.dayAfterTomorrow)

    def testTaskWithActualStartInThePastAndDueInTheNearFutureIsDueSoon(self):
        self.assertTaskStatus(task.status.duesoon, 
                              actualStartDateTime=self.yesterday,
                              dueDateTime=self.tomorrow)

    def testTaskWithActualStartInTheFutureAndDueInThePastIsOverdue(self):
        self.assertTaskStatus(task.status.overdue, 
                              actualStartDateTime=self.tomorrow,
                              dueDateTime=self.yesterday)

    def testTaskWithActualStartInTheFutureAndDueInTheFutureIsActive(self):
        self.assertTaskStatus(task.status.inactive, 
                              actualStartDateTime=self.tomorrow,
                              dueDateTime=self.dayAfterTomorrow)

    def testTaskWithActualStartInTheFutureAndDueInTheNearFutureIsDueSoon(self):
        self.assertTaskStatus(task.status.duesoon, 
                              actualStartDateTime=self.tomorrow,
                              dueDateTime=self.tomorrow)

    # actual start date/time and completion date/time
   
    def testTaskWithActualStartAndCompletionInThePastIsCompleted(self):
        self.assertTaskStatus(task.status.completed, 
                              actualStartDateTime=self.yesterday,
                              completionDateTime=self.yesterday)

    def testTaskWithActualStartInThePastAndCompletionInTheFutureIsCompleted(self):
        self.assertTaskStatus(task.status.completed, 
                              actualStartDateTime=self.yesterday,
                              completionDateTime=self.tomorrow)

    def testTaskWithActualStartInTheFutureAndCompletionInThePastIsCompleted(self):
        self.assertTaskStatus(task.status.completed, 
                              actualStartDateTime=self.tomorrow,
                              completionDateTime=self.yesterday)

    def testTaskWithActualStartInTheFutureAndCompletionInTheFutureIsComplete(self):
        self.assertTaskStatus(task.status.completed, 
                              actualStartDateTime=self.tomorrow,
                              completionDateTime=self.tomorrow)
   
    # due date/time and completion date/time
    
    def testTaskWithDueAndCompletionInThePastIsCompleted(self):
        self.assertTaskStatus(task.status.completed, 
                              dueDateTime=self.yesterday,
                              completionDateTime=self.yesterday)

    def testTaskWithDueInThePastAndCompletionInTheFutureIsCompleted(self):
        self.assertTaskStatus(task.status.completed, 
                              dueDateTime=self.yesterday,
                              completionDateTime=self.tomorrow)

    def testTaskWithDueInTheFutureAndCompletionInThePastIsCompleted(self):
        self.assertTaskStatus(task.status.completed, 
                              dueDateTime=self.tomorrow,
                              completionDateTime=self.yesterday)

    def testTaskWithDueInTheFutureAndCompletionInTheFutureIsComplete(self):
        self.assertTaskStatus(task.status.completed, 
                              dueDateTime=self.tomorrow,
                              completionDateTime=self.tomorrow)
   
    # Three dates/times
    
    # planned start date/time, actual start date/time and due date/time
    # (Other combinations are not interesting since they are always completed)
    
    def testTaskIsOverdueWheneverDueIsInThePast(self):
        for planned in self.dates:
            for actual in self.dates:
                self.assertTaskStatus(task.status.overdue, 
                                      plannedStartDateTime=planned,
                                      actualStartDateTime=actual,
                                      dueDateTime=self.yesterday)

    def testTaskIsDuesoonWheneverDueIsInTheNearFuture(self):
        for planned in self.dates:
            for actual in self.dates:
                self.assertTaskStatus(task.status.duesoon, 
                                      plannedStartDateTime=planned,
                                      actualStartDateTime=actual,
                                      dueDateTime=self.tomorrow)
         
    def testTaskIsOverdueWheneverDueIsInTheFuture(self):
        for planned in self.dates:
            expectedStatusBasedOnPlannedStart = task.status.late if planned < self.now else task.status.inactive
            for actual in self.dates:
                expectedStatus = task.status.active if actual < self.now else expectedStatusBasedOnPlannedStart
                self.assertTaskStatus(expectedStatus, 
                                      plannedStartDateTime=planned,
                                      actualStartDateTime=actual,
                                      dueDateTime=self.dayAfterTomorrow)
               
    # Four date/times (always completed)
    
    def testTaskWithCompletionDateTimeIsAlwaysCompleted(self):
        for planned in self.dates:
            for actual in self.dates:
                for due in self.dates + (self.dayAfterTomorrow,):
                    for completion in self.dates:
                        self.assertTaskStatus(task.status.completed, 
                                              plannedStartDateTime=planned,
                                              actualStartDateTime=actual,
                                              dueDateTime=due,
                                              completionDateTime=completion)

    # Prerequisites
    
    def testTaskWithUncompletedPrerequisiteIsNeverLate(self):
        prerequisite = task.Task()
        for planned in self.dates:
            self.assertTaskStatus(task.status.inactive, 
                                  plannedStartDateTime=planned,
                                  prerequisites=[prerequisite])

    def testTaskWithCompletedPrerequisiteIsLateWhenPlannedStartIsInThePast(self):
        prerequisite = task.Task(completionDateTime=self.yesterday)
        for planned in self.dates:
            expectedStatus = task.status.late if planned < self.now else task.status.inactive
            self.assertTaskStatus(expectedStatus, plannedStartDateTime=planned,
                                  prerequisites=[prerequisite])
            
    def testMutualPrerequisites(self):
        taskA = task.Task()
        taskB = task.Task(prerequisites=[taskA])
        taskA.addPrerequisites([taskB])
        for eachTask in (taskA, taskB):
            self.assertEqual(task.status.inactive, eachTask.status())
             