# -*- coding: utf-8 -*-

'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2011 Task Coach developers <developers@taskcoach.org>
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
from taskcoachlib import patterns, command, widgets, domain, render
from taskcoachlib.domain import task, date
from taskcoachlib.i18n import _
from taskcoachlib.gui import uicommand, menu, dialog
from taskcoachlib.thirdparty.wxScheduler import wxSCHEDULER_NEXT, wxSCHEDULER_PREV, \
    wxSCHEDULER_TODAY, wxSCHEDULER_TODAY, wxSCHEDULER_MONTHLY, wxFancyDrawer
from taskcoachlib.widgets import CalendarConfigDialog
import base, mixin, refresher, inplace_editor


class TaskViewerStatusMessages(patterns.Observer):
    template1 = _('Tasks: %d selected, %d visible, %d total')
    template2 = _('Status: %d overdue, %d inactive, %d completed')
    
    def __init__(self, viewer):
        super(TaskViewerStatusMessages, self).__init__()
        self.__viewer = viewer
        self.__presentation = viewer.presentation()
    
    def __call__(self):
        return self.template1%(len(self.__viewer.curselection()), 
                               self.__viewer.nrOfVisibleTasks(), 
                               self.__presentation.originalLength()), \
               self.template2%(self.__presentation.nrOverdue(), 
                               self.__presentation.nrInactive(), 
                               self.__presentation.nrCompleted())
        

class BaseTaskViewer(mixin.SearchableViewerMixin, # pylint: disable-msg=W0223
                     mixin.FilterableViewerForTasksMixin,
                     base.TreeViewer, patterns.Observer): 
    defaultTitle = _('Tasks')
    defaultBitmap = 'led_blue_icon'
    
    def __init__(self, *args, **kwargs):
        super(BaseTaskViewer, self).__init__(*args, **kwargs)
        if kwargs.get('doRefresh', True):
            self.secondRefresher = refresher.SecondRefresher(self,
                                                             task.Task.trackStartEventType(),
                                                             task.Task.trackStopEventType())
            self.minuteRefresher = refresher.MinuteRefresher(self)
        self.statusMessages = TaskViewerStatusMessages(self)
        self.__registerForAppearanceChanges()
        
    def domainObjectsToView(self):
        return self.taskFile.tasks()

    def isShowingTasks(self): 
        return True

    def createFilter(self, taskList):
        tasks = domain.base.DeletedFilter(taskList)
        return super(BaseTaskViewer, self).createFilter(tasks)

    def newItemDialog(self, *args, **kwargs):
        kwargs['categories'] = self.taskFile.categories().filteredCategories()
        return super(BaseTaskViewer, self).newItemDialog(*args, **kwargs)
    
    def editItemDialog(self, items, bitmap, columnName=''):
        if isinstance(items[0], task.Task):
            return super(BaseTaskViewer, self).editItemDialog(items, bitmap, columnName)
        else:
            return dialog.editor.EffortEditor(wx.GetTopLevelParent(self),
                items, self.settings, self.taskFile.efforts(), self.taskFile,  
                bitmap=bitmap)
            
    def itemEditorClass(self):
        return dialog.editor.TaskEditor
    
    def newItemCommandClass(self):
        return command.NewTaskCommand
    
    def newSubItemCommandClass(self):
        return command.NewSubTaskCommand
    
    def deleteItemCommand(self):
        return command.DeleteTaskCommand(self.presentation(), self.curselection(),
                  shadow=self.settings.getboolean('feature', 'syncml'))    

    def createTaskPopupMenu(self):
        return menu.TaskPopupMenu(self.parent, self.settings,
                                  self.presentation(), self.taskFile.efforts(),
                                  self.taskFile.categories(), self)

    def createCreationToolBarUICommands(self):
        return [uicommand.TaskNew(taskList=self.presentation(),
                                  settings=self.settings),
                uicommand.NewSubItem(viewer=self),
                uicommand.TaskNewFromTemplateButton(taskList=self.presentation(),
                                                    settings=self.settings,
                                                    bitmap='newtmpl')] + \
            super(BaseTaskViewer, self).createCreationToolBarUICommands()
    
    def createActionToolBarUICommands(self):
        uiCommands = [uicommand.TaskToggleCompletion(viewer=self),
                      None,
                      uicommand.ViewerHideCompletedTasks(viewer=self,
                          bitmap='filtercompletedtasks'),
                      uicommand.ViewerHideInactiveTasks(viewer=self,
                          bitmap='filterinactivetasks')]
        if self.settings.getboolean('feature', 'effort'):
            uiCommands.extend([
                # EffortStart needs a reference to the original (task) list to
                # be able to stop tracking effort for tasks that are already 
                # being tracked, but that might be filtered in the viewer's 
                # presentation.
                None,
                uicommand.EffortStart(viewer=self, 
                                      taskList=self.taskFile.tasks()),
                uicommand.EffortStop(effortList=self.taskFile.efforts(),
                                     taskList=self.taskFile.tasks())])
        return uiCommands + super(BaseTaskViewer, self).createActionToolBarUICommands()
        
    def nrOfVisibleTasks(self):
        # Make this overridable for viewers where the widget does not show all
        # items in the presentation, i.e. the widget does filtering on its own.
        return len(self.presentation())

    def __registerForAppearanceChanges(self):
        for appearance in ('font', 'fgcolor', 'bgcolor', 'icon'):
            appearanceSettings = ['%s.%s'%(appearance, setting) for setting in 'activetasks',\
                                  'inactivetasks', 'completedtasks', 'duesoontasks', 'overduetasks'] 
            for appearanceSetting in appearanceSettings:
                patterns.Publisher().registerObserver(self.onAppearanceSettingChange, 
                                                      eventType=appearanceSetting)
        for eventType in (task.Task.appearanceChangedEventType(), 
                          task.Task.percentageCompleteChangedEventType(),
                          'task.prerequisites'):
            patterns.Publisher().registerObserver(self.onAttributeChanged,
                                                  eventType=eventType)
        patterns.Publisher().registerObserver(self.atMidnight,
            eventType='clock.day')
        patterns.Publisher().registerObserver(self.onWake,
            eventType='powermgt.on')

    def atMidnight(self, event): # pylint: disable-msg=W0613
        pass

    def onWake(self, event): # pylint: disable-msg=W0613
        self.refresh()
        
    def onAppearanceSettingChange(self, event): # pylint: disable-msg=W0613
        wx.CallAfter(self.refresh) # Let domain objects update appearance first

    def iconName(self, item, isSelected):
        return item.selectedIcon(recursive=True) if isSelected else item.icon(recursive=True)

    def getItemTooltipData(self, task): # pylint: disable-msg=W0621
        if not self.settings.getboolean('view', 'descriptionpopups'):
            return []
        result = [(self.iconName(task, task in self.curselection()), 
                   [self.getItemText(task)])]
        if task.description():
            result.append((None, [line.rstrip('\n') for line in task.description().split('\n')]))
        if task.notes():
            result.append(('note_icon', sorted([note.subject() for note in task.notes()])))
        if task.attachments():
            result.append(('paperclip_icon',
                sorted([unicode(attachment) for attachment in task.attachments()])))
        return result

    def label(self, task): # pylint: disable-msg=W0621
        return self.getItemText(task)


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

    # pylint: disable-msg=W0613
    
    def foregroundColor(self, *args, **kwargs): 
        return None

    def backgroundColor(self, *args, **kwargs):
        return None
    
    def font(self, *args, **kwargs):
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

        self.__zero = date.TimeDelta() if attr in ('budget', 'budgetLeft', 'timeSpent') else 0 # pylint: disable-msg=W0201
        return getTaskAttribute


class TimelineRootNode(RootNode):
    def children(self, recursive=False):
        children = super(TimelineRootNode, self).children(recursive)
        children.sort(key=lambda task: task.startDateTime())
        return children
    
    def parallel_children(self, recursive=False):
        return self.children(recursive)

    def sequential_children(self):
        return []

    def startDateTime(self, recursive=False): # pylint: disable-msg=W0613
        startDateTimes = [item.startDateTime(recursive=True) for item in self.parallel_children()]
        startDateTimes = [dt for dt in startDateTimes if dt != date.DateTime()]
        if not startDateTimes:
            startDateTimes.append(date.Now())
        return min(startDateTimes)
    
    def dueDateTime(self, recursive=False): # pylint: disable-msg=W0613
        dueDateTimes = [item.dueDateTime(recursive=True) for item in self.parallel_children()]
        dueDateTimes = [dt for dt in dueDateTimes if dt != date.DateTime()]
        if not dueDateTimes:
            dueDateTimes.append(date.Now() + date.oneDay)    
        return max(dueDateTimes)
    

class TimelineViewer(BaseTaskViewer):
    defaultTitle = _('Timeline')
    defaultBitmap = 'timelineviewer'

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('settingsSection', 'timelineviewer')
        super(TimelineViewer, self).__init__(*args, **kwargs)
        for eventType in (task.Task.subjectChangedEventType(), 'task.startDateTime',
            'task.dueDateTime', 'task.completionDateTime'):
            self.registerObserver(self.onAttributeChanged, eventType)
        
    def createWidget(self):
        self.rootNode = TimelineRootNode(self.presentation()) # pylint: disable-msg=W0201
        itemPopupMenu = self.createTaskPopupMenu()
        self._popupMenus.append(itemPopupMenu)
        return widgets.Timeline(self, self.rootNode, self.onSelect, self.onEdit,
                                itemPopupMenu)

    def onEdit(self, item):
        edit = uicommand.Edit(viewer=self)
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
        return (min(times), max(times)) if times else []
 
    def start(self, item, recursive=False):
        try:
            start = item.startDateTime(recursive=recursive)
            if start == date.DateTime():
                return None
        except AttributeError:
            start = item.getStart()
        return start.toordinal()

    def stop(self, item, recursive=False):
        try:
            if item.completed():
                stop = item.completionDateTime(recursive=recursive)
            else:
                stop = item.dueDateTime(recursive=recursive)
            if stop == date.DateTime():
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
            children.sort(key=lambda task: task.startDateTime())
            return children
        except AttributeError:
            return []

    def foreground_color(self, item, depth=0): # pylint: disable-msg=W0613
        return item.foregroundColor(recursive=True)
          
    def background_color(self, item, depth=0): # pylint: disable-msg=W0613
        return item.backgroundColor(recursive=True)
    
    def font(self, item, depth=0): # pylint: disable-msg=W0613
        return item.font(recursive=True)

    def icon(self, item, isSelected=False):
        bitmap = self.iconName(item, isSelected)
        return wx.ArtProvider_GetIcon(bitmap, wx.ART_MENU, (16,16))
    
    def now(self):
        return date.Now().toordinal()
    
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
                result.append((None, [line.rstrip('\n') for line in item.description().split('\n')]))     
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
        for eventType in (task.Task.subjectChangedEventType(), 'task.dueDateTime',
            'task.startDateTime', 'task.completionDateTime'):
            self.registerObserver(self.onAttributeChanged, eventType)

    def curselectionIsInstanceOf(self, class_):
        return class_ == task.Task
    
    def createWidget(self):
        itemPopupMenu = self.createTaskPopupMenu()
        self._popupMenus.append(itemPopupMenu)
        return widgets.SquareMap(self, SquareMapRootNode(self.presentation()), 
            self.onSelect, uicommand.Edit(viewer=self), itemPopupMenu)
        
    def createModeToolBarUICommands(self):
        self.orderUICommand = uicommand.SquareTaskViewerOrderChoice(viewer=self) # pylint: disable-msg=W0201
        return super(SquareTaskViewer, self).createModeToolBarUICommands() + \
            [self.orderUICommand]
        
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
        return len([eachTask for eachTask in self.presentation() \
                    if getattr(eachTask, self.__orderBy)(recursive=True) > self.__zero])
        
    # SquareMap adapter methods:
    # pylint: disable-msg=W0621
    
    def overall(self, task):
        return self.__transformTaskAttribute(max(getattr(task, self.__orderBy)(recursive=True),
                                                 self.__zero))
    
    def children_sum(self, children, parent): # pylint: disable-msg=W0613
        children_sum = sum((max(getattr(child, self.__orderBy)(recursive=True), self.__zero) for child in children \
                            if child in self.presentation()), self.__zero)
        return self.__transformTaskAttribute(max(children_sum, self.__zero))
    
    def empty(self, task):
        overall = self.overall(task)
        if overall:
            children_sum = self.children_sum(self.children(task), task)
            return max(self.__transformTaskAttribute(self.__zero), (overall - children_sum))/float(overall)
        return 0
    
    def getItemText(self, task):
        text = super(SquareTaskViewer, self).getItemText(task)
        value = self.render(getattr(task, self.__orderBy)(recursive=False))
        return '%s (%s)'%(text, value) if value else text

    def value(self, task, parent=None): # pylint: disable-msg=W0613
        return self.overall(task)

    def foreground_color(self, task, depth): # pylint: disable-msg=W0613
        return task.foregroundColor(recursive=True)
        
    def background_color(self, task, depth): # pylint: disable-msg=W0613
        return task.backgroundColor(recursive=True)
    
    def font(self, task, depth): # pylint: disable-msg=W0613
        return task.font(recursive=True)

    def icon(self, task, isSelected):
        bitmap = self.iconName(task, isSelected) or 'led_blue_icon'
        return wx.ArtProvider_GetIcon(bitmap, wx.ART_MENU, (16,16))

    # Helper methods
    
    renderer = dict(budget=render.budget, timeSpent=render.timeSpent, 
                    fixedFee=render.monetaryAmount, 
                    revenue=render.monetaryAmount,
                    priority=render.priority)
    
    def render(self, value):
        return self.renderer[self.__orderBy](value)


class CalendarViewer(mixin.AttachmentDropTargetMixin,
                     mixin.SortableViewerForTasksMixin,
                     BaseTaskViewer):
    defaultTitle = _('Calendar')
    defaultBitmap = 'calendar_icon'

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('settingsSection', 'calendarviewer')
        kwargs['doRefresh'] = False
        super(CalendarViewer, self).__init__(*args, **kwargs)

        start = self.settings.get(self.settingsSection(), 'viewdate')
        if start:
            dt = wx.DateTime.Now()
            dt.ParseDateTime(start)
            self.widget.SetDate(dt)

        self.widget.SetWorkHours(self.settings.getint('view', 'efforthourstart'),
                                 self.settings.getint('view', 'efforthourend'))

        self.reconfig()
        self.widget.SetPeriodWidth(self.settings.getint(self.settingsSection(), 'periodwidth'))

        for eventType in ('view.efforthourstart', 'view.efforthourend'):
            self.registerObserver(self.onWorkingHourChanged, eventType)

        # pylint: disable-msg=E1101
        for eventType in (task.Task.subjectChangedEventType(), 'task.startDateTime',
                          'task.dueDateTime', 'task.completionDateTime',
                          task.Task.attachmentsChangedEventType(),
                          task.Task.notesChangedEventType(),
                          task.Task.trackStartEventType(), task.Task.trackStopEventType()):
            self.registerObserver(self.onAttributeChanged, eventType)

    def isTreeViewer(self):
        return False

    def onEverySecond(self, event): # pylint: disable-msg=W0221,W0613
        pass # Too expensive

    def atMidnight(self, event):
        if not self.settings.get(self.settingsSection(), 'viewdate'):
            # User has selected the "current" date/time; it may have
            # changed now
            self.SetViewType(wxSCHEDULER_TODAY)

    def onWake(self, event):
        self.atMidnight(event)

    def onWorkingHourChanged(self, event): # pylint: disable-msg=W0613
        self.widget.SetWorkHours(self.settings.getint('view', 'efforthourstart'),
                                 self.settings.getint('view', 'efforthourend'))

    def createWidget(self):
        itemPopupMenu = self.createTaskPopupMenu()
        self._popupMenus.append(itemPopupMenu)
        widget = widgets.Calendar(self, self.presentation(), self.iconName, self.onSelect,
                                  self.onEdit, self.onCreate, self.onChangeConfig, itemPopupMenu,
                                  **self.widgetCreationKeywordArguments())

        if self.settings.getboolean('calendarviewer', 'gradient'):
            # If called directly, we crash with a Cairo assert failing...
            wx.CallAfter(widget.SetDrawer, wxFancyDrawer)

        return widget

    def onChangeConfig(self):
        self.settings.set(self.settingsSection(), 'periodwidth', str(self.widget.GetPeriodWidth()))

    def onEdit(self, item):
        edit = uicommand.Edit(viewer=self)
        edit(item)

    def onCreate(self, dateTime, show=True):
        startDateTime = dateTime
        dueDateTime = dateTime.endOfDay() if dateTime == dateTime.startOfDay() else dateTime
        create = uicommand.TaskNew(taskList=self.presentation(), 
                                   settings=self.settings,
                                   taskKeywords=dict(startDateTime=startDateTime, 
                                                     dueDateTime=dueDateTime))
        return create(event=None, show=show)

    def createModeToolBarUICommands(self):
        return super(CalendarViewer, self).createModeToolBarUICommands() + \
            [uicommand.CalendarViewerConfigure(viewer=self),
             uicommand.CalendarViewerPreviousPeriod(viewer=self),
             uicommand.CalendarViewerToday(viewer=self),
             uicommand.CalendarViewerNextPeriod(viewer=self)]

    def SetViewType(self, type_):
        self.widget.SetViewType(type_)
        dt = self.widget.GetDate()
        now = wx.DateTime.Today()
        if (dt.GetYear(), dt.GetMonth(), dt.GetDay()) == (now.GetYear(), now.GetMonth(), now.GetDay()):
            toSave = ''
        else:
            toSave = dt.Format()
        self.settings.set(self.settingsSection(), 'viewdate', toSave)

    # We need to override these because BaseTaskViewer is a tree viewer, but
    # CalendarViewer is not. There is probably a better solution...

    def isAnyItemExpandable(self):
        return False

    def isAnyItemCollapsable(self):
        return False

    def reconfig(self):
        self.widget.Freeze()
        try:
            self.widget.SetPeriodCount(self.settings.getint(self.settingsSection(), 'periodcount'))
            self.widget.SetViewType(self.settings.getint(self.settingsSection(), 'viewtype'))
            self.widget.SetStyle(self.settings.getint(self.settingsSection(), 'vieworientation'))
            self.widget.SetShowNoStartDate(self.settings.getboolean(self.settingsSection(), 'shownostart'))
            self.widget.SetShowNoDueDate(self.settings.getboolean(self.settingsSection(), 'shownodue'))
            self.widget.SetShowUnplanned(self.settings.getboolean(self.settingsSection(), 'showunplanned'))
            self.widget.SetShowNow(self.settings.getboolean(self.settingsSection(), 'shownow'))

            hcolor = self.settings.get(self.settingsSection(), 'highlightcolor')
            if hcolor:
                highlightColor = wx.Colour(*tuple([int(c) for c in hcolor.split(',')]))
                self.widget.SetHighlightColor(highlightColor)
            self.widget.RefreshAllItems(0)
        finally:
            self.widget.Thaw()

    def configure(self):
        dlg = CalendarConfigDialog(self.settings, self.settingsSection(), self, title=_('Calendar viewer configuration'))
        dlg.CentreOnParent()
        if dlg.ShowModal() == wx.ID_OK:
            self.reconfig()


class TaskViewer(mixin.AttachmentDropTargetMixin, # pylint: disable-msg=W0223
                 mixin.SortableViewerForTasksMixin, 
                 mixin.NoteColumnMixin, mixin.AttachmentColumnMixin,
                 base.SortableViewerWithColumns, BaseTaskViewer):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('settingsSection', 'taskviewer')
        super(TaskViewer, self).__init__(*args, **kwargs)
        self.treeOrListUICommand.setChoice(self.isTreeViewer())
        if self.isVisibleColumnByName('timeLeft'):
            self.minuteRefresher.startClock()
    
    def isTreeViewer(self):
        # We first ask our presentation what the mode is because 
        # ConfigParser.getboolean is a relatively expensive method. However,
        # when initializing, the presentation might not be created yet. So in
        # that case we get an AttributeError and we use the settings.
        try:
            return self.presentation().treeMode()
        except AttributeError:
            return self.settings.getboolean(self.settingsSection(), 'treemode')

    def showColumn(self, column, show=True, *args, **kwargs):
        super(TaskViewer, self).showColumn(column, show, *args, **kwargs)
        if column.name() == 'timeLeft':
            if show:
                self.minuteRefresher.startClock()
            else:
                self.minuteRefresher.stopClock()
                            
    def curselectionIsInstanceOf(self, class_):
        return class_ == task.Task
    
    def createWidget(self):
        imageList = self.createImageList() # Has side-effects
        self._columns = self._createColumns()
        itemPopupMenu = self.createTaskPopupMenu()
        columnPopupMenu = self.createColumnPopupMenu()
        self._popupMenus.extend([itemPopupMenu, columnPopupMenu])
        widget = widgets.TreeListCtrl(self, self.columns(), self.onSelect, 
            uicommand.Edit(viewer=self),
            uicommand.TaskDragAndDrop(taskList=self.presentation(), viewer=self),
            itemPopupMenu, columnPopupMenu,
            **self.widgetCreationKeywordArguments())
        widget.AssignImageList(imageList) # pylint: disable-msg=E1101
        widget.Bind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self.onBeginEdit)
        widget.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.onEndEdit)
        return widget
    
    def onBeginEdit(self, event):
        ''' Make sure only the non-recursive part of the subject can be
            edited inline. '''
        event.Skip()
        if not self.isTreeViewer():
            # Make sure the text control only shows the non-recursive subject
            # by temporarily changing the item text into the non-recursive
            # subject. When the editing ends, we change the item text back into
            # the recursive subject. See onEndEdit.
            treeItem = event.GetItem()
            editedTask = self.widget.GetItemPyData(treeItem)
            self.widget.SetItemText(treeItem, editedTask.subject())
            
    def onEndEdit(self, event):
        ''' Make sure only the non-recursive part of the subject can be
            edited inline. '''
        event.Skip()
        if not self.isTreeViewer():
            # Restore the recursive subject. Here we don't care whether the user
            # actually changed the subject. If she did, the subject will updated
            # via the regular notification mechanism.
            treeItem = event.GetItem()
            editedTask = self.widget.GetItemPyData(treeItem)
            self.widget.SetItemText(treeItem, editedTask.subject(recursive=True))
    
    def _createColumns(self):
        kwargs = dict(renderDescriptionCallback=lambda task: task.description(),
                      resizeCallback=self.onResizeColumn)
        # pylint: disable-msg=E1101,W0142
        columns = [widgets.Column('subject', _('Subject'), 
                task.Task.subjectChangedEventType(), 
                'task.completionDateTime', 'task.dueDateTime', 
                'task.startDateTime',
                task.Task.trackStartEventType(), task.Task.trackStopEventType(), 
                sortCallback=uicommand.ViewerSortByCommand(viewer=self,
                    value='subject'),
                width=self.getColumnWidth('subject'), 
                imageIndicesCallback=self.subjectImageIndices,
                renderCallback=self.renderSubject, 
                editCallback=self.onEditSubject, 
                editControl=inplace_editor.SubjectCtrl, **kwargs)] + \
            [widgets.Column('description', _('Description'), 
                task.Task.descriptionChangedEventType(), 
                sortCallback=uicommand.ViewerSortByCommand(viewer=self,
                    value='description'),
                renderCallback=lambda task: task.description(), 
                width=self.getColumnWidth('description'),  
                editCallback=self.onEditDescription, 
                editControl=inplace_editor.DescriptionCtrl, **kwargs)] + \
            [widgets.Column('attachments', '', 
                task.Task.attachmentsChangedEventType(), 
                width=self.getColumnWidth('attachments'),
                alignment=wx.LIST_FORMAT_LEFT,
                imageIndicesCallback=self.attachmentImageIndices,
                headerImageIndex=self.imageIndex['paperclip_icon'],
                renderCallback=lambda task: '', **kwargs)]
        if self.settings.getboolean('feature', 'notes'):
            columns.append(widgets.Column('notes', '', 
                task.Task.notesChangedEventType(),
                width=self.getColumnWidth('notes'),
                alignment=wx.LIST_FORMAT_LEFT,
                imageIndicesCallback=self.noteImageIndices,
                headerImageIndex=self.imageIndex['note_icon'],
                renderCallback=lambda task: '', **kwargs))
        columns.extend(
            [widgets.Column('categories', _('Categories'), 
                task.Task.categoryAddedEventType(), 
                task.Task.categoryRemovedEventType(), 
                task.Task.categorySubjectChangedEventType(),
                task.Task.expansionChangedEventType(),
                sortCallback=uicommand.ViewerSortByCommand(viewer=self,
                                                           value='categories'),
                width=self.getColumnWidth('categories'),
                renderCallback=self.renderCategories, **kwargs),
             widgets.Column('prerequisites', _('Prerequisites'),
                'task.prerequisites', 'task.prerequisite.subject',
                task.Task.expansionChangedEventType(),
                sortCallback=uicommand.ViewerSortByCommand(viewer=self,
                                                           value='prerequisites'),
                renderCallback=self.renderPrerequisites,
                width=self.getColumnWidth('prerequisites'), **kwargs),
             widgets.Column('dependencies', _('Dependencies'),
                'task.dependencies', 'task.dependency.subject',
                task.Task.expansionChangedEventType(),
                sortCallback=uicommand.ViewerSortByCommand(viewer=self,
                                                           value='dependencies'),
                renderCallback=self.renderDependencies,
                width=self.getColumnWidth('dependencies'), **kwargs)])

            ## [widgets.Column('ordering', _('Manual ordering'),
            ##     task.Task.orderingChangedEventType(),
            ##     sortCallback=uicommand.ViewerSortByCommand(viewer=self,
            ##         value='ordering'),
            ##     renderCallback=lambda task: '',
            ##     width=self.getColumnWidth('ordering'))] + \

        effortOn = self.settings.getboolean('feature', 'effort')
        dependsOnEffortFeature = ['budget',  'timeSpent', 'budgetLeft',
                                  'hourlyFee', 'fixedFee', 'revenue']
        for name, columnHeader, editCtrl, editCallback, eventTypes in [
            ('startDateTime', _('Start date'), inplace_editor.DateTimeCtrl, self.onEditStartDateTime, []),
            ('dueDateTime', _('Due date'), inplace_editor.DateTimeCtrl, self.onEditDueDateTime, [task.Task.expansionChangedEventType()]),
            ('completionDateTime', _('Completion date'), inplace_editor.DateTimeCtrl, self.onEditCompletionDateTime, [task.Task.expansionChangedEventType()]),
            ('percentageComplete', _('% complete'), inplace_editor.PercentageCtrl, self.onEditPercentageComplete, [task.Task.expansionChangedEventType(), 'task.percentageComplete']),
            ('timeLeft', _('Time left'), None, None, [task.Task.expansionChangedEventType(), 'task.timeLeft']),
            ('recurrence', _('Recurrence'), None, None, [task.Task.expansionChangedEventType(), 'task.recurrence']),
            ('budget', _('Budget'), inplace_editor.BudgetCtrl, self.onEditBudget, [task.Task.expansionChangedEventType(), 'task.budget']),            
            ('timeSpent', _('Time spent'), None, None, [task.Task.expansionChangedEventType(), 'task.timeSpent']),
            ('budgetLeft', _('Budget left'), None, None, [task.Task.expansionChangedEventType(), 'task.budgetLeft']),            
            ('priority', _('Priority'), inplace_editor.PriorityCtrl, self.onEditPriority, [task.Task.expansionChangedEventType(), 'task.priority']),
            ('hourlyFee', _('Hourly fee'), inplace_editor.AmountCtrl, self.onEditHourlyFee, [task.Task.hourlyFeeChangedEventType()]),
            ('fixedFee', _('Fixed fee'), inplace_editor.AmountCtrl, self.onEditFixedFee, [task.Task.expansionChangedEventType(), 'task.fixedFee']),            
            ('revenue', _('Revenue'), None, None, [task.Task.expansionChangedEventType(), 'task.revenue']),
            ('reminder', _('Reminder'), inplace_editor.DateTimeCtrl, self.onEditReminderDateTime, [task.Task.expansionChangedEventType(), 'task.reminder'])]:
            if (name in dependsOnEffortFeature and effortOn) or name not in dependsOnEffortFeature:
                renderCallback = getattr(self, 'render%s'%(name[0].capitalize()+name[1:]))
                columns.append(widgets.Column(name, columnHeader,  
                    sortCallback=uicommand.ViewerSortByCommand(viewer=self, value=name),
                    renderCallback=renderCallback, width=self.getColumnWidth(name),
                    alignment=wx.LIST_FORMAT_RIGHT, editControl=editCtrl, 
                    editCallback=editCallback, *eventTypes, **kwargs))
        return columns
    
    def createColumnUICommands(self):
        commands = [
            uicommand.ToggleAutoColumnResizing(viewer=self,
                                               settings=self.settings),
            None,
            (_('&Dates'),
             uicommand.ViewColumns(menuText=_('&All date columns'),
                helpText=_('Show/hide all date-related columns'),
                setting=['startDateTime', 'dueDateTime', 'timeLeft', 
                         'completionDateTime', 'recurrence'],
                viewer=self),
             None,
             uicommand.ViewColumn(menuText=_('&Start date'),
                 helpText=_('Show/hide start date column'),
                 setting='startDateTime', viewer=self),
             uicommand.ViewColumn(menuText=_('&Due date'),
                 helpText=_('Show/hide due date column'),
                 setting='dueDateTime', viewer=self),
             uicommand.ViewColumn(menuText=_('&Completion date'),
                 helpText=_('Show/hide completion date column'),
                 setting='completionDateTime', viewer=self),
             uicommand.ViewColumn(menuText=_('&Time left'),
                 helpText=_('Show/hide time left column'),
                 setting='timeLeft', viewer=self),
             uicommand.ViewColumn(menuText=_('&Recurrence'),
                 helpText=_('Show/hide recurrence column'),
                 setting='recurrence', viewer=self))]
        if self.settings.getboolean('feature', 'effort'):
            commands.extend([
                (_('&Budget'),
                 uicommand.ViewColumns(menuText=_('&All budget columns'),
                     helpText=_('Show/hide all budget-related columns'),
                     setting=['budget', 'timeSpent', 'budgetLeft'],
                     viewer=self),
                 None,
                 uicommand.ViewColumn(menuText=_('&Budget'),
                     helpText=_('Show/hide budget column'),
                     setting='budget', viewer=self),
                 uicommand.ViewColumn(menuText=_('&Time spent'),
                     helpText=_('Show/hide time spent column'),
                     setting='timeSpent', viewer=self),
                 uicommand.ViewColumn(menuText=_('&Budget left'),
                     helpText=_('Show/hide budget left column'),
                     setting='budgetLeft', viewer=self),
                ),
                (_('&Financial'),
                 uicommand.ViewColumns(menuText=_('&All financial columns'),
                     helpText=_('Show/hide all finance-related columns'),
                     setting=['hourlyFee', 'fixedFee', 'revenue'],
                     viewer=self),
                 None,
                 uicommand.ViewColumn(menuText=_('&Hourly fee'),
                     helpText=_('Show/hide hourly fee column'),
                     setting='hourlyFee', viewer=self),
                 uicommand.ViewColumn(menuText=_('&Fixed fee'),
                     helpText=_('Show/hide fixed fee column'),
                     setting='fixedFee', viewer=self),
                 uicommand.ViewColumn(menuText=_('&Revenue'),
                     helpText=_('Show/hide revenue column'),
                     setting='revenue', viewer=self))])
        commands.extend([
            uicommand.ViewColumn(menuText=_('&Description'),
                helpText=_('Show/hide description column'),
                setting='description', viewer=self),
            ## uicommand.ViewColumn(menuText=_('&Manual ordering'),
            ##     helpText=_('Show/hide manual ordering column'),
            ##     setting='ordering', viewer=self),
            uicommand.ViewColumn(menuText=_('&Prerequisites'),
                 helpText=_('Show/hide prerequisites column'),
                 setting='prerequisites', viewer=self),
            uicommand.ViewColumn(menuText=_('&Dependencies'),
                 helpText=_('Show/hide dependencies column'),
                 setting='dependencies', viewer=self),
             uicommand.ViewColumn(menuText=_('&Percentage complete'),
                 helpText=_('Show/hide percentage complete column'),
                 setting='percentageComplete', viewer=self),
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
            uicommand.ViewColumn(menuText=_('&Priority'),
                helpText=_('Show/hide priority column'),
                setting='priority', viewer=self),
            uicommand.ViewColumn(menuText=_('&Reminder'),
                helpText=_('Show/hide reminder column'),
                setting='reminder', viewer=self)])
        return commands

    def createModeToolBarUICommands(self):
        self.treeOrListUICommand = uicommand.TaskViewerTreeOrListChoice(viewer=self) # pylint: disable-msg=W0201 
        return super(TaskViewer, self).createModeToolBarUICommands() + \
            [self.treeOrListUICommand]

    def createColumnPopupMenu(self):
        return menu.ColumnPopupMenu(self)
                    
    def setSortByTaskStatusFirst(self, *args, **kwargs): # pylint: disable-msg=W0221
        super(TaskViewer, self).setSortByTaskStatusFirst(*args, **kwargs)
        self.showSortOrder()
        
    def getSortOrderImage(self):
        sortOrderImage = super(TaskViewer, self).getSortOrderImage()
        if self.isSortByTaskStatusFirst(): # pylint: disable-msg=E1101
            sortOrderImage = sortOrderImage.rstrip('icon') + 'with_status_icon'
        return sortOrderImage

    def setSearchFilter(self, searchString, *args, **kwargs): # pylint: disable-msg=W0221
        super(TaskViewer, self).setSearchFilter(searchString, *args, **kwargs)
        if searchString:
            self.expandAll() # pylint: disable-msg=E1101      

    def showTree(self, treeMode):
        self.settings.set(self.settingsSection(), 'treemode', str(treeMode))
        self.presentation().setTreeMode(treeMode)
        
    # pylint: disable-msg=W0621
    
    def renderSubject(self, task):
        return task.subject(recursive=not self.isTreeViewer())
    
    @staticmethod
    def renderStartDateTime(task):
        # The rendering of the start date time doesn't depend on whether the
        # task is collapsed since the start date time is a parent is always <=
        # start date times of all children. 
        return render.dateTime(task.startDateTime())
    
    def renderDueDateTime(self, task):
        return self.renderedValue(task, task.dueDateTime, render.dateTime)

    def renderCompletionDateTime(self, task):
        return self.renderedValue(task, task.completionDateTime, render.dateTime)

    def renderRecurrence(self, task):
        return self.renderedValue(task, task.recurrence, render.recurrence)
    
    def renderPrerequisites(self, task):
        return self.renderSubjectsOfRelatedItems(task, task.prerequisites)
    
    def renderDependencies(self, task):
        return self.renderSubjectsOfRelatedItems(task, task.dependencies)
    
    def renderTimeLeft(self, task):
        return self.renderedValue(task, task.timeLeft, render.timeLeft, task.completed())
        
    def renderTimeSpent(self, task):
        return self.renderedValue(task, task.timeSpent, render.timeSpent)

    def renderBudget(self, task):
        return self.renderedValue(task, task.budget, render.budget)

    def renderBudgetLeft(self, task):
        return self.renderedValue(task, task.budgetLeft, render.budget)

    def renderRevenue(self, task):
        return self.renderedValue(task, task.revenue, render.monetaryAmount)
    
    def renderHourlyFee(self, task):
        return render.monetaryAmount(task.hourlyFee()) # hourlyFee has no recursive value
    
    def renderFixedFee(self, task):
        return self.renderedValue(task, task.fixedFee, render.monetaryAmount)

    def renderPercentageComplete(self, task):
        return self.renderedValue(task, task.percentageComplete, render.percentage)

    def renderPriority(self, task):
        return self.renderedValue(task, task.priority, render.priority)
    
    def renderReminder(self, task):
        return self.renderedValue(task, task.reminder, render.dateTime)
    
    def renderedValue(self, item, getValue, renderValue, *extraRenderArgs):
        value = getValue(recursive=False)
        template = '%s'
        if self.isItemCollapsed(item):
            recursiveValue = getValue(recursive=True)
            if value != recursiveValue:
                value = recursiveValue
                template = '(%s)'
        return template%renderValue(value, *extraRenderArgs)
    
    def onEditStartDateTime(self, item, newValue):
        command.EditStartDateTimeCommand(items=[item], newValue=newValue).do()
        
    def onEditDueDateTime(self, item, newValue):
        command.EditDueDateTimeCommand(items=[item], newValue=newValue).do()
        
    def onEditCompletionDateTime(self, item, newValue):
        command.EditCompletionDateTimeCommand(items=[item], newValue=newValue).do()
        
    def onEditPercentageComplete(self, item, newValue):
        command.EditPercentageCompleteCommand(items=[item], newValue=newValue).do()
        
    def onEditBudget(self, item, newValue):
        command.EditBudgetCommand(items=[item], newValue=newValue).do()
        
    def onEditPriority(self, item, newValue):
        command.EditPriorityCommand(items=[item], newValue=newValue).do()
        
    def onEditReminderDateTime(self, item, newValue):
        command.EditReminderDateTimeCommand(items=[item], newValue=newValue).do()
        
    def onEditHourlyFee(self, item, newValue):
        command.EditHourlyFeeCommand(items=[item], newValue=newValue).do()
        
    def onEditFixedFee(self, item, newValue):
        command.EditFixedFeeCommand(items=[item], newValue=newValue).do()

    def onEverySecond(self, event):
        # Only update when a column is visible that changes every second 
        if any([self.isVisibleColumnByName(column) for column in 'timeSpent', 
               'budgetLeft', 'revenue']):
            super(TaskViewer, self).onEverySecond(event)

    def getRootItems(self):
        ''' If the viewer is in tree mode, return the real root items. If the
            viewer is in list mode, return all items. '''
        return super(TaskViewer, self).getRootItems() if \
            self.isTreeViewer() else self.presentation()
    
    def getItemParent(self, item):
        return super(TaskViewer, self).getItemParent(item) if \
            self.isTreeViewer() else None

    def children(self, item=None):
        return super(TaskViewer, self).children(item) if \
            (self.isTreeViewer() or item is None) else []


class CheckableTaskViewer(TaskViewer): # pylint: disable-msg=W0223
    def createWidget(self):
        imageList = self.createImageList() # Has side-effects
        self._columns = self._createColumns()
        itemPopupMenu = self.createTaskPopupMenu()
        columnPopupMenu = self.createColumnPopupMenu()
        self._popupMenus.extend([itemPopupMenu, columnPopupMenu])
        widget = widgets.CheckTreeCtrl(self, self.columns(), self.onSelect,
            self.onCheck, 
            uicommand.Edit(viewer=self),
            uicommand.TaskDragAndDrop(taskList=self.presentation(), viewer=self),
            itemPopupMenu, columnPopupMenu,
            **self.widgetCreationKeywordArguments())
        widget.AssignImageList(imageList) # pylint: disable-msg=E1101
        return widget    
    
    def onCheck(self, *args, **kwargs):
        pass
    
    def getIsItemChecked(self, task): # pylint: disable-msg=W0613,W0621
        return False
    
    def getItemParentHasExclusiveChildren(self, task): # pylint: disable-msg=W0613,W0621
        return False
