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

from taskcoachlib import patterns
from taskcoachlib.thirdparty import apscheduler
import dateandtime
import logging
import timedelta
import wx


class Scheduler(apscheduler.scheduler.Scheduler):
    __metaclass__ = patterns.Singleton
    
    def __init__(self, *args, **kwargs):
        self.__handler = self.createLogHandler()
        super(Scheduler, self).__init__(*args, **kwargs)
        self.__jobs = {}
        self.start()
        
    def createLogHandler(self):
        # apscheduler logs, but doesn't provide a default handler itself, make it happy:
        schedulerLogger = logging.getLogger('taskcoachlib.thirdparty.apscheduler.scheduler')
        try:
            handler = logging.NullHandler()
        except AttributeError:
            # NullHandler is new in Python 2.7, log to stderr if not available
            handler = logging.StreamHandler()
        schedulerLogger.addHandler(handler)
        return handler

    def removeLogHandler(self):
        # accumulation of handlers in the unit/language/etc tests makes them *slow*
        schedulerLogger = logging.getLogger('taskcoachlib.thirdparty.apscheduler.scheduler')
        schedulerLogger.removeHandler(self.__handler)

    def shutdown(self, wait=True, shutdown_threadpool=True):
        super(Scheduler, self).shutdown(wait=wait, 
                                        shutdown_threadpool=shutdown_threadpool)
        self.removeLogHandler()

    def schedule(self, function, dateTime):
        def callback():
            if function in self.__jobs:
                del self.__jobs[function]
            wx.CallAfter(function)

        if dateTime <= dateandtime.Now() + timedelta.TimeDelta(milliseconds=500):
            callback()
        else:
            self.__jobs[function] = job = self.add_date_job(callback, dateTime, misfire_grace_time=0)
            return job
        
    def schedule_interval(self, function, days=0, minutes=0, seconds=0):
        def callback():
            wx.CallAfter(function)
            
        if function not in self.__jobs:
            start_date = dateandtime.Now().endOfDay() if days > 0 else None
            self.__jobs[function] = job = self.add_interval_job(callback, days=days, 
                minutes=minutes, seconds=seconds, start_date=start_date, misfire_grace_time=0,
                coalesce=True)
            return job

    def unschedule(self, function):
        if function in self.__jobs:
            try:
                self.unschedule_job(self.__jobs[function])
            except KeyError:
                pass
            del self.__jobs[function]

    def is_scheduled(self, function):
        return function in self.__jobs
