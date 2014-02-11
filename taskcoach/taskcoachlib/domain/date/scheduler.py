'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2014 Task Coach developers <developers@taskcoach.org>

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

from taskcoachlib import patterns
import dateandtime, timedelta
import logging
import timedelta
import wx
import weakref
import bisect


class ScheduledMethod(object):
    def __init__(self, method):
        self.__func = method.im_func
        self.__self = weakref.ref(method.im_self)

    def __eq__(self, other):
        return self.__func is other.__func and self.__self() is other.__self()

    def __hash__(self):
        return hash(self.__dict__['_ScheduledMethod__func'])

    def __call__(self, *args, **kwargs):
        obj = self.__self()
        if obj is None:
            Scheduler().unschedule(self)
        else:
            self.__func(obj, *args, **kwargs)


class wxScheduler(wx.EvtHandler):
    """
    A class to schedule jobs at specified date/time. Unlike apscheduler, this
    uses wx.Timers instead of threading, in order to avoid busy waits.
    """
    def __init__(self):
        super(wxScheduler, self).__init__()
        self.__jobs = []
        self.__timerId = wx.NewId()
        self.__timer = None
        self.__firing = False
        wx.EVT_TIMER(self, self.__timerId, self.__onTimer)

    def __schedule(self, job, dateTime, interval):
        if self.__timer is not None:
            self.__timer.Stop()
            self.__timer = None
        bisect.insort_right(self.__jobs, (dateTime, job, interval))
        if not self.__firing:
            self.__fire()

    def scheduleDate(self, job, dateTime):
        """
        Schedules 'job' to be called at 'dateTime'. This assumes the caller is the
        wx main loop thread.
        """
        self.__schedule(job, dateTime, None)

    def scheduleInterval(self, job, interval, startDateTime=None):
        self.__schedule(job, startDateTime or dateandtime.Now() + interval, interval)

    def unschedule(self, theJob):
        for idx, (ts, job, interval) in enumerate(self.__jobs):
            if job == theJob:
                del self.__jobs[idx]
                break

    def isScheduled(self, theJob):
        for ts, job, interval in self.__jobs:
            if job == theJob:
                return True
        return False

    def shutdown(self):
        if self.__timer is not None:
            self.__timer.Stop()
            self.__timer = None
        self.__jobs = []

    def jobs(self):
        return [job for ts, job, interval in self.__jobs]

    def __fire(self):
        self.__firing = True
        try:
            while self.__jobs and self.__jobs[0][0] <= dateandtime.Now():
                ts, job, interval = self.__jobs.pop(0)
                try:
                    job()
                except:
                    # Hum.
                    import traceback
                    traceback.print_exc()
                if interval is not None:
                    self.__schedule(job, ts + interval, interval)
        finally:
            self.__firing = False

        if self.__jobs and self.__timer is None:
            nextDuration = int((self.__jobs[0][0] - dateandtime.Now()).total_seconds() * 1000)
            nextDuration = max(nextDuration, 1)
            nextDuration = min(nextDuration, 2**31-1)
            self.__timer = wx.Timer(self, self.__timerId)
            self.__timer.Start(nextDuration, True)

    def __onTimer(self, event):
        self.__timer = None
        self.__fire()


class Scheduler(object):
    __metaclass__ = patterns.Singleton

    def __init__(self, *args, **kwargs):
        super(Scheduler, self).__init__(*args, **kwargs)
        self.__scheduler = wxScheduler()

    def shutdown(self):
        self.__scheduler.shutdown()

    def schedule(self, function, dateTime):
        job = ScheduledMethod(function)
        self.__scheduler.scheduleDate(job, dateTime)
        return job

    def schedule_interval(self, function, days=0, minutes=0, seconds=0):
        job = ScheduledMethod(function)
        if not self.__scheduler.isScheduled(job):
            startDate = dateandtime.Now().endOfDay() if days > 0 else None
            self.__scheduler.scheduleInterval(job, timedelta.TimeDelta(days=days, minutes=minutes, seconds=seconds), startDateTime=startDate)
            return job

    def unschedule(self, function):
        job = function if isinstance(function, ScheduledMethod) else ScheduledMethod(function)
        self.__scheduler.unschedule(job)

    def is_scheduled(self, function):
        return self.__scheduler.isScheduled(ScheduledMethod(function))

    def get_jobs(self):
        return self.__scheduler.jobs()
