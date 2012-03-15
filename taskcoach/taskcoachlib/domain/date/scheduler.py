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

import wx
from taskcoachlib import patterns
from taskcoachlib.thirdparty import apscheduler
import dateandtime, timedelta


class Scheduler(apscheduler.scheduler.Scheduler):
    __metaclass__ = patterns.Singleton
    
    def __init__(self, *args, **kwargs):
        super(Scheduler, self).__init__(*args, **kwargs)
        self.start()
    
    def schedule(self, func, dateTime):
        def callback():
            wx.CallAfter(func)

        if dateTime <= dateandtime.Now() + timedelta.TimeDelta(milliseconds=500):
            callback()
        else:
            return self.add_date_job(callback, dateTime)
