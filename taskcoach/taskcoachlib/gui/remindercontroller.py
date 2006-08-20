import wx, patterns
from i18n import _
import domain.date as date

class ReminderController(object):
    def __init__(self, taskList, *args, **kwargs):
        super(ReminderController, self).__init__(*args, **kwargs)
        patterns.Publisher().registerObserver(self.onSetReminder,
            eventType='task.reminder')
        patterns.Publisher().registerObserver(self.onAddTask,
            eventType=taskList.addItemEventType())
        patterns.Publisher().registerObserver(self.onRemoveTask,
            eventType=taskList.removeItemEventType())
        self.__tasksWithReminders = {} # {task: reminderDateTime}
        self.__registerRemindersForTasks(taskList)
    
    def onAddTask(self, event):
        self.__registerRemindersForTasks(event.values())
                
    def onRemoveTask(self, event):
        self.__removeRemindersForTasks(event.values())
                
    def onSetReminder(self, event):
        task, reminderDateTime = event.source(), event.value()
        previousReminderDateTime = self.__tasksWithReminders.get(task, None)
        if previousReminderDateTime:
            self.__removeReminder(task, previousReminderDateTime)
        self.__registerReminder(task)
        
    def onReminder(self, event):
        now = event.value()
        for task, reminderDateTime in self.__tasksWithReminders.items():
            if reminderDateTime <= now:
                self.showReminderMessage(task.subject())
                self.__removeReminder(task)

    def showReminderMessage(self, message):
        wx.MessageBox(message, caption=_('Reminder'), style=wx.ICON_WARNING)

    def __registerRemindersForTasks(self, tasks):
        for task in tasks:
            if task.reminder():
                self.__registerReminder(task)

    def __removeRemindersForTasks(self, tasks):
        for task in tasks:
            if task in self.__tasksWithReminders:
                self.__removeReminder(task)

    def __registerReminder(self, task):
        reminderDateTime = task.reminder()
        if not reminderDateTime in self.__tasksWithReminders.values():
            self.__changeDateTimeObservation(reminderDateTime, 'registerObserver')
        self.__tasksWithReminders[task] = reminderDateTime
            
    def __removeReminder(self, task, reminderDateTime=None):
        reminderDateTime = reminderDateTime or task.reminder()
        del self.__tasksWithReminders[task]
        if not reminderDateTime in self.__tasksWithReminders.values():
            self.__changeDateTimeObservation(reminderDateTime, 'removeObserver')
    
    def __changeDateTimeObservation(self, reminderDateTime, registrationMethod):
        eventType = date.Clock().eventType(reminderDateTime)
        getattr(patterns.Publisher(), registrationMethod)(self.onReminder, 
            eventType=eventType)
