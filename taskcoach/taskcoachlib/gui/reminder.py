'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2010 Task Coach developers <developers@taskcoach.org>

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
from taskcoachlib import meta, patterns, command
from taskcoachlib.widgets import sized_controls
from taskcoachlib.i18n import _
from taskcoachlib.domain import date
from taskcoachlib.gui import render
from taskcoachlib.notify import NotificationFrameBase


class ReminderPanel(wx.Panel):
    def __init__(self, frame, *args, **kwargs):
        super(ReminderPanel, self).__init__(*args, **kwargs)

        self.mainPanel = sized_controls.SizedPanel(self, -1)
        
        mysizer = wx.BoxSizer(wx.VERTICAL)
        mysizer.Add(self.mainPanel, 1, wx.EXPAND | wx.ALL, 2)
        self.SetSizer(mysizer)

        self.frame = frame

        patterns.Publisher().registerObserver(self.onTaskRemoved, 
                                              eventType=self.frame.taskList.removeItemEventType(),
                                              eventSource=self.frame.taskList)
        patterns.Publisher().registerObserver(self.onTaskCompletionDateChanged, 
                                              eventType='task.completionDateTime',
                                              eventSource=self.frame.task)
        self.openTaskAfterClose = self.ignoreSnoozeOption = False
        self.mainPanel.SetSizerType("form")
        wx.StaticText(self.mainPanel, label=_('Task') + ':')
        self.openTask = wx.Button(self.mainPanel, label=self.frame.task.subject(recursive=True))
        self.openTask.Bind(wx.EVT_BUTTON, self.onOpenTask)
        for label in _('Reminder date/time') + ':', \
            render.dateTime(self.frame.task.reminder()), _('Snooze') + ':':
            wx.StaticText(self.mainPanel, label=label)
        self.snoozeOptions = wx.ComboBox(self.mainPanel)
        snoozeTimesUserWantsToSee = [0] + eval(self.frame.settings.get('view', 'snoozetimes'))
        for minutes, label in date.snoozeChoices:
            if minutes in snoozeTimesUserWantsToSee:
                self.snoozeOptions.Append(label, date.TimeDelta(minutes=minutes))
        self.snoozeOptions.SetSelection(0)
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.markCompleted = wx.Button(self, label=_('Mark task completed'))
        self.markCompleted.Bind(wx.EVT_BUTTON, self.onMarkTaskCompleted)
        if self.frame.task.completed():
            self.markCompleted.Disable()
        buttonSizer.Add(wx.Button(self, wx.ID_OK, _('OK')), 0, wx.ALL, 3)
        buttonSizer.Add(self.markCompleted, 0, wx.ALL, 3)
        self.GetSizer().Add(buttonSizer, 0, wx.ALIGN_RIGHT|wx.ALL, 3)
        self.Bind(wx.EVT_BUTTON, self.onOK, id=wx.ID_OK)
        self.Fit()

    def onOpenTask(self, event): # pylint: disable-msg=W0613
        self.openTaskAfterClose = True
        self.frame.DoClose()
        
    def onMarkTaskCompleted(self, event): # pylint: disable-msg=W0613
        self.ignoreSnoozeOption = True
        self.frame.DoClose()
        command.MarkCompletedCommand(self.frame.taskList, [self.frame.task]).do()
    
    def onTaskRemoved(self, event):
        if self.frame.task in event.values():
            self.frame.DoClose()
            
    def onTaskCompletionDateChanged(self, event): # pylint: disable-msg=W0613
        if self.frame.task.completed():
            self.frame.DoClose()
        else:
            self.markCompleted.Enable()
        
    def onOK(self, event):
        event.Skip()
        self.frame.DoClose()


class ReminderFrame(NotificationFrameBase):
    def __init__(self, mainWindow, task, taskList, settings, **kwargs):
        self.task = task
        self.taskList = taskList
        self.settings = settings

        super(ReminderFrame, self).__init__(kwargs.pop('title', meta.name + ' ' + _('Reminder')),
                                            parent=mainWindow,
                                            icon=wx.ArtProvider.GetBitmap('taskcoach', wx.ART_FRAME_ICON, (16, 16)),
                                            **kwargs)

        self.Bind(wx.EVT_CLOSE, self.onClose)

    def AddInnerContent(self, sizer, panel):
        self.__panel = ReminderPanel(self, panel, wx.ID_ANY)
        sizer.Add(self.__panel, 1, wx.EXPAND|wx.ALL, 3)
    
    def onClose(self, event):
        event.Skip()
        patterns.Publisher().removeInstance(self.__panel)

    # The reminder controller accesses some attributes directly
    def __getattr__(self, name):
        return getattr(self.__panel, name)
