import patterns, task, command, widgets, effort, uicommand
import menu, color, render
import wx

class Viewer(patterns.Observable, wx.Panel):
    def __init__(self, parent, list, uiCommands, *args, **kwargs):
        super(Viewer, self).__init__(parent, -1)
        self.parent = parent
        self.uiCommands = uiCommands
        self.list = self.createSorter(list)
        self.list.registerObserver(self.onNotify)
        self.widget = self.createWidget()
        self.initLayout()
        self.onNotify(patterns.observer.Notification(self.list, itemsAdded=self.list))

    def initLayout(self):
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self._sizer.Add(self.widget, 1, wx.EXPAND)
        self.SetSizerAndFit(self._sizer)

    def __getattr__(self, attr):
        return getattr(self.widget, attr)
        
    def createWidget(self, *args):
        raise NotImplementedError

    def createImageList(self):
        imageList = wx.ImageList(16, 16)
        self.imageIndex = {}
        for index, image in enumerate(['task', 'task_inactive', 'task_completed', 
            'task_duetoday', 'task_overdue', 'tasks', 'tasks_open', 
            'tasks_inactive', 'tasks_inactive_open', 'tasks_completed', 
            'tasks_completed_open', 'tasks_duetoday', 'tasks_duetoday_open', 
            'tasks_overdue', 'tasks_overdue_open', 'start']):
            imageList.Add(wx.ArtProvider_GetBitmap(image, wx.ART_MENU, (16,16)))
            self.imageIndex[image] = index
        return imageList

    def getImageIndices(self, task):
        bitmap = 'task'
        if task.children():
            bitmap += 's'
        if task.completed():
            bitmap += '_completed'
        elif task.overdue():
            bitmap += '_overdue'
        elif task.dueToday():
            bitmap += '_duetoday'
        elif task.inactive():
            bitmap += '_inactive'
        if task.children():
            bitmap_selected = bitmap + '_open'
        else:
            bitmap_selected = bitmap
        if task.isBeingTracked():
            bitmap = bitmap_selected = 'start'
        return self.imageIndex[bitmap], self.imageIndex[bitmap_selected]
 
    def createSorter(self, *args):
        raise NotImplementedError

    def onNotify(self, notification, *args, **kwargs):
        if notification.itemsAdded or notification.itemsChanged or notification.itemsRemoved:
            self.widget.refresh(len(self.list))
            self.notifyObservers(patterns.observer.Notification(self))
        
    def onSelect(self, *args):
        self.notifyObservers(patterns.observer.Notification(self))

    def curselection(self):
        return [self.list[index] for index in self.widget.curselection()]
        
    def size(self):
        return self.widget.GetItemCount()

    def select(self, items):
        indices = [self.list.index(item) for item in items if item in self.list]
        self.widget.select(indices)

    def focus_set(self):
        self.widget.SetFocus()

    def canHideColumns(self):
        return hasattr(self, 'showColumn')

    def getItemAttr(self, index):
        task = self.list[index]
        return wx.ListItemAttr(color.taskColor(task))


class ListViewer(Viewer):
    def getItemImage(self, index):
        task = self.list[index]
        normalImageIndex, expandedImageIndex = self.getImageIndices(task) 
        if task.children():
            return expandedImageIndex
        else:
            return normalImageIndex


class TaskViewer(Viewer):
    def select_completedTasks(self):
        self.select([task for task in self.list if task.completed()])

    def isShowingTasks(self):
        return True

    def isShowingEffort(self):
        return False

    
class TaskListViewer(TaskViewer, ListViewer):
    def createWidget(self):
        widget = widgets.ListCtrl(self, ['Subject', 'Start date', 'Due date',
            'Days left', 'Completion date', 'Time spent', 'Total time spent'],
            self.getItemText, self.getItemImage, self.getItemAttr, 
            self.onSelect, self.uiCommands['edit'], 
            menu.TaskPopupMenu(self.parent, self.uiCommands))
        widget.AssignImageList(self.createImageList(), wx.IMAGE_LIST_SMALL)
        return widget

    def createSorter(self, taskList):
        return task.sorter.Sorter(taskList)
    
    def getItemText(self, index, column):
        if self.widget.GetColumnWidth(column) == 0:
            return ''
        task = self.list[index]
        if column == 0:
            return render.subject(task, recursively=True)
        elif column == 1:
            return render.date(task.startDate())
        elif column == 2:
            return render.date(task.dueDate())
        elif column == 3:
            return render.daysLeft(task.timeLeft())
        elif column == 4:
            return render.date(task.completionDate())
        elif column == 5:
            return render.timeSpent(task.duration())
        elif column == 6:
            return render.timeSpent(task.duration(recursive=True))
    
    def showColumn(self, columnIndex, show):
        width = {True : wx.LIST_AUTOSIZE, False : 0 } [show]
        self.widget.SetColumnWidth(columnIndex, width)

    def showStartDate(self, show):
        self.showColumn(1, show)

    def showDueDate(self, show):
        self.showColumn(2, show)
        
    def showDaysLeft(self, show):
        self.showColumn(3, show)

    def showCompletionDate(self, show):
        self.showColumn(4, show)

    def showTimeSpent(self, show):
        self.showColumn(5, show)

    def showTotalTimeSpent(self, show):
        self.showColumn(6, show)


class TaskTreeViewer(TaskViewer):
    def createWidget(self):
        widget = widgets.TreeCtrl(self, self.getItemText, self.getItemImage, 
            self.getItemAttr, self.getItemChildrenCount, 
            self.getItemFingerprint, self.onSelect, self.uiCommands['edit'], 
            menu.TaskPopupMenu(self.parent, self.uiCommands))
        widget.AssignImageList(self.createImageList())
        return widget

    def createSorter(self, taskList):
        return task.sorter.DepthFirstSorter(taskList) 
    
    def getItemText(self, index):
        task = self.list[index]
        return task.subject()
    
    def getItemImage(self, index):
        task = self.list[index]
        return self.getImageIndices(task) 
    
    def getItemChildrenCount(self, index):
        task = self.list[index]
        return len([task for task in task.children() if task in self.list])
        
    def getItemFingerprint(self, index):
        ''' A fingerprint can be used to detect changes in a task: if a task
        changes, its fingerprint will be different. What exactly is considered
        to be a change is entirely determined by the needs of the TaskTreeCtrl.
        The TaskTreeCtrl needs to be able to see whether a task has changed in 
        order to determine what parts of the tree need updating. '''
        task = self.list[index]
        fingerprint = {}
        fingerprint['subject'] = task.subject()
        fingerprint['children'] = len(task.children()) > 0
        fingerprint['startdate'] = task.startDate()
        fingerprint['duedate'] = task.dueDate()
        fingerprint['completiondate'] = task.completionDate()
        fingerprint['parent'] = task.parent()
        fingerprint['active'] = task.isBeingTracked()
        return fingerprint


class EffortListViewer(ListViewer):  
    def __init__(self, parent, effortList, uiCommands, *args, **kwargs):
        super(EffortListViewer, self).__init__(parent, effortList,
            uiCommands, *args, **kwargs)

    def createWidget(self):
        uiCommands = {}
        uiCommands.update(self.uiCommands)
        uiCommands['editeffort'] = uicommand.EffortEdit(self.parent, self.list, self, self.uiCommands)
        uiCommands['deleteeffort'] = uicommand.EffortDelete(self.list, self)
        widget = widgets.EffortListCtrl(self, self.columns(),
            self.getItemText, self.getItemImage, self.getItemAttr,
            self.onSelect, uiCommands['editeffort'], 
            menu.EffortPopupMenu(self.parent, uiCommands, self.list, self))
        widget.SetColumnWidth(0, 150)
        widget.SetColumnWidth(1, 300)
        return widget

    def columns(self):
        return ['Period', 'Task', 'Time spent']
        
    def createSorter(self, effortList):
        return effort.EffortSorter(effortList)
        
    def getItemText(self, index, column):
        effort = self.list[index]
        if column == 0:
            previousEffort = index > 0 and self.list[index-1] or None
            return self.renderPeriod(effort, previousEffort)
        elif column == 1:
            return render.subject(effort.task(), recursively=True)
        elif column == 2:
            return render.timeSpent(effort.duration())

    def _getTask(self, index):
        return self.list[index].task()
    
    def getItemImage(self, index):
        return -1
    
    def getItemAttr(self, index):
        return wx.ListItemAttr()
                
    def isShowingTasks(self):
        return False
        
    def isShowingEffort(self):
        return True

    def renderPeriod(self, effort, previousEffort=None):
        if previousEffort and effort.getStart() == previousEffort.getStart():
            return self.renderRepeatedPeriod(effort)
        else:
            return self.renderEntirePeriod(effort)

    def renderRepeatedPeriod(self, effort):
        return ''
        
    def renderEntirePeriod(self, effort):
        return render.dateTimePeriod(effort.getStart(), effort.getStop())


class CompositeEffortListViewer(EffortListViewer):
    def columns(self):
        return super(CompositeEffortListViewer, self).columns() + ['Total time spent']
        
    def curselection(self):
        compositeEfforts = super(CompositeEffortListViewer, self).curselection()
        return [effort for compositeEffort in compositeEfforts for effort in compositeEffort]

    def getItemText(self, index, column):
        if column == 3:
            effort = self.list[index]
            return render.timeSpent(effort.duration(recursive=True))
        else:
            return super(CompositeEffortListViewer, self).getItemText(index, column)


class EffortPerDayViewer(CompositeEffortListViewer):
    def createSorter(self, effortList):
        return effort.EffortSorter(effort.EffortPerDay(effortList))
    
    def renderEntirePeriod(self, compositeEffort):
        return render.date(compositeEffort.getStart().date())
    
        
class EffortPerWeekViewer(CompositeEffortListViewer):
    def createSorter(self, effortList):
        return effort.EffortSorter(effort.EffortPerWeek(effortList))
        
    def renderEntirePeriod(self, compositeEffort):
        return render.weekNumber(compositeEffort.getStart())


class EffortPerMonthViewer(CompositeEffortListViewer):
    def createSorter(self, effortList):
        return effort.EffortSorter(effort.EffortPerMonth(effortList))
        
    def renderEntirePeriod(self, compositeEffort):
        return render.month(compositeEffort.getStart())

