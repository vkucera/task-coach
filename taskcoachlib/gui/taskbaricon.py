import meta, wx, date
from i18n import _

        
class TaskBarIcon(wx.TaskBarIcon):
    def __init__(self, mainwindow, taskList, defaultBitmap='taskcoach', 
            tickBitmap='tick', tackBitmap='tack', *args, **kwargs):
        super(TaskBarIcon, self).__init__(*args, **kwargs)
        self.__bitmap = self.__defaultBitmap = defaultBitmap
        self.__tickBitmap = tickBitmap
        self.__tackBitmap = tackBitmap       
        self.__tracking = False
        taskList.registerObserver(self.onNotifyTaskList)
        self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, mainwindow.restore)
        self.__nrDueToday = 0
        self.__setIcon()
        
    def setPopupMenu(self, menu):
        self.Bind(wx.EVT_TASKBAR_RIGHT_UP, self.popupTaskBarMenu)
        self.popupmenu = menu

    def popupTaskBarMenu(self, event):
        self.PopupMenu(self.popupmenu)

    def onNotifyTaskList(self, notification, *args, **kwargs):
        taskList = notification.source
        self.__tracking = taskList.nrBeingTracked() > 0
        self.__nrDueToday = taskList.nrDueToday()
        self.__setIcon()
                
    def tooltip(self):
        return self.__getTooltipText() 
        
    def __getTooltipText(self):
        if self.__nrDueToday == 0:
            nrTasksText = _('No tasks due today')
        elif self.__nrDueToday == 1:
            nrTasksText = _('One task due today')
        else:
            nrTasksText = _('%d tasks due today')%self.__nrDueToday
        return '%s - %s'%(meta.name, nrTasksText)

    def __getBitmap(self):
        if self.__tracking:
            self.__alternateTrackingBitmap()
        else:
            self.__bitmap = self.__defaultBitmap
        return self.__bitmap
            
    def __alternateTrackingBitmap(self):
        if self.__bitmap == self.__tickBitmap:
            self.__bitmap = self.__tackBitmap
        else:
            self.__bitmap = self.__tickBitmap
        
    def __setIcon(self):
        bitmap = self.__getBitmap()
        tooltipText = self.__getTooltipText()
        self.SetIcon(wx.ArtProvider_GetIcon(bitmap, wx.ART_FRAME_ICON, (16, 16)), 
            tooltipText)
        
