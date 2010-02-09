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
from taskcoachlib.thirdparty.calendar import wxScheduler, wxSchedule, \
    EVT_SCHEDULE_ACTIVATED, EVT_SCHEDULE_RIGHT_CLICK, \
    EVT_SCHEDULE_DCLICK
from taskcoachlib.domain.date import Date
import tooltip


class Calendar(tooltip.ToolTipMixin, wxScheduler):
    def __init__(self, parent, taskList, iconProvider,  onSelect, onEdit, popupMenu, *args, **kwargs):
        self.getItemTooltipData = parent.getItemTooltipData

        super(Calendar, self).__init__(parent, wx.ID_ANY, *args, **kwargs)

        self.selectCommand = onSelect
        self.iconProvider = iconProvider
        self.editCommand = onEdit
        self.popupMenu = popupMenu

        self.__tip = tooltip.SimpleToolTip(self)
        self.__selection = []

        self.__showNoStartDate = False
        self.__showNoDueDate = False

        self.SetResizable(True)

        self.taskList = taskList
        self.RefreshAllItems(0)

        EVT_SCHEDULE_ACTIVATED(self, self.OnActivation)
        EVT_SCHEDULE_RIGHT_CLICK(self, self.OnPopup)
        EVT_SCHEDULE_DCLICK(self, self.OnEdit)

    def SetShowNoStartDate(self, doShow):
        self.__showNoStartDate = doShow
        self.RefreshAllItems(0)

    def SetShowNoDueDate(self, doShow):
        self.__showNoDueDate = doShow
        self.RefreshAllItems(0)

    def OnActivation(self, event):
        self.SetFocus()

        if self.__selection:
            self.taskMap[self.__selection[0].id()].SetSelected(False)

        if event.schedule is None:
            self.__selection = []
        else:
            self.__selection = [event.schedule.task]
            event.schedule.SetSelected(True)

        wx.CallAfter(self.selectCommand)
        event.Skip()

    def OnPopup(self, event):
        self.OnActivation(event)
        wx.CallAfter(self.PopupMenu, self.popupMenu)

    def OnEdit(self, event):
        if event.schedule is not None:
            self.editCommand(event.schedule.task)

    def RefreshAllItems(self, count):
        selectionId = None
        if self.__selection:
            selectionId = self.__selection[0].id()
        self.__selection = []

        self.DeleteAll()

        schedules = []
        self.taskMap = {}

        for task in self.taskList:
            if not task.isDeleted():
                if task.startDate() == Date() and not self.__showNoStartDate:
                    continue

                if task.dueDate() == Date() and not self.__showNoDueDate:
                    continue

                schedule = TaskSchedule(task, self.iconProvider)
                schedules.append(schedule)
                self.taskMap[task.id()] = schedule

                if task.id() == selectionId:
                    self.__selection = [task]
                    schedule.SetSelected(True)

        self.Add(schedules)
        wx.CallAfter(self.selectCommand)

    def RefreshItems(self, *args):
        for task in args:
            doShow = True

            if task.isDeleted():
                doShow = False

            if task.startDate() == Date() and task.dueDate() == Date():
                doShow = False

            if task.startDate() == Date() and not self.__showNoStartDate:
                doShow = False

            if task.dueDate() == Date() and not self.__showNoDueDate:
                doShow = False

            if doShow:
                if self.taskMap.has_key(task.id()):
                    self.taskMap[task.id()].update()
                else:
                    schedule = TaskSchedule(task, self.iconProvider)
                    self.taskMap[task.id()] = schedule
                    self.Add([schedule])
            else:
                if self.taskMap.has_key(task.id()):
                    self.Delete(self.taskMap[task.id()])
                    del self.taskMap[task.id()]
                    if self.__selection and self.__selection[0].id() == task.id():
                        self.__selection = []
                        wx.CallAfter(self.selectCommand)

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
        return self.__selection

    def isAnyItemCollapsable(self):
        return False


class TaskSchedule(wxSchedule):
    def __init__(self, task, iconProvider):
        super(TaskSchedule, self).__init__()

        self.__selected = False

        self.clientdata = task
        self.iconProvider = iconProvider
        self.update()

    def SetSelected(self, selected):
        self.__selected = selected
        if selected:
            self.color = wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHT)
        else:
            self.color = wx.Color(*(self.task.backgroundColor() or (255, 255, 255)))

    @property
    def task(self):
        return self.clientdata

    def update(self):
        self.Freeze()
        try:
            self.description = self.task.subject()

            started = self.task.startDate()
            if started == Date():
                self.start = wx.DateTimeFromDMY(1, 1, 0) # Huh
            else:
                self.start = wx.DateTimeFromDMY(started.day, started.month - 1, started.year, 0, 0, 1)

            ended = self.task.dueDate()
            if ended == Date():
                self.end = wx.DateTimeFromDMY(1, 1, 9999)
            else:
                self.end = wx.DateTimeFromDMY(ended.day, ended.month - 1, ended.year, 23, 59, 0)

            if self.task.completed():
                self.done = True

            self.color = wx.Color(*(self.task.backgroundColor() or (255, 255, 255)))
            self.foreground = wx.Color(*(self.task.foregroundColor(True) or (0, 0, 0)))

            self.icon = self.iconProvider(self.task, False)
        finally:
            self.Thaw()
