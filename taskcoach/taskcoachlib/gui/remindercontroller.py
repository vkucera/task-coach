import wx
from i18n import _

class ReminderController(object):
    def __init__(self, taskList, *args, **kwargs):
        self._taskList = taskList
        self._taskList.registerObserver(self.onReminder, 'reminder')
        super(ReminderController, self).__init__(*args, **kwargs)
        
    def onReminder(self, event):
        wx.MessageBox(event.value(), caption=_('Reminder'),
                      style=wx.ICON_WARNING)

    def reminders(self):
        return []
