import patterns, task, command, widgets, effort, uicommand
import menu, color, render, date
import wx
from i18n import _
import wx.grid as grid

class Viewer(patterns.Observable, wx.Panel):
    ''' A Viewer shows the contents of a model (a list of tasks or a list of 
        efforts) by means of a widget (e.g. a ListCtrl or a TreeListCtrl).'''
        
    def __init__(self, parent, list, uiCommands, settings=None, *args, **kwargs):
        # FIXME: Are settings still obtional?
        super(Viewer, self).__init__(parent, -1) # FIXME: Pass *args, **kwargs
        self.parent = parent # FIXME: Make instance variables private
        self.settings = settings
        self.uiCommands = uiCommands
        self.list = self.createSorter(self.createFilter(list))
        self.widget = self.createWidget()
        self.initLayout()
        self.list.registerObserver(self.onNotify)
        self.registerForColorChanges()
        self.onNotify(patterns.observer.Notification(self.list, itemsAdded=self.list))

    def initLayout(self):
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self._sizer.Add(self.widget, 1, wx.EXPAND)
        self.SetSizerAndFit(self._sizer)

    def registerForColorChanges(self):
        colorSettings = [('color', setting) for setting in 'activetasks',\
            'inactivetasks', 'completedtasks', 'duetodaytasks', 'overduetasks']
        self.settings.registerObserver(self.onColorChange, *colorSettings)
    
    def onColorChange(self, *args, **kwargs):
        self.refresh()
        
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
        if notification:
            if not notification.itemsAdded and not notification.itemsRemoved and not notification.orderChanged:
                for item in notification.itemsChanged:
                    self.widget.refreshItem(self.list.index(item))
            else:
                self.refresh()
        
    def onSelect(self, *args):
        self.notifyObservers(patterns.observer.Notification(self))
    
    def refresh(self):
        self.widget.refresh(len(self.list))
        
    def curselection(self):
        return [self.list[index] for index in self.widget.curselection()]
        
    def size(self):
        return self.widget.GetItemCount()

    def getItemAttr(self, index):
        task = self.list[index]
        return wx.ListItemAttr(color.taskColor(task, self.settings))

    def model(self):
        return self.list
    

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
        
        
class ViewerWithColumns(Viewer):
    def columns(self):
        return self._columns
    
    

class TaskViewer(Viewer):
    def isShowingTasks(self): # FIXME: can be removed?
        return True

    def isShowingEffort(self): # FIXME: can be removed?
        return False
   
    def statusMessages(self):
        status1 = _('Tasks: %d selected, %d visible, %d total')%\
            (len(self.curselection()), len(self.list), 
             self.list.originalLength())         
        status2 = _('Status: %d over due, %d inactive, %d completed')% \
            (self.list.nrOverdue(), self.list.nrInactive(),
             self.list.nrCompleted())
        return status1, status2
 
    def createTaskPopupMenu(self):
        return menu.TaskPopupMenu(self.parent, self.uiCommands)
        

class TaskViewerWithColumns(TaskViewer, ViewerWithColumns):
    def __init__(self, *args, **kwargs):
        super(TaskViewerWithColumns, self).__init__(*args, **kwargs)
        self.initColumns()
        self.settings.registerObserver(self.onSortKeyChanged, 
            ('view', 'sortby'))
        self.settings.registerObserver(self.onSortOrderChanged, 
            ('view', 'sortascending'))
            
    def _createColumns(self):
        return [widgets.Column(_('Subject'), None, 'subject', self.uiCommands['viewsortbysubject'])] + \
            [widgets.Column(columnHeader, ('view', setting), setting, self.uiCommands['viewsortby' + setting], renderCallback) for \
            columnHeader, setting, renderCallback in \
            (_('Start date'), 'startdate', lambda task: render.date(task.startDate())),
            (_('Due date'), 'duedate', lambda task: render.date(task.dueDate())),
            (_('Days left'), 'timeleft', lambda task: render.daysLeft(task.timeLeft())),
            (_('Completion date'), 'completiondate', lambda task: render.date(task.completionDate())),
            (_('Budget'), 'budget', lambda task: render.budget(task.budget())),
            (_('Total budget'), 'totalbudget', lambda task: render.budget(task.budget(recursive=True))),
            (_('Time spent'), 'timespent', lambda task: render.timeSpent(task.timeSpent())),
            (_('Total time spent'), 'totaltimespent', lambda task: render.timeSpent(task.timeSpent(recursive=True))),
            (_('Budget left'), 'budgetleft', lambda task: render.budget(task.budgetLeft())),
            (_('Total budget left'), 'totalbudgetleft', lambda task: render.budget(task.budgetLeft(recursive=True))),
            (_('Priority'), 'priority', lambda task: render.priority(task.priority())),
            (_('Overall priority'), 'totalpriority', lambda task: render.priority(task.priority(recursive=True))),
            (_('Hourly fee'), 'hourlyfee', lambda task: render.amount(task.hourlyFee())),
            (_('Fixed fee'), 'fixedfee', lambda task: render.amount(task.fixedFee())),
            (_('Total fixed fee'), 'totalfixedfee', lambda task: render.amount(task.fixedFee(recursive=True))),
            (_('Revenue'), 'revenue', lambda task: render.amount(task.revenue())),
            (_('Total revenue'), 'totalrevenue', lambda task: render.amount(task.revenue(recursive=True))),
            (_('Last modification time'), 'lastmodificationtime', lambda task: render.dateTime(task.lastModificationTime())),
            (_('Overall last modification time'), 'totallastmodificationtime', lambda task: render.dateTime(task.lastModificationTime(recursive=True)))]

    def initColumns(self):
        for column in self.columns():
            visibilitySetting = column.visibilitySetting()
            if visibilitySetting:
                self.settings.registerObserver(self.onShowColumn, 
                    visibilitySetting)
                self.widget.showColumn(column.header(), 
                    show=self.settings.getboolean(*column.visibilitySetting()))
            if self.settings.get('view', 'sortby') == column.sortKey():
                self.widget.showSortColumn(column.header())
                self.showSortOrder(self.settings.getboolean('view',
                    'sortascending'))
        
    def onShowColumn(self, notification):
        visibilitySetting = notification.section, notification.option
        for column in self.columns():
            if column.visibilitySetting() == visibilitySetting:
                self.widget.showColumn(column.header(), notification.value=='True')
                break

    def onSortKeyChanged(self, notification):
        sortKey = notification.value
        for column in self.columns():
            if column.sortKey() == sortKey:
                self.widget.showSortColumn(column.header())
                break
        
    def onSortOrderChanged(self, notification):
        self.showSortOrder(notification.value == 'True')

    def showSortOrder(self, ascending):
        if ascending:
            sortOrder = 'ascending'
        else:
            sortOrder = 'descending'
        self.widget.showSortOrder(self.imageIndex[sortOrder])
    
    def getItemText(self, index, column=None):
        task = self.list[index]
        # FIXME: When in a TaskTreeListViewer we need the subject non-recursively 
        # (e.g., 'task') when in a TaskListViewer we need the subject recursively
        # (e.g. 'parent -> task'. However, the following 5 lines depend on the fact 
        # that getItemText is currently called *with* the column argument from
        # a TreeCtrl and *without* the column from a TreeListCtrl.
        if not column:
            column = self.columns()[0]
            recursively = False
        else:
            recursively = True
        if column == self.columns()[0]:
            return render.subject(task, recursively=recursively)
        else:
            return column.render(task)
                
    def createColumnPopupMenu(self):
        return menu.TaskViewerColumnPopupMenu(self.parent, self.uiCommands)

    

class TaskListViewer(TaskViewerWithColumns, ListViewer):
    def createWidget(self):
        self._columns = self._createColumns()
        widget = widgets.ListCtrl(self, self.columns(),
            self.getItemText, self.getItemImage, self.getItemAttr, 
            self.onSelect, self.uiCommands['edit'], 
            self.createTaskPopupMenu(),
            self.createColumnPopupMenu())
        widget.AssignImageList(self.createImageList(), wx.IMAGE_LIST_SMALL)
        return widget
        
    def createFilter(self, taskList):
        return task.filter.CompositeFilter(task.filter.ViewFilter(taskList, 
            settings=self.settings), settings=self.settings)
        
    def createSorter(self, taskList):
        return task.sorter.Sorter(taskList, settings=self.settings, treeMode=False)
    
    def setViewCompositeTasks(self, viewCompositeTasks):
        self.list.setViewCompositeTasks(viewCompositeTasks)


class TaskTreeViewer(TaskViewer, TreeViewer):
    def createWidget(self):
        widget = widgets.TreeCtrl(self, self.getItemText, self.getItemImage, 
            self.getItemAttr, self.getItemId, self.getRootIndices, self.getChildIndices,
            self.onSelect, self.uiCommands['edit'], self.createTaskPopupMenu())
        widget.AssignImageList(self.createImageList())
        return widget
    
    def createFilter(self, taskList):
        return task.filter.ViewFilter(taskList, settings=self.settings, treeMode=True)
        
    def createSorter(self, taskList):
        return task.sorter.Sorter(taskList, settings=self.settings, treeMode=True)
    
    def getItemText(self, index):
        task = self.list[index]
        return task.subject()
    
    def getItemImage(self, index):
        task = self.list[index]
        return self.getImageIndices(task) 
        
    def getItemChildIndex(self, index):
        task = self.list[index]
        if task.parent():
            parentIndex = self.list.index(task.parent())
            childrenBeforeThisTask = [child for child in self.list[parentIndex+1:index] if task.parent() == child.parent()]
            return len(childrenBeforeThisTask)
        else:
            return len([child for child in self.list[:index] if child.parent() is None])
                   
    def getItemId(self, index):
        task = self.list[index]
        return task.id()

    def getRootIndices(self):
        return [self.list.index(task) for task in self.list.rootTasks()]
        
    def getChildIndices(self, index):
        task = self.list[index]
        childIndices = [self.list.index(child) for child in task.children() if child in self.list]
        childIndices.sort()
        return childIndices


class TaskTreeListViewer(TaskViewerWithColumns, TaskTreeViewer):
    def createWidget(self):
        self._columns = self._createColumns()
        widget = widgets.TreeListCtrl(self, self.columns(), self.getItemText,
            self.getItemImage, self.getItemAttr, self.getItemId, self.getRootIndices,
            self.getChildIndices, self.onSelect, self.uiCommands['edit'],
            self.createTaskPopupMenu(), self.createColumnPopupMenu())
        widget.AssignImageList(self.createImageList())
        return widget    


class EffortViewer(Viewer):
    def isShowingTasks(self):
        return False
        
    def isShowingEffort(self):
        return True

    def statusMessages(self):
        status1 = _('Effort: %d selected, %d visible, %d total')%\
            (len(self.curselection()), len(self.list), 
             self.list.originalLength())         
        status2 = _('Status: %d tracking')% self.list.nrBeingTracked()
        return status1, status2
 
    
class EffortListViewer(ListViewer, EffortViewer, ViewerWithColumns):
    def __init__(self, *args, **kwargs):
        self.taskList = kwargs.pop('taskList')
        super(EffortListViewer, self).__init__(*args, **kwargs)
        
    def createWidget(self):
        # We need to create new uiCommands here, because the viewer might not
        # be the effort viewer in the mainwindow, but the effort viewer in the 
        # task edit window.
        uiCommands = {}
        uiCommands.update(self.uiCommands)
        uiCommands['editeffort'] = uicommand.EffortEdit(mainwindow=self.parent, effortList=self.list, filteredTaskList=self.taskList, viewer=self, uiCommands=self.uiCommands)
        uiCommands['deleteeffort'] = uicommand.EffortDelete(effortList=self.list, viewer=self, filteredTaskList=self.taskList)
        uiCommands['cut'] = uicommand.EditCut(viewer=self)
        uiCommands['copy'] = uicommand.EditCopy(viewer=self)
        uiCommands['pasteintotask'] = uicommand.EditPasteIntoTask(viewer=self)
        
        self._columns = self._createColumns()
        widget = widgets.ListCtrl(self, self.columns(),
            self.getItemText, self.getItemImage, self.getItemAttr,
            self.onSelect, uiCommands['editeffort'], 
            menu.EffortPopupMenu(self.parent, uiCommands), resizeableColumn=2)
        widget.SetColumnWidth(0, 150)
        return widget
    
    def _createColumns(self):
        return [widgets.Column(columnHeader, None, None) for columnHeader in (_('Period'), _('Task'), _('Time spent'), _('Revenue'))]
        
    def createSorter(self, effortList):
        return effort.EffortSorter(effortList)
        
    def getItemText(self, index, column):
        effort = self.list[index]
        if column.header() == _('Period'):
            previousEffort = index > 0 and self.list[index-1] or None
            return self.renderPeriod(effort, previousEffort)
        elif column.header() == _('Task'):
            return render.subject(effort.task(), recursively=True)
        elif column.header() == _('Time spent'):
            return render.timeSpent(effort.duration())
        elif column.header() == _('Revenue'):
            return render.amount(effort.revenue())
    
    def getItemImage(self, index):
        return -1
    
    def getItemAttr(self, index):
        return wx.ListItemAttr()
                
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
    def _createColumns(self):
        return super(CompositeEffortListViewer, self)._createColumns() + \
            [widgets.Column(columnHeader, None, None) for columnHeader in (_('Total time spent'), _('Total revenue'))]
        
    def curselection(self):
        compositeEfforts = super(CompositeEffortListViewer, self).curselection()
        return [effort for compositeEffort in compositeEfforts for effort in compositeEffort]

    def getItemText(self, index, column):
        effort = self.list[index]
        if column.header() == _('Total time spent'):
            return render.timeSpent(effort.duration(recursive=True))
        elif column.header() == _('Total revenue'):
            return render.amount(effort.revenue(recursive=True))
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


class Table(grid.PyGridTableBase):
    def __init__(self, taskList, *args, **kwargs):
        self._taskList = taskList
        super(Table, self).__init__(*args, **kwargs)
        
    def GetRowLabelValue(self, row):
        return self._taskList[row].subject()

    def GetColLabelValue(self, col):
        return render.date(self.__minDate() + date.TimeDelta(days=col))
        
    def GetNumberRows(self):
        return len(self._taskList)

    def __minDate(self):
        minDate = self._taskList.minDate()
        if minDate == date.Date():
            minDate = date.Today()
        if minDate == date.minimumDate:
            return minDate
        else:
            return minDate - date.TimeDelta(days=1)
        
    def __maxDate(self):
        maxDate = self._taskList.maxDate()
        if maxDate == date.Date():
            maxDate = date.Today() 
        return maxDate + date.TimeDelta(days=1)
        
    def GetNumberCols(self):
        period = self.__maxDate() - self.__minDate() + date.TimeDelta(days=1)
        return period.days
       
    def IsEmptyCell(self, row, col):
        True
        
    def GetValue(self, row, col):
        return ''

    def GetAttr(self, row, col, *args):
        attr = grid.GridCellAttr()
        if not self.__emptyCell(row, col):
            task = self._taskList[row]
            attr.SetBackgroundColour(color.taskColor(task, active=wx.BLUE))
        return attr
       
    def __emptyCell(self, row, col):
        if row >= len(self._taskList):
            return True
        task = self._taskList[row]
        thisDate = self.__minDate() + date.TimeDelta(days=col)
        taskDates = [task.startDate()]
        if task.completed():
            taskDates.append(task.completionDate())
        else:
            taskDates.append(task.dueDate())
        return thisDate < min(taskDates) or thisDate > max(taskDates)
 

class GanttChartViewer(TaskViewer):
    def createWidget(self):
        self.table = Table(self.list)
        widget = widgets.GridCtrl(self, self.table, self.onSelect, self.uiCommands['edit'])
        return widget
