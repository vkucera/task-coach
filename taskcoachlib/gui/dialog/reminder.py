'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2010 Frank Niessink <frank@niessink.com>

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
from taskcoachlib import meta, patterns
from taskcoachlib.widgets import sized_controls
from taskcoachlib.i18n import _
from taskcoachlib.domain import date
from taskcoachlib.gui import render


class ReminderDialog(sized_controls.SizedDialog):
    snoozeChoices = [_("Don't snooze"), _('Five minutes'), _('Ten minutes'),
                     _('Fifteen minutes'), _('Half an hour'), _('One hour'),
                     _('Two hours'), _('24 hours')]
    snoozeTimes = [date.TimeDelta(minutes=minutes) for minutes in \
                   (0, 5, 10, 15, 30, 60, 120, 24*60)]
    
    def __init__(self, task, taskList, *args, **kwargs):
        kwargs['title'] = kwargs.get('title', meta.name + ' ' + _('Reminder'))
        super(ReminderDialog, self).__init__(*args, **kwargs)
        self.task = task
        self.taskList = taskList
        patterns.Publisher().registerObserver(self.onTaskRemoved, 
                                              eventType=self.taskList.removeItemEventType(),
                                              eventSource=self.taskList)
        patterns.Publisher().registerObserver(self.onTaskCompletionDateChanged, 
                                              eventType='task.completionDate',
                                              eventSource=self.task)
        self.openTaskAfterClose = False
        pane = self.GetContentsPane()
        pane.SetSizerType("form")
        wx.StaticText(pane, label=_('Task') + ':')
        self.openTask = wx.Button(pane, label=self.task.subject(recursive=True))
        self.openTask.Bind(wx.EVT_BUTTON, self.onOpenTask)
        for label in _('Reminder date/time') + ':', \
            render.dateTime(self.task.reminder()), _('Snooze') + ':':
            wx.StaticText(pane, label=label)
        self.snoozeOptions = wx.ComboBox(pane)
        for choice, timeDelta in zip(self.snoozeChoices, self.snoozeTimes):
            self.snoozeOptions.Append(choice, timeDelta)
        self.snoozeOptions.SetSelection(0)
        self.SetButtonSizer(self.CreateStdDialogButtonSizer(wx.OK))
        self.Bind(wx.EVT_BUTTON, lambda event: self.Close())
        self.Fit()

    def onOpenTask(self, event): # pylint: disable-msg=W0613
        self.openTaskAfterClose = True
        self.Close()

    def onTaskRemoved(self, event):
        if self.task in event.values():
            self.Close()
            
    def onTaskCompletionDateChanged(self, event):
        if self.task.completed():
            self.Close()
            
    def Close(self):
        patterns.Publisher().removeInstance(self)
        super(ReminderDialog, self).Close()
