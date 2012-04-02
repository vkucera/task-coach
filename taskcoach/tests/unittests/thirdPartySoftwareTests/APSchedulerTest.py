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
from taskcoachlib.domain import date
from taskcoachlib.thirdparty import apscheduler


class APSchedulerTest(test.TestCase):
    def setUp(self):
        super(APSchedulerTest, self).setUp()
        self.jobCalled = 0
        self.scheduler = apscheduler.scheduler.Scheduler()
        self.scheduler.start()
    
    def job(self):
        self.jobCalled += 1
        
    def testScheduleJob(self):
        self.scheduler.add_date_job(self.job, date.Now() + date.TimeDelta(microseconds=650))
        while self.jobCalled == 0:
            pass
        self.assertEqual(1, self.jobCalled)
        
    def testScheduleTwoJobs(self):
        self.scheduler.add_date_job(self.job, date.Now() + date.TimeDelta(microseconds=650))
        self.scheduler.add_date_job(self.job, date.Now() + date.TimeDelta(microseconds=700))
        while self.scheduler.get_jobs():
            pass
        self.assertEqual(2, self.jobCalled)
        
    def testScheduleJobInThePastRaisesValueError(self):
        self.assertRaises(ValueError, 
                          lambda: self.scheduler.add_date_job(self.job, date.Now() - date.TimeDelta(microseconds=500)))
    
    def testScheduleJobWithInterval(self):
        self.scheduler.add_interval_job(self.job, seconds=0.01)
        while self.jobCalled < 2:
            pass
        self.assertEqual(2, self.jobCalled)
        self.scheduler.unschedule_func(self.job)
        
