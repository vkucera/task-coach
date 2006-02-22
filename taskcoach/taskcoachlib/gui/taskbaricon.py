import meta, wx
from i18n import _
import domain.date as date
        
class TaskBarIcon(date.ClockObserver, wx.TaskBarIcon):
    def __init__(self, mainwindow, taskList, defaultBitmap='taskcoach', 
            tickBitmap='tick', tackBitmap='tack', *args, **kwargs):
        super(TaskBarIcon, self).__init__(*args, **kwargs)
        self.__bitmap = self.__defaultBitmap = defaultBitmap
        self.__tickBitmap = tickBitmap
        self.__tackBitmap = tackBitmap
        self.__iconSize = self.__determineIconSize()
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
        if taskList.nrBeingTracked() > 0 and not self.isClockStarted():
            self.startClock()
        elif taskList.nrBeingTracked() == 0 and self.isClockStarted():
            self.stopClock()
            self.__setIcon()
        self.__nrDueToday = taskList.nrDueToday()
    
    def onEverySecond(self, *args, **kwargs):
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
        if self.isClockStarted():
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
        self.SetIcon(wx.ArtProvider_GetIcon(bitmap, wx.ART_FRAME_ICON, 
            self.__iconSize), tooltipText)

    def __determineIconSize(self):
        if '__WXMAC__' in wx.PlatformInfo:
            return (128, 128)
        else:
            return (16, 16)
    