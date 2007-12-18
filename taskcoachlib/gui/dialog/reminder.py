import wx, meta, editor, command
from widgets import sized_controls
from i18n import _
from domain import date
from gui import render

class ReminderDialog(sized_controls.SizedDialog):
    snoozeChoices = [_("Don't snooze"), _('Five minutes'), _('Ten minutes'),
                     _('Fifteen minutes'), _('Half an hour'), _('One hour'),
                     _('Two hours'), ('24 hours')]
    snoozeTimes = [date.TimeDelta(minutes=minutes) for minutes in \
                   (0, 5, 10, 15, 30, 60, 120, 24*60)]
    
    def __init__(self, task, categories, uiCommands, settings, *args, **kwargs):
        kwargs['title'] = kwargs.get('title', meta.name + ' ' + _('Reminder'))
        super(ReminderDialog, self).__init__(*args, **kwargs)
        self.task = task
        self.categories = categories
        self.uiCommands = uiCommands
        self.settings = settings
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

    def onOpenTask(self, event):
        self.openTask.Enable(False)
        editTask = editor.TaskEditor(self.Parent,
            command.EditTaskCommand([self.task], [self.task]),
            [self.task], self.uiCommands, self.settings, self.categories,
            bitmap='edit')
        editTask.Show()
        editTask.Bind(wx.EVT_CLOSE, self.onCloseTask)

    def onCloseTask(self, event):
        # This dialog may have been closed when the user closes the task editor
        try:
            self.openTask.Enable()
        except wx.PyDeadObjectError: 
            pass
        event.Skip()
        
