'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2009 Frank Niessink <frank@niessink.com>
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
from taskcoachlib.domain import task, date
from taskcoachlib.i18n import _
from taskcoachlib.gui import uicommand, menu, color, render, dialog
import base, mixin


class BaseTaskViewer(mixin.SearchableViewer, mixin.FilterableViewerForTasks, 
                     base.UpdatePerSecondViewer, base.TreeViewer, patterns.Observer):
    defaultTitle = _('Tasks')
    defaultBitmap = 'task'
    
    def __init__(self, *args, **kwargs):
        super(BaseTaskViewer, self).__init__(*args, **kwargs)
        self.__registerForColorChanges()
        
    def domainObjectsToView(self):
        return self.taskFile.tasks()

    def isShowingTasks(self): 
        return True

    def createFilter(self, taskList):
        tasks = super(BaseTaskViewer, self).createFilter(taskList)
        return domain.base.DeletedFilter(tasks)

    def trackStartEventType(self):
        return task.Task.trackStartEventType()
    
    def trackStopEventType(self):
        return task.Task.trackStopEventType()
    
    def editItemDialog(self, *args, **kwargs):
        items = kwargs.get('items', self.curselection())
        if isinstance(items[0], task.Task):
            return dialog.editor.TaskEditor(wx.GetTopLevelParent(self),
                command.EditTaskCommand(self.presentation(), items),
                self.taskFile.tasks(), self.taskFile, self.settings, 
                bitmap=kwargs['bitmap'],
                columnName=kwargs.get('columnName', ''))
        else:
            return dialog.editor.EffortEditor(wx.GetTopLevelParent(self),
                command.EditEffortCommand(self.taskFile.efforts(), items),
                self.taskFile.efforts(), self.taskFile, self.settings, 
                bitmap=kwargs['bitmap'])

    def newSubItemDialog(self, *args, **kwargs):
        return dialog.editor.TaskEditor(wx.GetTopLevelParent(self),
            command.NewSubTaskCommand(self.presentation(), self.curselection()),
            self.taskFile.tasks(), self.taskFile, self.settings, 
            bitmap=kwargs['bitmap'])

    def deleteItemCommand(self):
        return command.DeleteTaskCommand(self.presentation(), self.curselection(),
                  shadow=self.settings.getboolean('feature', 'syncml'))    

    def createTaskPopupMenu(self):
        return menu.TaskPopupMenu(self.parent, self.settings,
                                  self.presentation(), self.taskFile.efforts(),
                                  self.taskFile.categories(), self)

    def createToolBarUICommands(self):
        ''' UI commands to put on the toolbar of this viewer. '''
        taskUICommands = super(BaseTaskViewer, self).createToolBarUICommands()

        # Don't use extend() because we want the search box to be at the end.
        taskUICommands[-2:-2] = \
            [None,
             uicommand.TaskNew(taskList=self.presentation(),
                               settings=self.settings),
             uicommand.TaskNewFromTemplateButton(taskList=self.presentation(),
                                                 settings=self.settings,
                                                 bitmap='newtmpl'),
             uicommand.TaskNewSubTask(taskList=self.presentation(),
                                      viewer=self),
             uicommand.TaskEdit(taskList=self.presentation(), viewer=self),
             uicommand.TaskDelete(taskList=self.presentation(), viewer=self),
             None,
             uicommand.TaskToggleCompletion(viewer=self)]
        if self.settings.getboolean('feature', 'effort'):
            taskUICommands[-2:-2] = [
                # EffortStart needs a reference to the original (task) list to
                # be able to stop tracking effort for tasks that are already 
                # being tracked, but that might be filtered in the viewer's 
                # presentation.
                None,
                uicommand.EffortStart(viewer=self, 
                                      taskList=self.taskFile.tasks()),
                uicommand.EffortStop(taskList=self.presentation())]
        return taskUICommands
 
    def statusMessages(self):
        status1 = _('Tasks: %d selected, %d visible, %d total')%\
            (len(self.curselection()), self.nrOfVisibleTasks(), 
             self.presentation().originalLength())         
        status2 = _('Status: %d over due, %d inactive, %d completed')% \
            (self.presentation().nrOverdue(), self.presentation().nrInactive(),
             self.presentation().nrCompleted())
        return status1, status2
    
    def nrOfVisibleTasks(self):
        # Make this overridable for viewers where the widgets does not show all
        # items in the presentation, i.e. the widget does filtering on its own.
        return len(self.presentation())

    def __registerForColorChanges(self):
        colorSettings = ['color.%s'%setting for setting in 'activetasks',\
            'inactivetasks', 'completedtasks', 'duesoontasks', 'overduetasks'] 
        colorSettings.append('behavior.duesoondays')
        for colorSetting in colorSettings:
            patterns.Publisher().registerObserver(self.onColorSettingChange, 
                eventType=colorSetting)
        patterns.Publisher().registerObserver(self.onAttributeChanged,
            eventType=task.Task.colorChangedEventType())
        patterns.Publisher().registerObserver(self.atMidnight,
            eventType='clock.midnight')

    def atMidnight(self, event):
        self.refresh()
        
    def onColorSettingChange(self, event):
        self.refresh()
        
    def children(self, item):
        try:
            return [child for child in item.children() if child in self.presentation()]
        except AttributeError:
            return []

    def iconName(self, item, isSelected):
        if not hasattr(item, 'children'):
            return ''
        bitmap, bitmap_selected = render.taskBitmapNames(item, 
                                                         self.children(item))
        if isSelected:
            bitmap = bitmap_selected
        return bitmap
        
    def getItemTooltipData(self, task):
        if not self.settings.getboolean('view', 'descriptionpopups'):
            return []
        result = [(self.iconName(task, task in self.curselection()), 
                   [self.label(task)])]
        if task.description():
            result.append((None, map(lambda x: x.rstrip('\n'),
                                 task.description().split('\n'))))
        if task.notes():
            result.append(('note', [note.subject() for note in task.notes()]))
        if task.attachments():
            result.append(('attachment', 
                [unicode(attachment) for attachment in task.attachments()]))
        return result


class RootNode(object):
    def __init__(self, tasks):
        self.tasks = tasks
        
    def subject(self):
        return ''
    
    def children(self, recursive=False):
        if recursive:
            return self.tasks[:]
        else:
            return self.tasks.rootItems()

    def color(self, *args, **kwargs):
        return None

    def completed(self, *args, **kwargs):
        return False

    dueSoon = inactive = overdue = isBeingTracked = completed


class SquareMapRootNode(RootNode):
    def __getattr__(self, attr):
        def getTaskAttribute(recursive=True):
            if recursive:
                return max(sum((getattr(task, attr)(recursive=True) for task in self.children()),
                               self.__zero), 
                           self.__zero)
            else:
                return self.__zero

        if attr in ('budget', 'budgetLeft', 'timeSpent'):
            self.__zero = date.TimeDelta()
        else:
            self.__zero = 0
        return getTaskAttribute


class TimelineRootNode(RootNode):
    def children(self, recursive=False):
        children = super(TimelineRootNode, self).children(recursive)
        children.sort(key=lambda task: task.startDate())
        return children
    
    def parallel_children(self, recursive=False):
        return self.children(recursive)

    def sequential_children(self):
        return []

    def startDate(self, recursive=False):
        startDates = [item.startDate(recursive=True) for item in self.parallel_children()]
        startDates = [aDate for aDate in startDates if aDate != date.Date()]
        if not startDates:
            startDates.append(date.Today())
        return min(startDates)
    
    def dueDate(self, recursive=False):
        dueDates = [item.dueDate(recursive=True) for item in self.parallel_children()]
        dueDates = [aDate for aDate in dueDates if aDate != date.Date()]
        if not dueDates:
            dueDates.append(date.Tomorrow())    
        return max(dueDates)
    

class TimelineViewer(BaseTaskViewer):
    defaultTitle = _('Timeline')
    defaultBitmap = 'timelineviewer'

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('settingsSection', 'timelineviewer')
        super(TimelineViewer, self).__init__(*args, **kwargs)
        for eventType in (task.Task.subjectChangedEventType(), 'task.startDate',
            'task.dueDate', 'task.completionDate'):
            self.registerObserver(self.onAttributeChanged, eventType)
        
    def createWidget(self):
        self.rootNode = TimelineRootNode(self.presentation())
        return widgets.Timeline(self, self.rootNode, self.onSelect, self.onEdit,
                                self.getItemTooltipData, self.createTaskPopupMenu())

    def onEdit(self, item):
        if isinstance(item, task.Task):
            edit = uicommand.TaskEdit(taskList=self.presentation(), viewer=self)
        else:
            edit = uicommand.EffortEdit(effortList=self.taskFile.efforts(), viewer=self)
        edit(item)
        
    def curselection(self):
        # Override curselection, because there is no need to translate indices
        # back to domain objects. Our widget already returns the selected domain
        # object itself.
        return self.widget.curselection()
    
    def bounds(self, item):
        times = [self.start(item), self.stop(item)]
        for child in self.parallel_children(item) + self.sequential_children(item):
            times.extend(self.bounds(child))
        times = [time for time in times if time is not None]
        if times:
            return min(times), max(times)
        else:
            return []
 
    def start(self, item, recursive=False):
        try:
            start = item.startDate(recursive=recursive)
            if start == date.Date():
                return None
        except AttributeError:
            start = item.getStart()
        return start.toordinal()

    def stop(self, item, recursive=False):
        try:
            if item.completed():
                stop = item.completionDate(recursive=recursive)
            else:
                stop = item.dueDate(recursive=recursive)
            if stop == date.Date():
                return None   
            else:
                stop += date.oneDay
        except AttributeError:
            stop = item.getStop()
            if not stop:
                return None
        return stop.toordinal() 

    def sequential_children(self, item):
        try:
            return item.efforts()
        except AttributeError:
            return []

    def parallel_children(self, item, recursive=False):
        try:
            children = [child for child in item.children(recursive=recursive) \
                        if child in self.presentation()]
            children.sort(key=lambda task: task.startDate())
            return children
        except AttributeError:
            return []

    def label(self, item):
        return item.subject()

    def background_color(self, item):
        return item.color()

    def foreground_color(self, item, depth=0):
        if hasattr(item, 'children'):
            return color.taskColor(item, self.settings)
        else:
            return None
  
    def icon(self, item, isSelected=False):
        bitmap = self.iconName(item, isSelected)
        return wx.ArtProvider_GetIcon(bitmap, wx.ART_MENU, (16,16))
    
    def now(self):
        return date.Today().toordinal()
    
    def nowlabel(self):
        return _('Now')

    def getItemTooltipData(self, item):
        if not self.settings.getboolean('view', 'descriptionpopups'):
            result = []
        elif isinstance(item, task.Task):
            result = super(TimelineViewer, self).getItemTooltipData(item)
        else:
            result = [(None, [render.dateTimePeriod(item.getStart(), item.getStop())])]
            if item.description(): 
                result.append((None, map(lambda x: x.rstrip('\n'),
                                 item.description().split('\n'))))       
        return result


class SquareTaskViewer(BaseTaskViewer):
    defaultTitle = _('Task square map')
    defaultBitmap = 'squaremapviewer'

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('settingsSection', 'squaretaskviewer')
        self.__orderBy = 'revenue'
        self.__transformTaskAttribute = lambda x: x
        self.__zero = 0
        super(SquareTaskViewer, self).__init__(*args, **kwargs)
        self.orderBy(self.settings.get(self.settingsSection(), 'sortby'))
        self.orderUICommand.setChoice(self.__orderBy)
        for eventType in (task.Task.subjectChangedEventType(), 'task.dueDate',
            'task.startDate', 'task.completionDate'):
            self.registerObserver(self.onAttributeChanged, eventType)

    def curselectionIsInstanceOf(self, class_):
        return class_ == task.Task
    
    def createWidget(self):
        return widgets.SquareMap(self, SquareMapRootNode(self.presentation()), 
            self.onSelect, 
            uicommand.TaskEdit(taskList=self.presentation(), viewer=self),
            self.getItemTooltipData, self.createTaskPopupMenu())
        
    def getToolBarUICommands(self):
        ''' UI commands to put on the toolbar of this viewer. '''
        toolBarUICommands = super(SquareTaskViewer, self).getToolBarUICommands()
        toolBarUICommands.insert(-2, None) # Separator
        self.orderUICommand = \
            uicommand.SquareTaskViewerOrderChoice(viewer=self)
        toolBarUICommands.insert(-2, self.orderUICommand)
        return toolBarUICommands
    
    def orderBy(self, choice):
        if choice == self.__orderBy:
            return
        oldChoice = self.__orderBy
        self.__orderBy = choice
        self.settings.set(self.settingsSection(), 'sortby', choice)
        self.removeObserver(self.onAttributeChanged, 'task.%s'%oldChoice)
        self.registerObserver(self.onAttributeChanged, 'task.%s'%choice)
        if choice in ('budget', 'timeSpent'):
            self.__transformTaskAttribute = lambda timeSpent: timeSpent.milliseconds()/1000
            self.__zero = date.TimeDelta()
        else:
            self.__transformTaskAttribute = lambda x: x
            self.__zero = 0
        self.refresh()
        
    def curselection(self):
        # Override curselection, because there is no need to translate indices
        # back to domain objects. Our widget already returns the selected domain
        # object itself.
        return self.widget.curselection()
    
    def nrOfVisibleTasks(self):
        return len([task for task in self.presentation() if getattr(task, 
                    self.__orderBy)(recursive=True) > self.__zero])
        

    # SquareMap adapter methods:
    
    def overall(self, task):
        return self.__transformTaskAttribute(max(getattr(task, self.__orderBy)(recursive=True),
                                                 self.__zero))
    
    def children_sum(self, children, parent):
        children_sum = sum((getattr(child, self.__orderBy)(recursive=True) for child in children \
                            if child in self.presentation()), self.__zero)
        return self.__transformTaskAttribute(max(children_sum, self.__zero))
    
    def empty(self, task):
        overall = self.overall(task)
        if overall:
            children_sum = self.children_sum(self.children(task), task)
            return max(self.__transformTaskAttribute(self.__zero), (overall - children_sum))/float(overall)
        return 0
    
    def label(self, task):
        subject = task.subject()
        value = self.render(getattr(task, self.__orderBy)(recursive=False))
        if value:
            return '%s (%s)'%(subject, value) 
        else:
            return subject

    def value(self, task, parent=None):
        return self.overall(task)
    
    def background_color(self, task, depth):
        return task.color()

    def foreground_color(self, task, depth):
        return color.taskColor(task, self.settings)
    
    def icon(self, task, isSelected):
        bitmap = self.iconName(task, isSelected)
        return wx.ArtProvider_GetIcon(bitmap, wx.ART_MENU, (16,16))

    # Helper methods
    
    renderer = dict(budget=render.budget, timeSpent=render.timeSpent, 
                    fixedFee=render.monetaryAmount, 
                    revenue=render.monetaryAmount)
    
    def render(self, value):
        return self.renderer[self.__orderBy](value)

    
    
class TaskViewer(mixin.AttachmentDropTarget, mixin.SortableViewerForTasks, 
                 base.SortableViewerWithColumns, BaseTaskViewer):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('settingsSection', 'taskviewer')
        super(TaskViewer, self).__init__(*args, **kwargs)
        self.treeOrListUICommand.setChoice(self.isTreeViewer())
    
    def isTreeViewer(self):
        return self.settings.getboolean(self.settingsSection(), 'treemode')

    def curselectionIsInstanceOf(self, class_):
        return class_ == task.Task
    
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
                task.Task.trackStartEventType(), task.Task.trackStopEventType(), 
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
        for name, columnHeader, renderCallback, eventType in [
            ('startDate', _('Start date'), lambda task: render.date(task.startDate()), None),
            ('dueDate', _('Due date'), lambda task: render.date(task.dueDate()), None),
            ('timeLeft', _('Days left'), lambda task: render.daysLeft(task.timeLeft(), task.completed()), None),
            ('completionDate', _('Completion date'), lambda task: render.date(task.completionDate()), None),
            ('recurrence', _('Recurrence'), lambda task: render.recurrence(task.recurrence()), None),
            ('budget', _('Budget'), lambda task: render.budget(task.budget()), None),
            ('totalBudget', _('Total budget'), lambda task: render.budget(task.budget(recursive=True)), None),
            ('timeSpent', _('Time spent'), lambda task: render.timeSpent(task.timeSpent()), None),
            ('totalTimeSpent', _('Total time spent'), lambda task: render.timeSpent(task.timeSpent(recursive=True)), None),
            ('budgetLeft', _('Budget left'), lambda task: render.budget(task.budgetLeft()), None),
            ('totalBudgetLeft', _('Total budget left'), lambda task: render.budget(task.budgetLeft(recursive=True)), None),
            ('priority', _('Priority'), lambda task: render.priority(task.priority()), None),
            ('totalPriority', _('Overall priority'), lambda task: render.priority(task.priority(recursive=True)), None),
            ('hourlyFee', _('Hourly fee'), lambda task: render.monetaryAmount(task.hourlyFee()), task.Task.hourlyFeeChangedEventType()),
            ('fixedFee', _('Fixed fee'), lambda task: render.monetaryAmount(task.fixedFee()), None),
            ('totalFixedFee', _('Total fixed fee'), lambda task: render.monetaryAmount(task.fixedFee(recursive=True)), None),
            ('revenue', _('Revenue'), lambda task: render.monetaryAmount(task.revenue()), None),
            ('totalRevenue', _('Total revenue'), lambda task: render.monetaryAmount(task.revenue(recursive=True)), None),
            ('reminder', _('Reminder'), lambda task: render.dateTime(task.reminder()), None)]:
            eventType = eventType or 'task.'+name
            if (name in dependsOnEffortFeature and effortOn) or name not in dependsOnEffortFeature:
                columns.append(widgets.Column(name, columnHeader, eventType, 
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

    def createImageList(self):
        imageList = wx.ImageList(16, 16)
        self.imageIndex = {}
        for index, image in enumerate(['task', 'task_inactive', 
            'task_completed', 'task_duesoon', 'task_overdue', 'tasks', 
            'tasks_open', 'tasks_inactive', 'tasks_inactive_open', 
            'tasks_completed', 'tasks_completed_open', 'tasks_duesoon', 
            'tasks_duesoon_open', 'tasks_overdue', 'tasks_overdue_open', 
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
        expanded = which in [wx.TreeItemIcon_Expanded, 
                             wx.TreeItemIcon_SelectedExpanded]
        return expandedImageIndex if expanded else normalImageIndex
                    
    def attachmentImageIndex(self, task, which):
        return self.imageIndex['attachment'] if task.attachments() else -1 

    def noteImageIndex(self, task, which):
        return self.imageIndex['note'] if task.notes() else -1 

    def newItemDialog(self, *args, **kwargs):
        bitmap = kwargs.pop('bitmap')
        kwargs['categories'] = [category for category in self.taskFile.categories()
                                if category.isFiltered()]
        newCommand = command.NewTaskCommand(self.presentation(), **kwargs)
        newCommand.do()
        return self.editItemDialog(bitmap=bitmap, items=newCommand.items)

    def setSortByTaskStatusFirst(self, *args, **kwargs):
        super(TaskViewer, self).setSortByTaskStatusFirst(*args, **kwargs)
        self.showSortOrder()
        
    def getSortOrderImageIndex(self):
        sortOrderImageIndex = super(TaskViewer, self).getSortOrderImageIndex()
        if self.isSortByTaskStatusFirst():
            sortOrderImageIndex += '_with_status' 
        return sortOrderImageIndex

    def setSearchFilter(self, searchString, *args, **kwargs):
        super(TaskViewer, self).setSearchFilter(searchString, *args, **kwargs)
        if searchString:
            self.expandAll()           

    def showTree(self, treeMode):
        self.settings.set(self.settingsSection(), 'treemode', str(treeMode))
        self.presentation().setTreeMode(treeMode)
        
    def renderSubject(self, task):
        return task.subject(recursive=not self.isTreeViewer())
    
    def onEverySecond(self, event):
        # Only update when a column is visible that changes every second 
        if any([self.isVisibleColumnByName(column) for column in 'timeSpent', 
               'totalTimeSpent', 'budgetLeft', 'totalBudgetLeft',
               'revenue', 'totalRevenue']):
            super(TaskViewer, self).onEverySecond(event)

    def getRootItems(self):
        ''' If the viewer is in tree mode, return the real root items. If the
            viewer is in list mode, return all items. '''
        return super(TaskViewer, self).getRootItems() if \
            self.isTreeViewer() else self.presentation()
    
    def getItemParent(self, item):
        return super(TaskViewer, self).getItemParent(item) if \
            self.isTreeViewer() else None
            
    def getChildrenCount(self, index):
        return super(TaskViewer, self).getChildrenCount(index) if \
            self.isTreeViewer() or (index == ()) else 0

