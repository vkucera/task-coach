'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>
Copyright (C) 2007-2008 Jerome Laheurte <fraca7@free.fr>
Copyright (C) 2008 Rob McMullen <rob.mcmullen@gmail.com>
Copyright (C) 2008 Thomas Sonne Olesen <tpo@sonnet.dk>

Task Coach is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Task Coach is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import wx
from taskcoachlib import patterns, command, widgets, domain
from taskcoachlib.domain import task
from taskcoachlib.i18n import _
from taskcoachlib.gui import uicommand, menu, color, render, dialog
import base, mixin


class TaskViewer(mixin.AttachmentDropTarget, mixin.FilterableViewerForTasks, 
                 mixin.SortableViewerForTasks, mixin.SearchableViewer, 
                 base.UpdatePerSecondViewer, base.SortableViewerWithColumns,
                 base.TreeViewer):
    
    defaultTitle = _('Tasks')
    defaultBitmap = 'task'
    
    def __init__(self, *args, **kwargs):
        self.__sortKeyUnchangedCount = 0
        kwargs.setdefault('settingsSection', 'taskviewer')
        super(TaskViewer, self).__init__(*args, **kwargs)
        self.treeOrListUICommand.setChoice(self.isTreeViewer())
        self.__registerForColorChanges()

    def domainObjectsToView(self):
        return self.taskFile.tasks()
    
    def isShowingTasks(self): 
        return True
    
    def isTreeViewer(self):
        return self.settings.getboolean(self.settingsSection(), 'treemode')

    def createWidget(self):
        imageList = self.createImageList() # Has side-effects
        self._columns = self._createColumns()
        widget = widgets.TreeListCtrl(self, self.columns(), self.getItemText,
            self.getItemTooltipData, self.getItemImage, self.getItemAttr,
            self.getChildrenCount, self.getItemExpanded, self.onSelect, 
            uicommand.TaskEdit(taskList=self.presentation(), viewer=self),
            uicommand.TaskDragAndDrop(taskList=self.presentation(), viewer=self),
            self.createTaskPopupMenu(), self.createColumnPopupMenu(),
            **self.widgetCreationKeywordArguments())
        widget.AssignImageList(imageList)
        return widget    
    
    def _createColumns(self):
        kwargs = dict(renderDescriptionCallback=lambda task: task.description(),
                      resizeCallback=self.onResizeColumn)
        columns = [widgets.Column('subject', _('Subject'), 
                task.Task.subjectChangedEventType(), 
                'task.completionDate', 'task.dueDate', 'task.startDate',
                'task.track.start', 'task.track.stop', 
                sortCallback=uicommand.ViewerSortByCommand(viewer=self,
                    value='subject'),
                width=self.getColumnWidth('subject'), 
                imageIndexCallback=self.subjectImageIndex,
                renderCallback=self.renderSubject, **kwargs)] + \
            [widgets.Column('description', _('Description'), 
                task.Task.descriptionChangedEventType(), 
                sortCallback=uicommand.ViewerSortByCommand(viewer=self,
                    value='description'),
                renderCallback=lambda task: task.description(), 
                width=self.getColumnWidth('description'), **kwargs)] + \
            [widgets.Column('attachments', '', 
                task.Task.attachmentsChangedEventType(),
                width=self.getColumnWidth('attachments'),
                alignment=wx.LIST_FORMAT_LEFT,
                imageIndexCallback=self.attachmentImageIndex,
                headerImageIndex=self.imageIndex['attachment'],
                renderCallback=lambda task: '', **kwargs)]
        if self.settings.getboolean('feature', 'notes'):
            columns.append(widgets.Column('notes', '', 
                task.Task.notesChangedEventType(),
                width=self.getColumnWidth('notes'),
                alignment=wx.LIST_FORMAT_LEFT,
                imageIndexCallback=self.noteImageIndex,
                headerImageIndex=self.imageIndex['note'],
                renderCallback=lambda task: '', **kwargs))
        columns.extend(
            [widgets.Column('categories', _('Categories'), 
                task.Task.categoryAddedEventType(), 
                task.Task.categoryRemovedEventType(), 
                task.Task.categorySubjectChangedEventType(),
                sortCallback=uicommand.ViewerSortByCommand(viewer=self,
                                                           value='categories'),
                width=self.getColumnWidth('categories'),
                renderCallback=self.renderCategory, **kwargs)] + \
            [widgets.Column('totalCategories', _('Overall categories'),
                task.Task.totalCategoryAddedEventType(),
                task.Task.totalCategoryRemovedEventType(),
                task.Task.totalCategorySubjectChangedEventType(),
                sortCallback=uicommand.ViewerSortByCommand(viewer=self,
                                                           value='totalCategories'),
                renderCallback=lambda task: self.renderCategory(task, recursive=True),
                width=self.getColumnWidth('totalCategories'), **kwargs)])
        effortOn = self.settings.getboolean('feature', 'effort')
        dependsOnEffortFeature = ['budget', 'totalBudget', 
                                  'timeSpent', 'totalTimeSpent', 
                                  'budgetLeft', 'totalBudgetLeft',
                                  'hourlyFee', 'fixedFee', 'totalFixedFee',
                                  'revenue', 'totalRevenue']
        for name, columnHeader, renderCallback in [
            ('startDate', _('Start date'), lambda task: render.date(task.startDate())),
            ('dueDate', _('Due date'), lambda task: render.date(task.dueDate())),
            ('timeLeft', _('Days left'), lambda task: render.daysLeft(task.timeLeft(), task.completed())),
            ('completionDate', _('Completion date'), lambda task: render.date(task.completionDate())),
            ('recurrence', _('Recurrence'), lambda task: render.recurrence(task.recurrence())),
            ('budget', _('Budget'), lambda task: render.budget(task.budget())),
            ('totalBudget', _('Total budget'), lambda task: render.budget(task.budget(recursive=True))),
            ('timeSpent', _('Time spent'), lambda task: render.timeSpent(task.timeSpent())),
            ('totalTimeSpent', _('Total time spent'), lambda task: render.timeSpent(task.timeSpent(recursive=True))),
            ('budgetLeft', _('Budget left'), lambda task: render.budget(task.budgetLeft())),
            ('totalBudgetLeft', _('Total budget left'), lambda task: render.budget(task.budgetLeft(recursive=True))),
            ('priority', _('Priority'), lambda task: render.priority(task.priority())),
            ('totalPriority', _('Overall priority'), lambda task: render.priority(task.priority(recursive=True))),
            ('hourlyFee', _('Hourly fee'), lambda task: render.amount(task.hourlyFee())),
            ('fixedFee', _('Fixed fee'), lambda task: render.amount(task.fixedFee())),
            ('totalFixedFee', _('Total fixed fee'), lambda task: render.amount(task.fixedFee(recursive=True))),
            ('revenue', _('Revenue'), lambda task: render.amount(task.revenue())),
            ('totalRevenue', _('Total revenue'), lambda task: render.amount(task.revenue(recursive=True))),
            ('reminder', _('Reminder'), lambda task: render.dateTime(task.reminder()))]:
            if (name in dependsOnEffortFeature and effortOn) or name not in dependsOnEffortFeature:
                columns.append(widgets.Column(name, columnHeader, 'task.'+name, 
                    sortCallback=uicommand.ViewerSortByCommand(viewer=self, value=name),
                    renderCallback=renderCallback, width=self.getColumnWidth(name),
                    alignment=wx.LIST_FORMAT_RIGHT, **kwargs))
        return columns
    
    def createColumnUICommands(self):
        commands = [
            uicommand.ToggleAutoColumnResizing(viewer=self,
                                               settings=self.settings),
            None,
            (_('&Dates'),
             uicommand.ViewColumns(menuText=_('All date columns'),
                helpText=_('Show/hide all date-related columns'),
                setting=['startDate', 'dueDate', 'timeLeft', 'completionDate',
                         'recurrence'],
                viewer=self),
             None,
             uicommand.ViewColumn(menuText=_('&Start date'),
                 helpText=_('Show/hide start date column'),
                 setting='startDate', viewer=self),
             uicommand.ViewColumn(menuText=_('&Due date'),
                 helpText=_('Show/hide due date column'),
                 setting='dueDate', viewer=self),
             uicommand.ViewColumn(menuText=_('Co&mpletion date'),
                 helpText=_('Show/hide completion date column'),
                 setting='completionDate', viewer=self),
             uicommand.ViewColumn(menuText=_('D&ays left'),
                 helpText=_('Show/hide days left column'),
                 setting='timeLeft', viewer=self),
             uicommand.ViewColumn(menuText=_('&Recurrence'),
                 helpText=_('Show/hide recurrence column'),
                 setting='recurrence', viewer=self))]
        if self.settings.getboolean('feature', 'effort'):
            commands.extend([
                (_('&Budget'),
                 uicommand.ViewColumns(menuText=_('All budget columns'),
                     helpText=_('Show/hide all budget-related columns'),
                     setting=['budget', 'totalBudget', 'timeSpent',
                              'totalTimeSpent', 'budgetLeft','totalBudgetLeft'],
                     viewer=self),
                 None,
                 uicommand.ViewColumn(menuText=_('&Budget'),
                     helpText=_('Show/hide budget column'),
                     setting='budget', viewer=self),
                 uicommand.ViewColumn(menuText=_('Total b&udget'),
                     helpText=_('Show/hide total budget column (total budget includes budget for subtasks)'),
                     setting='totalBudget', viewer=self),
                 uicommand.ViewColumn(menuText=_('&Time spent'),
                     helpText=_('Show/hide time spent column'),
                     setting='timeSpent', viewer=self),
                 uicommand.ViewColumn(menuText=_('T&otal time spent'),
                     helpText=_('Show/hide total time spent column (total time includes time spent on subtasks)'),
                     setting='totalTimeSpent', viewer=self),
                 uicommand.ViewColumn(menuText=_('Budget &left'),
                     helpText=_('Show/hide budget left column'),
                     setting='budgetLeft', viewer=self),
                 uicommand.ViewColumn(menuText=_('Total budget l&eft'),
                     helpText=_('Show/hide total budget left column (total budget left includes budget left for subtasks)'),
                     setting='totalBudgetLeft', viewer=self)
                ),
                (_('&Financial'),
                 uicommand.ViewColumns(menuText=_('All financial columns'),
                     helpText=_('Show/hide all finance-related columns'),
                     setting=['hourlyFee', 'fixedFee', 'totalFixedFee',
                              'revenue', 'totalRevenue'],
                     viewer=self),
                 None,
                 uicommand.ViewColumn(menuText=_('&Hourly fee'),
                     helpText=_('Show/hide hourly fee column'),
                     setting='hourlyFee', viewer=self),
                 uicommand.ViewColumn(menuText=_('&Fixed fee'),
                     helpText=_('Show/hide fixed fee column'),
                     setting='fixedFee', viewer=self),
                 uicommand.ViewColumn(menuText=_('&Total fixed fee'),
                     helpText=_('Show/hide total fixed fee column'),
                     setting='totalFixedFee', viewer=self),
                 uicommand.ViewColumn(menuText=_('&Revenue'),
                     helpText=_('Show/hide revenue column'),
                     setting='revenue', viewer=self),
                 uicommand.ViewColumn(menuText=_('T&otal revenue'),
                     helpText=_('Show/hide total revenue column'),
                     setting='totalRevenue', viewer=self))])
        commands.extend([
            uicommand.ViewColumn(menuText=_('&Description'),
                helpText=_('Show/hide description column'),
                setting='description', viewer=self),
            uicommand.ViewColumn(menuText=_('&Attachments'),
                helpText=_('Show/hide attachment column'),
                setting='attachments', viewer=self)])
        if self.settings.getboolean('feature', 'notes'):
            commands.append(
                uicommand.ViewColumn(menuText=_('&Notes'),
                    helpText=_('Show/hide notes column'),
                    setting='notes', viewer=self))
        commands.extend([
            uicommand.ViewColumn(menuText=_('&Categories'),
                helpText=_('Show/hide categories column'),
                setting='categories', viewer=self),
            uicommand.ViewColumn(menuText=_('Overall categories'),
                helpText=_('Show/hide overall categories column'),
                setting='totalCategories', viewer=self),
            uicommand.ViewColumn(menuText=_('&Priority'),
                helpText=_('Show/hide priority column'),
                setting='priority', viewer=self),
            uicommand.ViewColumn(menuText=_('O&verall priority'),
                helpText=_('Show/hide overall priority column (overall priority is the maximum priority of a task and all its subtasks'),
                setting='totalPriority', viewer=self),
            uicommand.ViewColumn(menuText=_('&Reminder'),
                helpText=_('Show/hide reminder column'),
                setting='reminder', viewer=self)])
        return commands

    def getToolBarUICommands(self):
        ''' UI commands to put on the toolbar of this viewer. '''
        toolBarUICommands = super(TaskViewer, self).getToolBarUICommands() 
        toolBarUICommands.insert(-2, None) # Separator
        self.treeOrListUICommand = \
            uicommand.TaskViewerTreeOrListChoice(viewer=self)
        toolBarUICommands.insert(-2, self.treeOrListUICommand)
        return toolBarUICommands

    def createToolBarUICommands(self):
        ''' UI commands to put on the toolbar of this viewer. '''
        taskUICommands = super(TaskViewer, self).createToolBarUICommands()

        # Don't use extend() because we want the search box to be at
        # the end.

        taskUICommands[-2:-2] = [None,
                                 uicommand.TaskNew(taskList=self.presentation(),
                                                   settings=self.settings),
                                 uicommand.TaskNewFromTemplateButton(taskList=self.presentation(),
                                                             settings=self.settings,
                                                             bitmap='newtmpl'),
                                 uicommand.TaskNewSubTask(taskList=self.presentation(),
                                                          viewer=self),
                                 uicommand.TaskEdit(taskList=self.presentation(),
                                               viewer=self),
                                 uicommand.TaskDelete(taskList=self.presentation(),
                                                      viewer=self),
                                 None,
                                 uicommand.TaskToggleCompletion(viewer=self)]
        if self.settings.getboolean('feature', 'effort'):
            taskUICommands[-2:-2] = [
                # EffortStart needs a reference to the original (task) list to
                # be able to stop tracking effort for tasks that are already 
                # being tracked, but that might be filtered in the viewer's 
                # presentation.
                None,
                uicommand.EffortStart(viewer=self, taskList=self.taskFile.tasks()),
                uicommand.EffortStop(taskList=self.presentation())]
        return taskUICommands
 
    def trackStartEventType(self):
        return 'task.track.start'
    
    def trackStopEventType(self):
        return 'task.track.stop'
   
    def statusMessages(self):
        status1 = _('Tasks: %d selected, %d visible, %d total')%\
            (len(self.curselection()), len(self.presentation()), 
             self.presentation().originalLength())         
        status2 = _('Status: %d over due, %d inactive, %d completed')% \
            (self.presentation().nrOverdue(), self.presentation().nrInactive(),
             self.presentation().nrCompleted())
        return status1, status2
 
    def createTaskPopupMenu(self):
        return menu.TaskPopupMenu(self.parent, self.settings,
                                  self.presentation(), self.taskFile.efforts(),
                                  self)

    def createColumnPopupMenu(self):
        return menu.ColumnPopupMenu(self)

    def getColor(self, task):
        return color.taskColor(task, self.settings)
    
    def getBackgroundColor(self, task):
        return task.color()
    
    def getItemAttr(self, index):
        task = self.getItemWithIndex(index)
        return wx.ListItemAttr(self.getColor(task), 
                               self.getBackgroundColor(task))

    def __registerForColorChanges(self):
        colorSettings = ['color.%s'%setting for setting in 'activetasks',\
            'inactivetasks', 'completedtasks', 'duetodaytasks', 'overduetasks']
        for colorSetting in colorSettings:
            patterns.Publisher().registerObserver(self.onColorSettingChange, 
                eventType=colorSetting)
        patterns.Publisher().registerObserver(self.onColorChange,
            eventType=task.Task.colorChangedEventType())
        patterns.Publisher().registerObserver(self.atMidnight,
            eventType='clock.midnight')
        
    def atMidnight(self, event):
        self.refresh()
        
    def onColorSettingChange(self, event):
        self.refresh()
        
    def onColorChange(self, event):
        task = event.source()
        if task in self.presentation():
            self.widget.RefreshItem(self.getIndexOfItem(task))

    def createImageList(self):
        imageList = wx.ImageList(16, 16)
        self.imageIndex = {}
        for index, image in enumerate(['task', 'task_inactive', 
            'task_completed', 'task_duetoday', 'task_overdue', 'tasks', 
            'tasks_open', 'tasks_inactive', 'tasks_inactive_open', 
            'tasks_completed', 'tasks_completed_open', 'tasks_duetoday', 
            'tasks_duetoday_open', 'tasks_overdue', 'tasks_overdue_open', 
            'start', 'ascending', 'descending', 'ascending_with_status',
            'descending_with_status', 'attachment', 'note']):
            imageList.Add(wx.ArtProvider_GetBitmap(image, wx.ART_MENU, (16,16)))
            self.imageIndex[image] = index
        return imageList
    
    def getImageIndices(self, task):
        bitmap, bitmap_selected = render.taskBitmapNames(task)
        return self.imageIndex[bitmap], self.imageIndex[bitmap_selected]

    def subjectImageIndex(self, task, which):
        normalImageIndex, expandedImageIndex = self.getImageIndices(task) 
        if which in [wx.TreeItemIcon_Expanded, wx.TreeItemIcon_SelectedExpanded]:
            return expandedImageIndex 
        else:
            return normalImageIndex
                    
    def attachmentImageIndex(self, task, which):
        if task.attachments():
            return self.imageIndex['attachment'] 
        else:
            return -1

    def noteImageIndex(self, task, which):
        if task.notes():
            return self.imageIndex['note'] 
        else:
            return -1

    def newItemDialog(self, *args, **kwargs):
        bitmap = kwargs.pop('bitmap')
        kwargs['categories'] = [category for category in self.taskFile.categories()
                                if category.isFiltered()]
        newCommand = command.NewTaskCommand(self.presentation(), **kwargs)
        newCommand.do()
        return self.editItemDialog(bitmap=bitmap, items=newCommand.items)

    def editItemDialog(self, *args, **kwargs):
        items = kwargs.get('items', self.curselection())
        return dialog.editor.TaskEditor(wx.GetTopLevelParent(self),
            command.EditTaskCommand(self.presentation(), items),
            self.taskFile, self.settings, bitmap=kwargs['bitmap'])
    
    def deleteItemCommand(self):
        return command.DeleteTaskCommand(self.presentation(), self.curselection(),
                  shadow=self.settings.getboolean('feature', 'syncml'))
    
    def newSubItemDialog(self, *args, **kwargs):
        return dialog.editor.TaskEditor(wx.GetTopLevelParent(self),
            command.NewSubTaskCommand(self.presentation(), self.curselection()),
            self.taskFile, self.settings, bitmap=kwargs['bitmap'])
                           
    def sortBy(self, sortKey):
        # If the user clicks the same column for the third time, toggle
        # the SortyByTaskStatusFirst setting:
        if self.isSortedBy(sortKey):
            self.__sortKeyUnchangedCount += 1
        else:
            self.__sortKeyUnchangedCount = 0
        if self.__sortKeyUnchangedCount > 1:
            self.setSortByTaskStatusFirst(not self.isSortByTaskStatusFirst())
            self.__sortKeyUnchangedCount = 0
        super(TaskViewer, self).sortBy(sortKey)
            
    def setSortByTaskStatusFirst(self, *args, **kwargs):
        super(TaskViewer, self).setSortByTaskStatusFirst(*args, **kwargs)
        self.showSortOrder()
        
    def getSortOrderImageIndex(self):
        sortOrderImageIndex = super(TaskViewer, self).getSortOrderImageIndex()
        if self.isSortByTaskStatusFirst():
            sortOrderImageIndex += '_with_status' 
        return sortOrderImageIndex

    def createFilter(self, taskList):
        tasks = super(TaskViewer, self).createFilter(taskList)
        return domain.base.DeletedFilter(tasks)

    def setSearchFilter(self, searchString, *args, **kwargs):
        super(TaskViewer, self).setSearchFilter(searchString, *args, **kwargs)
        if searchString:
            self.expandAll()           

    def showTree(self, treeMode):
        self.settings.set(self.settingsSection(), 'treemode', str(treeMode))
        self.presentation().setTreeMode(treeMode)
        
    def renderSubject(self, task):
        return task.subject(recursive=not self.isTreeViewer())

    def getRootItems(self):
        ''' If the viewer is in tree mode, return the real root items. If the
            viewer is in list mode, return all items. '''
        if self.isTreeViewer():
            return super(TaskViewer, self).getRootItems()
        else:
            return self.presentation()
    
    def getItemParent(self, item):
        if self.isTreeViewer():
            return super(TaskViewer, self).getItemParent(item)
        else:
            return None
            
    def getChildrenCount(self, index):
        if self.isTreeViewer() or (index == ()):
            return super(TaskViewer, self).getChildrenCount(index)
        else:
            return 0

