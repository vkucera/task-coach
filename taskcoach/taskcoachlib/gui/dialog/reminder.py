'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2011 Task Coach developers <developers@taskcoach.org>

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


class ReminderDialog(sized_controls.SizedDialog):
    def __init__(self, task, taskList, effortList, settings, *args, **kwargs):
        kwargs['title'] = kwargs.get('title', meta.name + ' ' + _('Reminder'))
        super(ReminderDialog, self).__init__(*args, **kwargs)
        self.SetIcon(wx.ArtProvider_GetIcon('taskcoach', wx.ART_FRAME_ICON, (16,16)))
        self.task = task
        self.taskList = taskList
        self.effortList = effortList
        self.settings = settings
        patterns.Publisher().registerObserver(self.onTaskRemoved, 
                                              eventType=self.taskList.removeItemEventType(),
                                              eventSource=self.taskList)
        patterns.Publisher().registerObserver(self.onTaskCompletionDateChanged, 
                                              eventType='task.completionDateTime',
                                              eventSource=task)
        patterns.Publisher().registerObserver(self.onTrackingStartedOrStopped,
                                              eventType=task.trackStartEventType(),
                                              eventSource=task)
        patterns.Publisher().registerObserver(self.onTrackingStartedOrStopped,
                                              eventType=task.trackStopEventType(),
                                              eventSource=task)
        self.openTaskAfterClose = self.ignoreSnoozeOption = False
        pane = self.GetContentsPane()
        pane.SetSizerType("form")
        wx.StaticText(pane, label=_('Task') + ':')
        panel = wx.Panel(pane)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.openTask = wx.Button(panel, label=self.task.subject(recursive=True))
        self.openTask.Bind(wx.EVT_BUTTON, self.onOpenTask)
        sizer.Add(self.openTask)
        if self.settings.getboolean('feature', 'effort'):
            self.startTracking = wx.BitmapButton(panel)
            self.setTrackingIcon()
            self.startTracking.Bind(wx.EVT_BUTTON, self.onStartOrStopTracking)
            sizer.Add(self.startTracking)
        panel.SetSizerAndFit(sizer)
        for label in _('Reminder date/time') + ':', \
            render.dateTime(self.task.reminder()), _('Snooze') + ':':
            wx.StaticText(pane, label=label)
        self.snoozeOptions = wx.ComboBox(pane)
        snoozeTimesUserWantsToSee = [0] + self.settings.getlist('view', 'snoozetimes')
        for minutes, label in date.snoozeChoices:
            if minutes in snoozeTimesUserWantsToSee:
                self.snoozeOptions.Append(label, date.TimeDelta(minutes=minutes))
        self.snoozeOptions.SetSelection(0)
        buttonSizer = self.CreateStdDialogButtonSizer(wx.OK)
        self.markCompleted = wx.Button(self, label=_('Mark task completed'))
        self.markCompleted.Bind(wx.EVT_BUTTON, self.onMarkTaskCompleted)
        if self.task.completed():
            self.markCompleted.Disable()
        buttonSizer.Add(self.markCompleted)
        self.SetButtonSizer(buttonSizer)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Bind(wx.EVT_BUTTON, self.onOK, id=self.GetAffirmativeId())
        self.Fit()
        self.RequestUserAttention()

    def onOpenTask(self, event): # pylint: disable-msg=W0613
        self.openTaskAfterClose = True
        self.Close()
        
    def onStartOrStopTracking(self, event): # pylint: disable-msg=W0613
        if self.task.isBeingTracked():
            command.StopEffortCommand(self.effortList).do()
        else:
            command.StartEffortCommand(self.taskList, [self.task]).do()
        self.setTrackingIcon()
        
    def onTrackingStartedOrStopped(self, event): # pylint: disable-msg=W0613
        self.setTrackingIcon()
        
    def setTrackingIcon(self):
        icon = 'clock_stop_icon' if self.task.isBeingTracked() else 'clock_icon'
        self.startTracking.SetBitmapLabel(wx.ArtProvider_GetBitmap(icon, wx.ART_TOOLBAR, (16,16)))
        
    def onMarkTaskCompleted(self, event): # pylint: disable-msg=W0613
        self.ignoreSnoozeOption = True
        self.Close()
        command.MarkCompletedCommand(self.taskList, [self.task]).do()
    
    def onTaskRemoved(self, event):
        if self.task in event.values():
            self.Close()
            
    def onTaskCompletionDateChanged(self, event): # pylint: disable-msg=W0613
        if self.task.completed():
            self.Close()
        else:
            self.markCompleted.Enable()
    
    def onClose(self, event):
        event.Skip()
        patterns.Publisher().removeInstance(self)
        
    def onOK(self, event):
        event.Skip()
        self.Close()