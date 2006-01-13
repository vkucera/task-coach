import wx
from i18n import _

class ReminderController(object):
    def __init__(self, taskList, *args, **kwargs):
        self._taskList = taskList
        self._taskList.registerObserver(self.onReminder, 'reminder')
        super(ReminderController, self).__init__(*args, **kwargs)
        
    def onReminder(self, notification, *args, **kwargs):
        wx.MessageBox(notification.task.subject(), caption=_('Reminder'),
                      style=wx.ICON_WARNING)