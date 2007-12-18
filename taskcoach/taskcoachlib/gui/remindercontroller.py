import wx, patterns
from i18n import _
from domain import date
from gui.dialog import reminder

class ReminderController(object):
    def __init__(self, taskList, settings, uiCommands, *args, **kwargs):
        super(ReminderController, self).__init__(*args, **kwargs)
        patterns.Publisher().registerObserver(self.onSetReminder,
            eventType='task.reminder')
        patterns.Publisher().registerObserver(self.onAddTask,
            eventType=taskList.addItemEventType())
        patterns.Publisher().registerObserver(self.onRemoveTask,
            eventType=taskList.removeItemEventType())
        self.__tasksWithReminders = {} # {task: reminderDateTime}
        self.__registerRemindersForTasks(taskList)
        self.settings = settings
        self.uiCommands = uiCommands
        self.taskList = taskList
    
    def onAddTask(self, event):
        self.__registerRemindersForTasks(event.values())
                
    def onRemoveTask(self, event):
        self.__removeRemindersForTasks(event.values())
                
    def onSetReminder(self, event):
        task, newReminderDateTime = event.source(), event.value()
        oldReminderDateTime = self.__tasksWithReminders.get(task, None)
        if oldReminderDateTime:
            self.__removeReminder(task, oldReminderDateTime)
        if newReminderDateTime:
            self.__registerReminder(task, newReminderDateTime)            
        
    def onReminder(self, event):
        now = event.value() + date.TimeDelta(seconds=1)
        for task, reminderDateTime in self.__tasksWithReminders.items():
            if reminderDateTime <= now:
                self.showReminderMessage(task)
                self.__removeReminder(task)

    def showReminderMessage(self, task):
        mainWindow = wx.GetApp().GetTopWindow()
        reminderDialog = reminder.ReminderDialog(task, 
            self.taskList.categories(), self.uiCommands, self.settings, 
            mainWindow)
        reminderDialog.Bind(wx.EVT_CLOSE, self.onCloseReminderDialog)
        if not mainWindow.IsShown():
            mainWindow.Show()
        if not mainWindow.IsActive():
            mainWindow.RequestUserAttention()
        reminderDialog.Show()
        
    def onCloseReminderDialog(self, event):
        dialog = event.EventObject
        snoozeOptions = dialog.snoozeOptions
        snoozeTimeDelta = snoozeOptions.GetClientData(snoozeOptions.Selection)
        if snoozeTimeDelta:
            newReminder = date.DateTime.now() + snoozeTimeDelta
        else:
            newReminder = None
        dialog.task.setReminder(newReminder)
        dialog.Destroy()
        
    def __registerRemindersForTasks(self, tasks):
        for task in tasks:
            if task.reminder():
                self.__registerReminder(task)

    def __removeRemindersForTasks(self, tasks):
        for task in tasks:
            if task in self.__tasksWithReminders:
                self.__removeReminder(task)

    def __registerReminder(self, task, reminderDateTime=None):
        reminderDateTime = reminderDateTime or task.reminder()
        if reminderDateTime < date.DateTime.now():
            reminderDateTime = date.DateTime.now() + date.TimeDelta(seconds=2)
        if reminderDateTime not in self.__tasksWithReminders.values():
            self.__changeDateTimeObservation(reminderDateTime, 'registerObserver')
        self.__tasksWithReminders[task] = reminderDateTime
            
    def __removeReminder(self, task, reminderDateTime=None):
        reminderDateTime = reminderDateTime or task.reminder()
        del self.__tasksWithReminders[task]
        if reminderDateTime not in self.__tasksWithReminders.values():
            self.__changeDateTimeObservation(reminderDateTime, 'removeObserver')
    
    def __changeDateTimeObservation(self, reminderDateTime, registrationMethod):
        eventType = date.Clock().eventType(reminderDateTime)
        getattr(patterns.Publisher(), registrationMethod)(self.onReminder, 
            eventType=eventType)
