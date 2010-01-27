'''
Task Coach - Your friendly task manager
Copyright (C) 2010 Jerome Laheurte <fraca7@free.fr>

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

import wx, operator
from taskcoachlib.thirdparty.calendar import wxScheduler, wxSchedule
from taskcoachlib.domain.date import Date
import tooltip


class Calendar(tooltip.ToolTipMixin, wxScheduler):
    def __init__(self, parent, taskList, *args, **kwargs):
        self.getItemTooltipData = parent.getItemTooltipData

        super(Calendar, self).__init__(parent, wx.ID_ANY, *args, **kwargs)

        self.__tip = tooltip.SimpleToolTip(self)

        self.SetResizable(True)

        self.taskList = taskList
        self.RefreshAllItems(0)

    def RefreshAllItems(self, count):
        self.DeleteAll()

        schedules = []
        self.taskMap = {}

        for task in self.taskList:
            if task.startDate() != Date() and task.dueDate() != Date() and not task.isDeleted():
                schedule = TaskSchedule(task)
                schedules.append(schedule)
                self.taskMap[task.id()] = schedule

        self.Add(schedules)

    def RefreshItems(self, *args):
        for task in args:
            if task.dueDate() == Date() or task.startDate() == Date() or task.isDeleted():
                if self.taskMap.has_key(task.id()):
                    self.Delete(self.taskMap[task.id()])
                    del self.taskMap[task.id()]
            elif self.taskMap.has_key(task.id()):
                self.taskMap[task.id()].update()
            else:
                schedule = TaskSchedule(task)
                self.taskMap[task.id()] = schedule
                self.Add([schedule])

    def GetItemCount(self):
        return len(self.GetSchedules())
        
    def OnBeforeShowToolTip(self, x, y):
        schedule = self._findSchedule(wx.Point(x, y))

        if schedule and isinstance(schedule, TaskSchedule):
            item = schedule.task

            tooltipData = self.getItemTooltipData(item)
            doShow = reduce(operator.__or__,
                            map(bool, [data[1] for data in tooltipData]),
                            False)
            if doShow:
                self.__tip.SetData(tooltipData)
                return self.__tip
            else:
                return None

    def GetMainWindow(self):
        return self
    
    MainWindow = property(GetMainWindow)

    def curselection(self):
        return []

    def isAnyItemCollapsable(self):
        return False


class TaskSchedule(wxSchedule):
    def __init__(self, task):
        super(TaskSchedule, self).__init__()

        self.clientdata = task
        self.update()

    @property
    def task(self):
        return self.clientdata

    def update(self):
        self.Freeze()
        try:
            self.description = self.task.subject()

            started = self.task.startDate()
            self.start = wx.DateTimeFromDMY(started.day, started.month - 1, started.year)

            ended = self.task.dueDate()
            self.end = wx.DateTimeFromDMY(ended.day, ended.month - 1, ended.year, 23, 59, 59)

            if self.task.completed():
                self.done = True

            self.color = wx.Color(*(self.task.backgroundColor() or (255, 255, 255)))
        finally:
            self.Thaw()
