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
from taskcoachlib.domain import effort, date
from taskcoachlib.domain.base import filter
from taskcoachlib.i18n import _
from taskcoachlib.gui import uicommand, menu, render, dialog
import base, mixin


class EffortViewer(base.ListViewer, mixin.SortableViewerForEffort, 
                   mixin.SearchableViewer, base.UpdatePerSecondViewer, 
                   base.ViewerWithColumns): 
    defaultTitle = _('Effort')
    defaultBitmap = 'start'  
    SorterClass = effort.EffortSorter
    
    def __init__(self, *args, **kwargs):
        self.aggregation = 'details'
        self.tasksToShowEffortFor = kwargs.pop('tasksToShowEffortFor', [])
        kwargs.setdefault('settingsSection', 'effortviewer')
        self.__hiddenTotalColumns = []
        self.__hiddenWeekdayColumns = []
        self.__columnUICommands = None
        self.__domainObjectsToView = None
        self.__observersToDetach = []
        super(EffortViewer, self).__init__(*args, **kwargs)
        self.aggregation = self.settings.get(self.settingsSection(), 'aggregation')
        self.aggregationUICommand.setChoice(self.aggregation)
        self.createColumnUICommands()
        patterns.Publisher().registerObserver(self.onColorChange,
            eventType=effort.Effort.colorChangedEventType())
        
    def domainObjectsToView(self):
        if self.__domainObjectsToView is None:
            if self.displayingNewTasks():
                tasks = self.tasksToShowEffortFor
            else:
                tasks = selectedItemsFilter = domain.base.SelectedItemsFilter(self.taskFile.tasks(), 
                                                                              selectedItems=self.tasksToShowEffortFor)
                self.__observersToDetach.append(selectedItemsFilter)
            searchFilter = domain.base.SearchFilter(tasks)
            self.__domainObjectsToView = searchFilter
            self.__observersToDetach.append(searchFilter)
        return self.__domainObjectsToView
    
    def displayingNewTasks(self):
        return any([task not in self.taskFile.tasks() for task in self.tasksToShowEffortFor])
    
    def detach(self):
        super(EffortViewer, self).detach()
        for observer in self.__observersToDetach:
            patterns.Publisher().removeInstance(observer)    
            
    def isSortable(self):
        return False # FIXME: make effort viewers sortable too?
    
    def isShowingEffort(self):
        return True
    
    def trackStartEventType(self):
        return effort.Effort.trackStartEventType()
    
    def trackStopEventType(self):
        return effort.Effort.trackStopEventType()
        
    def onColorChange(self, event):
        self.refreshItem(event.source())
        
    def showEffortAggregation(self, aggregation):
        ''' Change the aggregation mode. Can be one of 'details', 'day', 'week'
            and 'month'. '''
        assert aggregation in ('details', 'day', 'week', 'month')
        self.aggregation = aggregation
        self.settings.set(self.settingsSection(), 'aggregation', aggregation)
        self.setPresentation(self.createSorter(self.createAggregator(\
                             self.domainObjectsToView(), aggregation)))
        self.registerPresentationObservers()
        # Invalidate the UICommands used for the column popup menu:
        self.__columnUICommands = None
        # If the widget is auto-resizing columns, turn it off temporarily to 
        # make removing/adding columns faster
        autoResizing = self.widget.IsAutoResizing()
        if autoResizing:
            self.widget.ToggleAutoResizing(False)
        self._showTotalColumns(show=aggregation!='details')
        self._showWeekdayColumns(show=aggregation=='week')
        if autoResizing:
            self.widget.ToggleAutoResizing(True)
        self.refresh()

    def createFilter(self, taskList):
        ''' Return a class that filters the original list. In this case we
            create an effort aggregator that aggregates the effort records in
            the taskList, either individually (i.e. no aggregation), per day,
            per week, or per month. '''
        aggregation = self.settings.get(self.settingsSection(), 'aggregation')
        return self.createAggregator(filter.DeletedFilter(taskList), aggregation)
    
    def createAggregator(self, taskList, aggregation):
        ''' Return an instance of a class that aggregates the effort records 
            in the taskList, either:
            - individually (aggregation == 'details'), 
            - per day (aggregation == 'day'), 
            - per week ('week'), or 
            - per month ('month'). '''
        if aggregation == 'details':
            result = effort.EffortList(taskList)
        else:
            result = effort.EffortAggregator(taskList, aggregation=aggregation)
        self.__observersToDetach.append(result)
        return result
            
    def createWidget(self):
        self._columns = self._createColumns()
        widget = widgets.ListCtrl(self, self.columns(),
            self.getItemText, self.getItemTooltipData, self.getItemImage,
            self.getItemAttr, self.onSelect,
            uicommand.EffortEdit(viewer=self, effortList=self.presentation()),
            menu.EffortPopupMenu(self.parent, self.taskFile.tasks(), 
                                 self.settings, self.presentation(), self),
            menu.EffortViewerColumnPopupMenu(self),
            resizeableColumn=1, **self.widgetCreationKeywordArguments())
        widget.SetColumnWidth(0, 150)
        return widget
    
    def _createColumns(self):
        return [widgets.Column(name, columnHeader, eventType, 
                renderCallback=renderCallback, width=self.getColumnWidth(name),
                resizeCallback=self.onResizeColumn) \
            for name, columnHeader, eventType, renderCallback in \
            ('period', _('Period'), 'effort.duration', self.renderPeriod),
            ('task', _('Task'), effort.Effort.taskChangedEventType(), lambda effort: effort.task().subject(recursive=True)),
            ('description', _('Description'), effort.Effort.descriptionChangedEventType(), lambda effort: effort.description())] + \
            [widgets.Column('categories', _('Categories'),
             width=self.getColumnWidth('categories'),
             renderCallback=self.renderCategory, 
             renderDescriptionCallback=lambda effort: effort.description(),
             resizeCallback=self.onResizeColumn)] + \
            [widgets.Column('totalCategories', _('Overall categories'),
             width=self.getColumnWidth('totalCategories'),
             renderCallback=lambda effort: self.renderCategory(effort, recursive=True),
             renderDescriptionCallback=lambda effort: effort.description(),
             resizeCallback=self.onResizeColumn)] + \
            [widgets.Column(name, columnHeader, eventType, 
             width=self.getColumnWidth(name), resizeCallback=self.onResizeColumn,
             renderCallback=renderCallback, alignment=wx.LIST_FORMAT_RIGHT) \
            for name, columnHeader, eventType, renderCallback in \
            ('timeSpent', _('Time spent'), 'effort.duration', 
                lambda effort: render.timeSpent(effort.duration())),
            ('revenue', _('Revenue'), 'effort.revenue', 
                lambda effort: render.monetaryAmount(effort.revenue())),
            ('totalTimeSpent', _('Total time spent'), 'effort.totalDuration',  
                 lambda effort: render.timeSpent(effort.duration(recursive=True))),
            ('totalRevenue', _('Total revenue'), 'effort.totalRevenue',
                 lambda effort: render.monetaryAmount(effort.revenue(recursive=True)))] + \
             [widgets.Column(name, columnHeader, eventType, 
              renderCallback=renderCallback, alignment=wx.LIST_FORMAT_RIGHT,
              width=self.getColumnWidth(name), resizeCallback=self.onResizeColumn) \
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

    def getColumnUICommands(self):
        if not self.__columnUICommands:
            self.createColumnUICommands()
        return self.__columnUICommands

    def createColumnUICommands(self):
        self.__columnUICommands = \
            [uicommand.ToggleAutoColumnResizing(viewer=self,
                                                settings=self.settings),
             None,
             uicommand.ViewColumn(menuText=_('&Description'),
                                  helpText=_('Show/hide description column'),
                                  setting='description', viewer=self),
             uicommand.ViewColumn(menuText=_('&Categories'),
                                  helpText=_('Show/hide categories column'),
                                  setting='categories', viewer=self),
             uicommand.ViewColumn(menuText=_('Overall categories'),
                                  helpText=_('Show/hide categories column'),
                                  setting='totalCategories', viewer=self),
             uicommand.ViewColumn(menuText=_('&Time spent'),
                                  helpText=_('Show/hide time spent column'),
                                  setting='timeSpent', viewer=self),
             uicommand.ViewColumn(menuText=_('&Revenue'),
                                  helpText=_('Show/hide revenue column'),
                                  setting='revenue', viewer=self),]
        if self.aggregation != 'details':
            self.__columnUICommands.insert(-1, 
                uicommand.ViewColumn(menuText=_('&Total time spent'),
                    helpText=_('Show/hide total time spent column'),
                    setting='totalTimeSpent',
                    viewer=self))
            self.__columnUICommands.append(\
                uicommand.ViewColumn(menuText=_('Total &revenue'),
                    helpText=_('Show/hide total revenue column'),
                    setting='totalRevenue',
                    viewer=self))
        if self.aggregation == 'week':
            self.__columnUICommands.append(\
                uicommand.ViewColumns(menuText=_('Effort per weekday'),
                    helpText=_('Show/hide time spent per weekday columns'),
                    setting=['monday', 'tuesday', 'wednesday', 'thursday', 
                             'friday', 'saturday', 'sunday'],
                    viewer=self))

    def createToolBarUICommands(self):
        commands = super(EffortViewer, self).createToolBarUICommands()
        # This is an instance variable for use in unit tests
        self.deleteUICommand = uicommand.EffortDelete(viewer=self,
                                                      effortList=self.presentation())
        # This is an instance variable so that the choice can be changed programmatically
        self.aggregationUICommand = \
            uicommand.EffortViewerAggregationChoice(viewer=self)
        for command in [None, 
                        uicommand.EffortNew(viewer=self,
                                            effortList=self.presentation(),
                                            taskList=self.taskFile.tasks(),
                                            settings=self.settings),
                        uicommand.EffortEdit(viewer=self,
                                             effortList=self.presentation()),
                        self.deleteUICommand, 
                        None,
                        self.aggregationUICommand]:
            commands.insert(-2, command)
        return commands

    def getItemImage(self, index, which, column=0):
        return -1
    
    def getBackgroundColor(self, effort):
        return effort.task().color()
    
    def getItemAttr(self, index):
        effort = self.getItemWithIndex(index)
        return wx.ListItemAttr(None, self.getBackgroundColor(effort))

    def getItemTooltipData(self, index, column=0):
        if self.settings.getboolean('view', 'descriptionpopups'):
            item = self.getItemWithIndex(index)
            if item.description():
                return [(None, map(lambda x: x.rstrip('\r'), item.description().split('\n')))]
        return []
    
    def curselection(self):
        selection = super(EffortViewer, self).curselection()
        if self.aggregation != 'details':
            selection = [effort for compositeEffort in selection\
                                for effort in compositeEffort]
        return selection

    def isselected(self, item):
        """When this viewer is in aggregation mode, L{curselection}
        returns the actual underlying L{Effort} objects instead of
        aggregates. This is a problem e.g. when exporting only a
        selection, since items we're iterating over (aggregates) are
        never in curselection(). This method is used instead. It just
        ignores the overriden version of curselection."""

        return item in super(EffortViewer, self).curselection()

    def statusMessages(self):
        status1 = _('Effort: %d selected, %d visible, %d total')%\
            (len(self.curselection()), len(self.presentation()), 
             self.presentation().originalLength())         
        status2 = _('Status: %d tracking')% self.presentation().nrBeingTracked()
        return status1, status2

    def renderPeriod(self, effort):
        if self._hasRepeatedPeriod(effort):
            return ''
        start = effort.getStart()
        if self.aggregation == 'details':
            return render.dateTimePeriod(start, effort.getStop())
        elif self.aggregation == 'day':
            return render.date(start.date())
        elif self.aggregation == 'week':
            return render.weekNumber(start)
        elif self.aggregation == 'month':
            return render.month(start)
            
    def _hasRepeatedPeriod(self, effort):
        ''' Return whether the effort has the same period as the previous 
            effort record. '''
        index = self.presentation().index(effort)
        previousEffort = index > 0 and self.presentation()[index-1] or None
        return previousEffort and effort.getStart() == previousEffort.getStart()

    def renderTimeSpentOnDay(self, effort, dayOffset):
        if self.aggregation == 'week':
            duration = effort.durationDay(dayOffset)
        else:
            duration = date.TimeDelta()
        return render.timeSpent(duration)
    
    # See TaskViewer for why the methods below have two names.
    
    def newItemDialog(self, *args, **kwargs):
        selectedTasks = kwargs.get('selectedTasks', [])
        bitmap = kwargs.get('bitmap', 'new')
        if not selectedTasks:
            subjectDecoratedTaskList = [(task.subject(recursive=True), task) \
                                        for task in self.tasksToShowEffortFor]
            subjectDecoratedTaskList.sort() # Sort by subject
            selectedTasks = [subjectDecoratedTaskList[0][1]]
        return dialog.editor.EffortEditor(wx.GetTopLevelParent(self), 
            command.NewEffortCommand(self.presentation(), selectedTasks),
            self.taskFile, self.settings, bitmap=bitmap)
        
    newEffortDialog = newItemDialog
    
    def editItemDialog(self, *args, **kwargs):
        return dialog.editor.EffortEditor(wx.GetTopLevelParent(self),
            command.EditEffortCommand(self.presentation(), self.curselection()), 
            self.taskFile, self.settings, 
            columnName=kwargs.get('columnName', ''))
    
    def deleteItemCommand(self):
        return command.DeleteCommand(self.presentation(), self.curselection())
    

