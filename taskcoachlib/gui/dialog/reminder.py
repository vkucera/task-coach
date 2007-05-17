import wx, meta
from widgets import sized_controls
from i18n import _
from domain import date

class ReminderDialog(sized_controls.SizedDialog):
    snoozeChoices = [_("Don't snooze"), _('Five minutes'), _('Ten minutes'),
                     _('Fifteen minutes'), _('Half an hour'), _('One hour'),
                     _('Two hours'), ('24 hours')]
    snoozeTimes = [date.TimeDelta(minutes=minutes) for minutes in \
                   (0, 5, 10, 15, 30, 60, 120, 24*60)]
    
    def __init__(self, task, *args, **kwargs):
        kwargs['title'] = kwargs.get('title', meta.name + ' ' + _('Reminder'))
        super(ReminderDialog, self).__init__(*args, **kwargs)
        self.task = task
        pane = self.GetContentsPane()
        pane.SetSizerType("form")
        for label in _('Task') + ':', self.task.subject(), _('Snooze') + ':':
            wx.StaticText(pane, label=label)
        self.snoozeOptions = wx.ComboBox(pane)
        for choice, timeDelta in zip(self.snoozeChoices, self.snoozeTimes):
            self.snoozeOptions.Append(choice, timeDelta)
        self.snoozeOptions.SetSelection(0)
        self.SetButtonSizer(self.CreateStdDialogButtonSizer(wx.OK))
        self.Bind(wx.EVT_BUTTON, lambda event: self.Close())
        self.Fit()
