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
from taskcoachlib.domain import effort, date
from taskcoachlib.domain.base import filter # pylint: disable-msg=W0622
from taskcoachlib.i18n import _
from taskcoachlib.gui import uicommand, menu, dialog
import base, mixin, refresher


class EffortViewer(base.ListViewer, 
                   mixin.FilterableViewerForCategorizablesMixin, 
                   mixin.SortableViewerForEffortMixin, 
                   mixin.SearchableViewerMixin, base.SortableViewerWithColumns): 
    defaultTitle = _('Effort')
    defaultBitmap = 'clock_icon'
    SorterClass = effort.EffortSorter
    
    def __init__(self, parent, taskFile, settings, *args, **kwargs):        
        kwargs.setdefault('settingsSection', 'effortviewer')
        self.tasksToShowEffortFor = kwargs.pop('tasksToShowEffortFor', [])
        self.aggregation = 'details' # Temporary value, will be properly set below
        self.__hiddenWeekdayColumns = []
        self.__hiddenTotalColumns = []
        self.__columnUICommands = None
        self.__domainObjectsToView = None
        self.__observersToDetach = []
        super(EffortViewer, self).__init__(parent, taskFile, settings, *args, **kwargs)
        self.secondRefresher = refresher.SecondRefresher(self,
            effort.Effort.trackStartEventType(), 
            effort.Effort.trackStopEventType())
        self.aggregation = settings.get(self.settingsSection(), 'aggregation')
        self.initModeToolBarUICommands()
        patterns.Publisher().registerObserver(self.onAttributeChanged,
                                              eventType=effort.Effort.appearanceChangedEventType())
        patterns.Publisher().registerObserver(self.onRoundingChanged,
                                              eventType='%s.round'%self.settingsSection())
        
    def onRoundingChanged(self, event): # pylint: disable-msg=W0613
        self.refresh()
        
    def initModeToolBarUICommands(self):
        self.aggregationUICommand.setChoice(self.aggregation)
        self.initRoundingToolBarUICommand()
        
    def initRoundingToolBarUICommand(self):
        aggregated = self.isShowingAggregatedEffort()
        rounding = self.settings.get(self.settingsSection(), 'round') if aggregated else '0'
        self.roundingUICommand.setChoice(rounding)
        self.roundingUICommand.enable(aggregated)
        
    def domainObjectsToView(self):
        if self.__domainObjectsToView is None:
            if self.displayingNewTasks():
                tasks = self.tasksToShowEffortFor
            else:
                tasks = selectedItemsFilter = domain.base.SelectedItemsFilter(self.taskFile.tasks(), 
                                                                              selectedItems=self.tasksToShowEffortFor)
                self.__observersToDetach.append(selectedItemsFilter)
            self.__domainObjectsToView = tasks
        return self.__domainObjectsToView
    
    def displayingNewTasks(self):
        return any([task not in self.taskFile.tasks() for task in self.tasksToShowEffortFor])
    
    def detach(self):
        super(EffortViewer, self).detach()
        patterns.Publisher().removeInstance(self.secondRefresher)
        for observer in self.__observersToDetach:
            patterns.Publisher().removeInstance(observer)    
            
    def isShowingEffort(self):
        return True
    
    def curselectionIsInstanceOf(self, class_):
        return class_ == effort.Effort
    
    def showEffortAggregation(self, aggregation):
        ''' Change the aggregation mode. Can be one of 'details', 'day', 'week'
            and 'month'. '''
        assert aggregation in ('details', 'day', 'week', 'month')
        self.aggregation = aggregation
        self.settings.set(self.settingsSection(), 'aggregation', aggregation)
        self.setPresentation(self.createSorter(self.createFilter(\
                             self.domainObjectsToView())))
        self.secondRefresher.updatePresentation()
        self.registerPresentationObservers()
        # Invalidate the UICommands used for the column popup menu:
        self.__columnUICommands = None
        # Clear the selection to remove the cached selection
        self.clearselection()
        # If the widget is auto-resizing columns, turn it off temporarily to 
        # make removing/adding columns faster
        autoResizing = self.widget.IsAutoResizing()
        if autoResizing:
            self.widget.ToggleAutoResizing(False)
        # Refresh first so that the list control doesn't think there are more
        # efforts than there really are when switching from aggregate mode to
        # detail mode.
        self.refresh()
        self._showWeekdayColumns(show=aggregation=='week')
        self._showTotalColumns(show=aggregation!='details')
        if autoResizing:
            self.widget.ToggleAutoResizing(True)
        self.initRoundingToolBarUICommand()
        patterns.Event('effortviewer.aggregation').send()
            
    def isShowingAggregatedEffort(self):
        return self.aggregation != 'details'
    
    def createFilter(self, taskList):
        ''' Return a class that filters the original list. In this case we
            create an effort aggregator that aggregates the effort records in
            the taskList, either individually (i.e. no aggregation), per day,
            per week, or per month. '''
        aggregation = self.settings.get(self.settingsSection(), 'aggregation')
        deletedFilter = filter.DeletedFilter(taskList)
        categoryFilter = super(EffortViewer, self).createFilter(deletedFilter)
        searchFilter = filter.SearchFilter(self.createAggregator(categoryFilter, aggregation))
        self.__observersToDetach.extend([deletedFilter, categoryFilter, searchFilter])
        return searchFilter
    
    def createAggregator(self, taskList, aggregation):
        ''' Return an instance of a class that aggregates the effort records 
            in the taskList, either:
            - individually (aggregation == 'details'), 
            - per day (aggregation == 'day'), 
            - per week ('week'), or 
            - per month ('month'). '''
        if aggregation == 'details':
            aggregator = effort.EffortList(taskList)
        else:
            aggregator = effort.EffortAggregator(taskList, aggregation=aggregation)
        self.__observersToDetach.append(aggregator)
        return aggregator
            
    def createWidget(self):
        imageList = self.createImageList() # Has side-effects
        self._columns = self._createColumns()
        itemPopupMenu = menu.EffortPopupMenu(self.parent, self.taskFile.tasks(),
            self.taskFile.efforts(), self.settings, self)
        columnPopupMenu = menu.EffortViewerColumnPopupMenu(self)
        self._popupMenus.extend([itemPopupMenu, columnPopupMenu])
        widget = widgets.ListCtrl(self, self.columns(), self.onSelect,
            uicommand.Edit(viewer=self),
            itemPopupMenu, columnPopupMenu,
            resizeableColumn=1, **self.widgetCreationKeywordArguments())
        widget.AssignImageList(imageList, wx.IMAGE_LIST_SMALL) # pylint: disable-msg=E1101
        return widget
    
    def _createColumns(self):
        # pylint: disable-msg=W0142
        kwargs = dict(renderDescriptionCallback=lambda effort: effort.description(),
                      resizeCallback=self.onResizeColumn)
        return [widgets.Column(name, columnHeader, eventType, 
                renderCallback=renderCallback,
                sortCallback=sortCallback,
                width=self.getColumnWidth(name), **kwargs) \
            for name, columnHeader, eventType, renderCallback, sortCallback in \
            ('period', _('Period'), 'effort.duration', self.renderPeriod, 
             uicommand.ViewerSortByCommand(viewer=self, value='period')),
            ('task', _('Task'), effort.Effort.taskChangedEventType(), lambda effort: effort.task().subject(recursive=True), None),
            ('description', _('Description'), effort.Effort.descriptionChangedEventType(), lambda effort: effort.description(), None)] + \
            [widgets.Column('categories', _('Categories'),
             width=self.getColumnWidth('categories'),
             renderCallback=self.renderCategories, **kwargs)] + \
            [widgets.Column(name, columnHeader, eventType, 
             width=self.getColumnWidth(name),
             renderCallback=renderCallback, alignment=wx.LIST_FORMAT_RIGHT,
             **kwargs) \
            for name, columnHeader, eventType, renderCallback in \
            ('timeSpent', _('Time spent'), 'effort.duration', self.renderTimeSpent),
            ('totalTimeSpent', _('Total time spent'), 'effort.duration', self.renderTotalTimeSpent),
            ('revenue', _('Revenue'), 'effort.revenue', 
                lambda effort: render.monetaryAmount(effort.revenue())),
            ('totalRevenue', _('Total revenue'), 'effort.revenue',
                lambda effort: render.monetaryAmount(effort.revenue(recursive=True)))] + \
             [widgets.Column(name, columnHeader, eventType, 
              renderCallback=renderCallback, alignment=wx.LIST_FORMAT_RIGHT,
              width=self.getColumnWidth(name), **kwargs) \
             for name, columnHeader, eventType, renderCallback in \
                ('monday', _('Monday'), 'effort.duration',  
                 lambda effort: self.renderTimeSpentOnDay(effort, 0)),                             
                ('tuesday', _('Tuesday'), 'effort.duration',  
                 lambda effort: self.renderTimeSpentOnDay(effort, 1)),
                ('wednesday', _('Wednesday'), 'effort.duration',  
                 lambda effort: self.renderTimeSpentOnDay(effort, 2)),
                ('thursday', _('Thursday'), 'effort.duration',  
                 lambda effort: self.renderTimeSpentOnDay(effort, 3)),
                ('friday', _('Friday'), 'effort.duration',  
                 lambda effort: self.renderTimeSpentOnDay(effort, 4)),
                ('saturday', _('Saturday'), 'effort.duration',  
                 lambda effort: self.renderTimeSpentOnDay(effort, 5)),
                ('sunday', _('Sunday'), 'effort.duration',  
                 lambda effort: self.renderTimeSpentOnDay(effort, 6))      
             ]

    def _showWeekdayColumns(self, show=True):
        if show:
            columnsToShow = self.__hiddenWeekdayColumns[:]
            self.__hiddenWeekdayColumns = []
        else:
            self.__hiddenWeekdayColumns = columnsToShow = \
                [column for column in self.visibleColumns() \
                 if column.name() in ['monday', 'tuesday', 'wednesday', 
                 'thursday', 'friday', 'saturday', 'sunday']]
        for column in columnsToShow:
            self.showColumn(column, show, refresh=False)

    def _showTotalColumns(self, show=True):
        if show:
            columnsToShow = self.__hiddenTotalColumns[:]
            self.__hiddenTotalColumns = []
        else:
            self.__hiddenTotalColumns = columnsToShow = \
                [column for column in self.visibleColumns() \
                 if column.name().startswith('total')]
        for column in columnsToShow:
            self.showColumn(column, show, refresh=False)
            
    def getColumnUICommands(self):
        # Create new UI commands every time since the UI commands depend on the
        # aggregation mode
        columnUICommands = \
            [uicommand.ToggleAutoColumnResizing(viewer=self,
                                                settings=self.settings),
             None,
             uicommand.ViewColumn(menuText=_('&Description'),
                                  helpText=_('Show/hide description column'),
                                  setting='description', viewer=self),
             uicommand.ViewColumn(menuText=_('&Categories'),
                                  helpText=_('Show/hide categories column'),
                                  setting='categories', viewer=self),
             uicommand.ViewColumn(menuText=_('&Time spent'),
                                  helpText=_('Show/hide time spent column'),
                                  setting='timeSpent', viewer=self),
             uicommand.ViewColumn(menuText=_('&Revenue'),
                                  helpText=_('Show/hide revenue column'),
                                  setting='revenue', viewer=self),]
        if self.aggregation != 'details':
            columnUICommands.insert(5,
                uicommand.ViewColumn(menuText=_('&Total time spent'),
                                     helpText=_('Show/hide total time spent column'),
                                     setting='totalTimeSpent', viewer=self))
            columnUICommands.insert(7,
                uicommand.ViewColumn(menuText=_('&Total revenue'),
                                     helpText=_('Show/hide total revenue column'),
                                     setting='totalRevenue', viewer=self))
        if self.aggregation == 'week':
            columnUICommands.append(\
                uicommand.ViewColumns(menuText=_('Effort per weekday'),
                    helpText=_('Show/hide time spent per weekday columns'),
                    setting=['monday', 'tuesday', 'wednesday', 'thursday', 
                             'friday', 'saturday', 'sunday'],
                    viewer=self))
        return columnUICommands
    
    def createCreationToolBarUICommands(self):
        return (uicommand.EffortNew(viewer=self, effortList=self.presentation(),
                                    taskList=self.taskFile.tasks(), 
                                    settings=self.settings),)
        
    def createActionToolBarUICommands(self):
        tasks = self.taskFile.tasks()
        return (uicommand.EffortStartForEffort(viewer=self, taskList=tasks),
                uicommand.EffortStop(effortList=self.taskFile.efforts(), 
                                     taskList=tasks))
                
    def createModeToolBarUICommands(self):
        # This is an instance variable so that the choice can be changed 
        # programmatically
        self.aggregationUICommand = \
            uicommand.EffortViewerAggregationChoice(viewer=self)
        self.roundingUICommand = uicommand.RoundingPrecision(viewer=self, settings=self.settings)
        return (self.aggregationUICommand, self.roundingUICommand)

    def getItemImages(self, index, column=0): # pylint: disable-msg=W0613
        return {wx.TreeItemIcon_Normal: -1}
    
    def curselection(self):
        selection = super(EffortViewer, self).curselection()
        if self.aggregation != 'details':
            selection = [anEffort for compositeEffort in selection\
                                for anEffort in compositeEffort]
        return selection
    
    def getIndexOfItem(self, item):
        if self.aggregation == 'details':
            return super(EffortViewer, self).getIndexOfItem(item)
        for index, compositeEffort in enumerate(self.presentation()):
            if item == compositeEffort or item in compositeEffort:
                return index
        return -1

    def isselected(self, item):
        ''' When this viewer is in aggregation mode, L{curselection}
            returns the actual underlying L{Effort} objects instead of
            aggregates. This is a problem e.g. when exporting only a
            selection, since items we're iterating over (aggregates) are
            never in curselection(). This method is used instead. It just
            ignores the overriden version of curselection. '''

        return item in super(EffortViewer, self).curselection()

    def statusMessages(self):
        status1 = _('Effort: %d selected, %d visible, %d total')%\
            (len(self.curselection()), len(self.presentation()), 
             len(self.taskFile.efforts()))         
        status2 = _('Status: %d tracking')% self.presentation().nrBeingTracked()
        return status1, status2
    
    renderers = dict(details=lambda anEffort: render.dateTimePeriod(anEffort.getStart(), anEffort.getStop()),
                     day=lambda anEffort: render.date(anEffort.getStart().date()),
                     week=lambda anEffort: render.weekNumber(anEffort.getStart()),
                     month=lambda anEffort: render.month(anEffort.getStart()))

    def renderPeriod(self, anEffort):
        return '' if self._hasRepeatedPeriod(anEffort) else self.renderers[self.aggregation](anEffort)
                    
    def _hasRepeatedPeriod(self, anEffort):
        ''' Return whether the effort has the same period as the previous 
            effort record. '''
        index = self.presentation().index(anEffort)
        previousEffort = index > 0 and self.presentation()[index-1] or None
        if not previousEffort:
            return False
        if anEffort.getStart() != previousEffort.getStart():
            return False # Starts are not equal, so period cannot be repeated
        if self.isShowingAggregatedEffort():
            return True # Starts are equal and length of period is equal, so period is repeated
        # If we get here, we are in details mode and the starts are equal 
        # Period can only be repeated when the stop times are also equal
        return anEffort.getStop() == previousEffort.getStop()
    
    def renderTimeSpent(self, anEffort):
        duration = anEffort.duration()
        # Check for aggregation because we never round in details mode
        if self.isShowingAggregatedEffort():
            duration = self.round(duration)
            showSeconds = self.settings.getint(self.settingsSection(), 'round') == 0
        else:
            showSeconds = True
        return render.timeSpent(duration, showSeconds=showSeconds)

    def renderTotalTimeSpent(self, anEffort):
        # No need to check for aggregation because this method is only used
        # in aggregated mode
        showSeconds = self.settings.getint(self.settingsSection(), 'round') == 0
        return render.timeSpent(self.round(anEffort.duration(recursive=True)), showSeconds=showSeconds)
    
    def renderTimeSpentOnDay(self, anEffort, dayOffset):
        duration = anEffort.durationDay(dayOffset) if self.aggregation == 'week' else date.TimeDelta()
        showSeconds = self.settings.getint(self.settingsSection(), 'round') == 0
        return render.timeSpent(self.round(duration), showSeconds=showSeconds)
    
    def round(self, duration):
        round_precision = self.settings.getint(self.settingsSection(), 'round')
        return duration.round(seconds=round_precision)
    
    def newItemDialog(self, *args, **kwargs):
        selectedTasks = kwargs.get('selectedTasks', [])
        bitmap = kwargs.get('bitmap', 'new')
        if not selectedTasks:
            subjectDecoratedTaskList = [(task.subject(recursive=True), task) \
                                        for task in self.tasksToShowEffortFor]
            subjectDecoratedTaskList.sort() # Sort by subject
            selectedTasks = [subjectDecoratedTaskList[0][1]]
        return super(EffortViewer, self).newItemDialog(selectedTasks, bitmap=bitmap)
        
    def itemEditorClass(self):
        return dialog.editor.EffortEditor
    
    def newItemCommandClass(self):
        return command.NewEffortCommand
    
    def newSubItemCommandClass(self):
        pass # efforts are not composite.

    def deleteItemCommandClass(self):
        return command.DeleteEffortCommand
    
