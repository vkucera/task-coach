import meta
import wx

class TaskBarIcon(wx.TaskBarIcon):
    def __init__(self, mainwindow, taskList):
        super(TaskBarIcon, self).__init__()
        self.taskList = taskList
        taskList.registerObserver(self.notify, self.notify, self.notify)
        self.notify()
        wx.EVT_TASKBAR_LEFT_DCLICK(self, mainwindow.restore)

    def setPopupMenu(self, menu):
        wx.EVT_TASKBAR_RIGHT_UP(self, self.popupTaskBarMenu)
        self.popupmenu = menu

    def popupTaskBarMenu(self, event):
        self.PopupMenu(self.popupmenu)

    def createTooltipText(self, nrDueToday):
        if nrDueToday == 0:
            tasksDueText = 'No tasks'
        elif nrDueToday == 1:
            tasksDueText = 'One task'
        else:
            tasksDueText = '%d tasks'%nrDueToday
        return '%s - %s due today'%(meta.name, tasksDueText)

    def selectBitmap(self, taskList):
        bitmap = 'taskbar'
        if taskList.nrOverdue() > 0:
            bitmap += '_overdue'
        elif taskList.allCompleted():
            bitmap += '_completed'
        return bitmap

    def notify(self, *args, **kwargs):
        bitmap = self.selectBitmap(self.taskList)
        self._tooltip = self.createTooltipText(self.taskList.nrDueToday())
        self.SetIcon(wx.ArtProvider_GetIcon(bitmap, wx.ART_FRAME_ICON,
            (16, 16)), self._tooltip)

    def tooltip(self):
        return self._tooltip # would be better to ask TaskBarIcon, but
                             # there is no getter for the tooltip text
