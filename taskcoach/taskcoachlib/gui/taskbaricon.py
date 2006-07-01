import meta, wx
from i18n import _
import domain.date as date
        
class TaskBarIcon(date.ClockObserver, wx.TaskBarIcon):
    def __init__(self, mainwindow, taskList, defaultBitmap='taskcoach', 
            tickBitmap='tick', tackBitmap='tack', *args, **kwargs):
        super(TaskBarIcon, self).__init__(*args, **kwargs)
        self.__taskList = taskList
        self.__bitmap = self.__defaultBitmap = defaultBitmap
        self.__tickBitmap = tickBitmap
        self.__tackBitmap = tackBitmap
        self.__iconSize = self.__determineIconSize()
        self.__taskList.registerObserver(self.onAddItem, 'list.add')
        self.__taskList.registerObserver(self.onRemoveItem, 'list.remove')
        self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, mainwindow.restore)
        self.__setTooltipText()

    # Event handlers:

    def onAddItem(self, event):
        for task in event.values():
            task.registerObserver(self.onStartTracking, 'task.track.start')
            task.registerObserver(self.onStopTracking, 'task.track.stop')
            task.registerObserver(self.onChangeDueDate, 'task.dueDate')
        self.__setTooltipText()
        self.__startTicking()
        
    def onRemoveItem(self, event):
        for task in event.values():
            task.removeObservers(self.onStartTracking,
                self.onStopTracking, self.onChangeDueDate)
        self.__setTooltipText()
        self.__stopTicking()

    def onStartTracking(self, event):
        self.__startTicking()

    def onStopTracking(self, event):
        self.__stopTicking()

    def onChangeDueDate(self, event):
        self.__setTooltipText()
        self.__setIcon()

    def onEverySecond(self, *args, **kwargs):
        self.__toggleTrackingBitmap()
        self.__setIcon()

    # Menu:

    def setPopupMenu(self, menu):
        self.Bind(wx.EVT_TASKBAR_RIGHT_UP, self.popupTaskBarMenu)
        self.popupmenu = menu

    def popupTaskBarMenu(self, event):
        self.PopupMenu(self.popupmenu)

    # Getters:

    def tooltip(self):
        return self.__tooltipText
        
    def bitmap(self):
        return self.__bitmap

    def defaultBitmap(self):
        return self.__defaultBitmap
            
    # Private methods:

    def __startTicking(self):
        if self.__taskList.nrBeingTracked() > 0 and not self.isClockStarted():
            self.startClock()
            self.__toggleTrackingBitmap()
            self.__setIcon()

    def __stopTicking(self):
        if self.__taskList.nrBeingTracked() == 0 and self.isClockStarted():
            self.stopClock()
            self.__setDefaultBitmap()
            self.__setIcon()

    def __setTooltipText(self):
        nrDueToday = self.__taskList.nrDueToday()
        if nrDueToday == 0:
            nrTasksText = _('No tasks due today')
        elif nrDueToday == 1:
            nrTasksText = _('One task due today')
        else:
            nrTasksText = _('%d tasks due today')%nrDueToday
        self.__tooltipText = '%s - %s'%(meta.name, nrTasksText)

    def __setDefaultBitmap(self):
        self.__bitmap = self.__defaultBitmap

    def __toggleTrackingBitmap(self):
        if self.__bitmap == self.__tickBitmap:
            self.__bitmap = self.__tackBitmap
        else:
            self.__bitmap = self.__tickBitmap

    def __setIcon(self):
        self.SetIcon(wx.ArtProvider_GetIcon(self.__bitmap, wx.ART_FRAME_ICON, 
            self.__iconSize), self.__tooltipText)

    def __determineIconSize(self):
        if '__WXMAC__' in wx.PlatformInfo:
            return (128, 128)
        else:
            return (16, 16)
    
