import patterns, task, command, widgets, effort, uicommand
import menu, color, render
import wx
from i18n import _

class Viewer(patterns.Observable, wx.Panel):
    def __init__(self, parent, list, uiCommands, settings=None, *args, **kwargs):
        super(Viewer, self).__init__(parent, -1)
        self.parent = parent
        self.settings = settings
        self.uiCommands = uiCommands
        self.list = self.createSorter(self.createFilter(list))
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
            'tasks_overdue', 'tasks_overdue_open', 'start', 'ascending', 'descending']):
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
 
    def createSorter(self, list):
        return list
        
    def createFilter(self, list):
        return list

    def onNotify(self, notification, *args, **kwargs):
        if notification.itemsAdded or notification.itemsChanged or notification.itemsRemoved:
            if notification.itemsAdded and len(notification.itemsAdded) < len(self.list):
                selection = notification.itemsAdded
            elif notification.itemsChanged and len(notification.itemsChanged) < len(self.list):
                selection = notification.itemsChanged
            else:
                selection = []
            self.widget.refresh(len(self.list))
            self.select(selection)
        
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


class TreeViewer(Viewer):
    def expandAll(self):
        self.widget.expandAllItems()

    def collapseAll(self):
        self.widget.collapseAllItems()
        
    def expandSelected(self):
        self.widget.expandSelectedItems()
        
    def collapseSelected(self):
        self.widget.collapseSelectedItems()
        

class TaskViewer(Viewer):
    def isShowingTasks(self): # FIXME: can be removed?
        return True

    def isShowingEffort(self): # FIXME: can be removed?
        return False
    
    
class TaskListViewer(TaskViewer, ListViewer):
    def createWidget(self):
        widget = widgets.ListCtrl(self, self.columns(),
            self.getItemText, self.getItemImage, self.getItemAttr, 
            self.onSelect, self.uiCommands['edit'], 
            menu.TaskPopupMenu(self.parent, self.uiCommands),
            menu.TaskListViewerColumnPopupMenu(self.parent, self.uiCommands),
            [self.uiCommands['viewsortbysubject'], 
                self.uiCommands['viewsortbystartdate'], 
                self.uiCommands['viewsortbyduedate'],
                self.uiCommands['viewsortbydaysleft'],
                self.uiCommands['viewsortbycompletiondate'],
                self.uiCommands['viewsortbybudget'],
                self.uiCommands['viewsortbytotalbudget'],
                self.uiCommands['viewsortbytimespent'],
                self.uiCommands['viewsortbytotaltimespent'],
                self.uiCommands['viewsortbybudgetleft'],
                self.uiCommands['viewsortbytotalbudgetleft']])
        widget.AssignImageList(self.createImageList(), wx.IMAGE_LIST_SMALL)
        return widget
        
    def columns(self):
        return [_('Subject'), _('Start date'), _('Due date'),
            _('Days left'), _('Completion date'), _('Budget'), 
            _('Total budget'), _('Time spent'), _('Total time spent'), 
            _('Budget left'), _('Total budget left')]
       
    def createFilter(self, taskList):
        return task.filter.CompositeFilter(taskList)
        
    def setViewCompositeTasks(self, viewCompositeTasks):
        self.list.setViewCompositeTasks(viewCompositeTasks)
    
    def getItemText(self, index, columnHeader):
        task = self.list[index]
        if columnHeader == _('Subject'):
            return render.subject(task, recursively=True)
        elif columnHeader == _('Start date'):
            return render.date(task.startDate())
        elif columnHeader == _('Due date'):
            return render.date(task.dueDate())
        elif columnHeader == _('Days left'):
            return render.daysLeft(task.timeLeft())
        elif columnHeader == _('Completion date'):
            return render.date(task.completionDate())
        elif columnHeader == _('Budget'):
            return render.budget(task.budget())
        elif columnHeader == _('Total budget'):
            return render.budget(task.budget(recursive=True))
        elif columnHeader == _('Time spent'):
            return render.timeSpent(task.timeSpent())
        elif columnHeader == _('Total time spent'):
            return render.timeSpent(task.timeSpent(recursive=True))
        elif columnHeader == _('Budget left'):
            return render.budget(task.budgetLeft())
        elif columnHeader == _('Total budget left'):
            return render.budget(task.budgetLeft(recursive=True))
    
    def showColumn(self, columnHeader, show):
        self.widget.showColumn(columnHeader, show)

    def onNotify(self, *args, **kwargs):
        sortKey = self.list.getSortKey()
        columnHeader = {'subject': _('Subject'), 'startDate': _('Start date'),
            'dueDate': _('Due date'), 'timeLeft': _('Days left'),
            'completionDate': _('Completion date'), 'budget': _('Budget'),
            'totalbudget': _('Total budget'), 'timeSpent': _('Time spent'),
            'totaltimeSpent': _('Total time spent'), 'budgetLeft': _('Budget left'),
            'totalbudgetLeft': _('Total budget left')}[sortKey]
        if self.list.isAscending():
            imageIndex = self.imageIndex['ascending']
        else:
            imageIndex = self.imageIndex['descending']
        self.widget.showSort(columnHeader, imageIndex)
        super(TaskListViewer, self).onNotify(*args, **kwargs)


class TaskTreeViewer(TaskViewer, TreeViewer):
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
        fingerprint['id'] = task.id()
        fingerprint['children'] = len(task.children()) > 0
        fingerprint['startdate'] = task.startDate()
        fingerprint['duedate'] = task.dueDate()
        fingerprint['completiondate'] = task.completionDate()
        fingerprint['parent'] = task.parent()
        fingerprint['active'] = task.isBeingTracked()
        fingerprint['index'] = index
        return fingerprint


class EffortListViewer(ListViewer):  
    def createWidget(self):
        uiCommands = {}
        uiCommands.update(self.uiCommands)
        uiCommands['editeffort'] = uicommand.EffortEdit(self.parent, self.list, self, self.uiCommands)
        uiCommands['deleteeffort'] = uicommand.EffortDelete(self.list, self)
        widget = widgets.EffortListCtrl(self, self.columns(),
            self.getItemText, self.getItemImage, self.getItemAttr,
            self.onSelect, uiCommands['editeffort'], 
            menu.EffortPopupMenu(self.parent, uiCommands))
        widget.SetColumnWidth(0, 150)
        return widget

    def columns(self):
        return [_('Period'), _('Task'), _('Time spent')]
        
    def createSorter(self, effortList):
        return effort.EffortSorter(effortList)
        
    def getItemText(self, index, columnHeader):
        effort = self.list[index]
        if columnHeader == _('Period'):
            previousEffort = index > 0 and self.list[index-1] or None
            return self.renderPeriod(effort, previousEffort)
        elif columnHeader == _('Task'):
            return render.subject(effort.task(), recursively=True)
        elif columnHeader == _('Time spent'):
            return render.timeSpent(effort.duration())
    
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

    def showColumn(self, *args, **kwargs):
        raise AttributeError # not implemented yet
        

class CompositeEffortListViewer(EffortListViewer):
    def columns(self):
        return super(CompositeEffortListViewer, self).columns() + [_('Total time spent')]
        
    def curselection(self):
        compositeEfforts = super(CompositeEffortListViewer, self).curselection()
        return [effort for compositeEffort in compositeEfforts for effort in compositeEffort]

    def getItemText(self, index, columnHeader):
        if columnHeader == _('Total time spent'):
            effort = self.list[index]
            return render.timeSpent(effort.duration(recursive=True))
        else:
            return super(CompositeEffortListViewer, self).getItemText(index, columnHeader)


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

