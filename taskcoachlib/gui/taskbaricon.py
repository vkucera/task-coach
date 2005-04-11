import meta
import wx

        
class TaskBarIcon(wx.TaskBarIcon):
    def __init__(self, mainwindow, taskList, defaultBitmap='taskcoach', 
            tickBitmap='tick', tackBitmap='tack'):
        super(TaskBarIcon, self).__init__()
        self.__bitmap = self.__defaultBitmap = defaultBitmap
        self.__tickBitmap = tickBitmap
        self.__tackBitmap = tackBitmap       
        taskList.registerObserver(self.onNotifyTaskList)
        self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, mainwindow.restore)
        self.__tracking = False
        self.__nrDueToday = 0
        self.__bitmapTimer = wx.Timer(self, -1)
        self.Bind(wx.EVT_TIMER, self.onNotifyTimer, self.__bitmapTimer)
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
        
    def onNotifyTimer(self, *args, **kwargs):
        self.__setIcon()
        
    def tooltip(self):
        return self.__getTooltipText() 
        
    def __getTooltipText(self):
        if self.__nrDueToday == 0:
            tasksDueText = 'No tasks'
        elif self.__nrDueToday == 1:
            tasksDueText = 'One task'
        else:
            tasksDueText = '%d tasks'%self.__nrDueToday
        return '%s - %s due today'%(meta.name, tasksDueText)

    def __getBitmap(self):
        if self.__tracking:
            if self.__bitmapTimer.IsRunning():
                self.__alternateTrackingBitmap()
            else: 
                self.__startTrackingBitmap()
        else:
            self.__stopTrackingBitmap()
        return self.__bitmap

    def __stopTrackingBitmap(self):
        self.__bitmap = self.__defaultBitmap
        self.__bitmapTimer.Stop()
    
    def __startTrackingBitmap(self):
        self.__bitmap = self.__tickBitmap
        self.__bitmapTimer.Start(1000) # tick tack every second (1000ms)
        
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
        
