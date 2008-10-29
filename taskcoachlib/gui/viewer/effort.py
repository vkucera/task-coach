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
from taskcoachlib.domain import effort, date
from taskcoachlib.i18n import _
from taskcoachlib.gui import uicommand, menu, render, dialog
import base, mixin


class EffortViewer(mixin.SortableViewerForEffort, mixin.SearchableViewer, 
                   base.UpdatePerSecondViewer):
    SorterClass = effort.EffortSorter
    
    def isSortable(self):
        return False # FIXME: make effort viewers sortable too?
    
    def isShowingEffort(self):
        return True
    
    def trackStartEventType(self):
        return 'effort.track.start'
    
    def trackStopEventType(self):
        return 'effort.track.stop'

    def createToolBarUICommands(self):
        commands = super(EffortViewer, self).createToolBarUICommands()
        # This is needed for unit tests
        self.deleteUICommand = uicommand.EffortDelete(viewer=self,
                                                      effortList=self.model())
        commands[-2:-2] = [None,
                           uicommand.EffortNew(viewer=self,
                                               effortList=self.model(),
                                               taskList=self.taskList,
                                               settings=self.settings),
                           uicommand.EffortEdit(viewer=self,
                                                effortList=self.model()),
                           self.deleteUICommand]
        return commands

    def statusMessages(self):
        status1 = _('Effort: %d selected, %d visible, %d total')%\
            (len(self.curselection()), len(self.list), 
             self.list.originalLength())         
        status2 = _('Status: %d tracking')% self.list.nrBeingTracked()
        return status1, status2

    def getItemTooltipData(self, index, column=0):
        if self.settings.getboolean('view', 'descriptionpopups'):
            item = self.getItemWithIndex(index)
            if item.description():
                return [(None, map(lambda x: x.rstrip('\r'), item.description().split('\n')))]
        return []
 
    # See TaskViewer for why the methods below have two names.
    
    def newItemDialog(self, *args, **kwargs):
        selectedTasks = kwargs.get('selectedTasks', [])
        if not selectedTasks:
            subjectDecoratedTaskList = [(task.subject(recursive=True), task) \
                                        for task in self.taskList]
            subjectDecoratedTaskList.sort() # Sort by subject
            selectedTasks = [subjectDecoratedTaskList[0][1]]
        return dialog.editor.EffortEditor(wx.GetTopLevelParent(self), 
            command.NewEffortCommand(self.list, selectedTasks),
            self.list, self.taskList, self.settings, bitmap=kwargs['bitmap'])
        
    newEffortDialog = newItemDialog
    
    def editItemDialog(self, *args, **kwargs):
        return dialog.editor.EffortEditor(wx.GetTopLevelParent(self),
            command.EditEffortCommand(self.list, self.curselection()), 
            self.list, self.taskList, self.settings)
    
    def deleteItemCommand(self):
        return command.DeleteCommand(self.list, self.curselection())
    

class EffortListViewer(base.ListViewer, EffortViewer, base.ViewerWithColumns): 
    defaultTitle = _('Effort')  
    
    def __init__(self, parent, list, *args, **kwargs):
        self.aggregation = 'details'
        self.taskList = domain.base.SearchFilter(list)
        kwargs.setdefault('settingsSection', 'effortlistviewer')
        self.__hiddenTotalColumns = []
        self.__hiddenWeekdayColumns = []
        self.__columnUICommands = None
        super(EffortListViewer, self).__init__(parent, self.taskList, *args, **kwargs)
        self.aggregation = self.settings.get(self.settingsSection(), 'aggregation')
        self.aggregationUICommand.setChoice(self.aggregation)
        self.createColumnUICommands()
        patterns.Publisher().registerObserver(self.onColorChange,
            eventType=effort.Effort.colorChangedEventType())
        
    def onColorChange(self, event):
        effort = event.source()
        if effort in self.model():
            self.widget.RefreshItem(self.getIndexOfItem(effort))
        
    def showEffortAggregation(self, aggregation):
        ''' Change the aggregation mode. Can be one of 'details', 'day', 'week'
            and 'month'. '''
        assert aggregation in ('details', 'day', 'week', 'month')
        self.aggregation = aggregation
        self.settings.set(self.settingsSection(), 'aggregation', aggregation)
        self.setModel(self.createSorter(self.createAggregator(self.taskList, 
                                                            aggregation)))
        self.registerModelObservers()
        # Invalidate the UICommands used for the column popup menu:
        self.__columnUICommands = None
        self.refresh()
        self._showTotalColumns(show=aggregation!='details')
        self._showWeekdayColumns(show=aggregation=='week')

    def createFilter(self, taskList):
        ''' Return a class that filters the original list. In this case we
            create an effort aggregator that aggregates the effort records in
            the taskList, either individually (i.e. no aggregation), per day,
            per week, or per month. '''
        aggregation = self.settings.get(self.settingsSection(), 'aggregation')
        return self.createAggregator(taskList, aggregation)
                
    def createAggregator(self, taskList, aggregation):
        ''' Return an instance of a class that aggregates the effort records 
            in the taskList, either:
            - individually (aggregation == 'details'), 
            - per day (aggregation == 'day'), 
            - per week ('week'), or 
            - per month ('month'). '''
        if aggregation == 'details':
            return effort.EffortList(taskList)
        else:
            return effort.EffortAggregator(taskList, aggregation=aggregation)
                
    def createWidget(self):
        self._columns = self._createColumns()
        widget = widgets.ListCtrl(self, self.columns(),
            self.getItemText, self.getItemTooltipData, self.getItemImage,
            self.getItemAttr, self.onSelect,
            uicommand.EffortEdit(viewer=self, effortList=self.model()),
            menu.EffortPopupMenu(self.parent, self.taskList, self.settings,
                                 self.model(), self),
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
            ('task', _('Task'), 'effort.task', lambda effort: effort.task().subject(recursive=True)),
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
                lambda effort: render.amount(effort.revenue())),
            ('totalTimeSpent', _('Total time spent'), 'effort.totalDuration',  
                 lambda effort: render.timeSpent(effort.duration(recursive=True))),
            ('totalRevenue', _('Total revenue'), 'effort.totalRevenue',
                 lambda effort: render.amount(effort.revenue(recursive=True)))] + \
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
            self.showColumn(column, show)

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
            self.showColumn(column, show)

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
            
    def getToolBarUICommands(self):
        ''' UI commands to put on the toolbar of this viewer. '''
        toolBarUICommands = super(EffortListViewer, self).getToolBarUICommands() 
        toolBarUICommands.insert(-2, None) # Separator
        self.aggregationUICommand = \
            uicommand.EffortViewerAggregationChoice(viewer=self) 
        toolBarUICommands.insert(-2, self.aggregationUICommand)
        return toolBarUICommands

    def getItemImage(self, index, which, column=0):
        return -1
    
    def getBackgroundColor(self, effort):
        return effort.task().color()
    
    def getItemAttr(self, index):
        effort = self.getItemWithIndex(index)
        return wx.ListItemAttr(None, self.getBackgroundColor(effort))

    def curselection(self):
        selection = super(EffortListViewer, self).curselection()
        if self.aggregation != 'details':
            selection = [effort for compositeEffort in selection\
                                for effort in compositeEffort]
        return selection
                
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
        index = self.list.index(effort)
        previousEffort = index > 0 and self.list[index-1] or None
        return previousEffort and effort.getStart() == previousEffort.getStart()

    def renderTimeSpentOnDay(self, effort, dayOffset):
        if self.aggregation == 'week':
            duration = effort.durationDay(dayOffset)
        else:
            duration = date.TimeDelta()
        return render.timeSpent(duration)
