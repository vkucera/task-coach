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

from taskcoachlib import command, patterns
from taskcoachlib.domain import base, task, category, attachment
from taskcoachlib.i18n import _
from taskcoachlib.gui import uicommand


class SearchableViewerMixin(object):
    ''' A viewer that is searchable. This is a mixin class. '''

    def isSearchable(self):
        return True
    
    def createFilter(self, presentation):
        presentation = super(SearchableViewerMixin, self).createFilter(presentation)
        return base.SearchFilter(presentation, **self.searchOptions())

    def searchOptions(self):
        searchString, matchCase, includeSubItems, searchDescription = self.getSearchFilter()
        return dict(searchString=searchString, 
                    matchCase=matchCase, 
                    includeSubItems=includeSubItems, 
                    searchDescription=searchDescription,
                    treeMode=self.isTreeViewer())
    
    def setSearchFilter(self, searchString, matchCase=False, 
                        includeSubItems=False, searchDescription=False):
        section = self.settingsSection()
        self.settings.set(section, 'searchfilterstring', searchString)
        self.settings.set(section, 'searchfiltermatchcase', str(matchCase))
        self.settings.set(section, 'searchfilterincludesubitems', str(includeSubItems))
        self.settings.set(section, 'searchdescription', str(searchDescription))
        self.presentation().setSearchFilter(searchString, matchCase=matchCase, 
                                            includeSubItems=includeSubItems,
                                            searchDescription=searchDescription)
        
    def getSearchFilter(self):
        section = self.settingsSection()
        searchString = self.settings.get(section, 'searchfilterstring')
        matchCase = self.settings.getboolean(section, 'searchfiltermatchcase')
        includeSubItems = self.settings.getboolean(section, 'searchfilterincludesubitems')
        searchDescription = self.settings.getboolean(section, 'searchdescription')
        return searchString, matchCase, includeSubItems, searchDescription
    
    def createToolBarUICommands(self):
        ''' UI commands to put on the toolbar of this viewer. '''
        searchUICommand = uicommand.Search(viewer=self, settings=self.settings)
        return super(SearchableViewerMixin, self).createToolBarUICommands() + \
            [None, searchUICommand]
            

class FilterableViewerMixin(object):
    ''' A viewer that is filterable. This is a mixin class. '''

    def isFilterable(self):
        return True
    

class FilterableViewerForNotesMixin(FilterableViewerMixin):
    def createFilter(self, notesContainer):
        notesContainer = super(FilterableViewerForNotesMixin, self).createFilter(notesContainer)
        return category.filter.CategoryFilter(notesContainer, 
            categories=self.taskFile.categories(), treeMode=self.isTreeViewer(),
            filterOnlyWhenAllCategoriesMatch=self.settings.getboolean('view',
            'categoryfiltermatchall'))
        
            
class FilterableViewerForTasksMixin(FilterableViewerMixin):
    def __init__(self, *args, **kwargs):
        self.__filterUICommands = None
        super(FilterableViewerForTasksMixin, self).__init__(*args, **kwargs)

    def createFilter(self, taskList):
        taskList = super(FilterableViewerForTasksMixin, self).createFilter(taskList)
        return category.filter.CategoryFilter( \
            task.filter.ViewFilter(taskList, treeMode=self.isTreeViewer(), 
                                   **self.viewFilterOptions()), 
            categories=self.taskFile.categories(), treeMode=self.isTreeViewer(),
            filterOnlyWhenAllCategoriesMatch=self.settings.getboolean('view',
            'categoryfiltermatchall'))
    
    def viewFilterOptions(self):
        options = dict(dueDateFilter=self.getFilteredByDueDate(),
                       hideActiveTasks=self.isHidingActiveTasks(),
                       hideCompletedTasks=self.isHidingCompletedTasks(),
                       hideInactiveTasks=self.isHidingInactiveTasks(),
                       hideOverdueTasks=self.isHidingOverdueTasks(),
                       hideOverBudgetTasks=self.isHidingOverbudgetTasks(),
                       hideCompositeTasks=self.isHidingCompositeTasks())
        return options
    
    def isFilteredByDueDate(self, dueDateString):
        return dueDateString == self.settings.get(self.settingsSection(), 
                                                  'tasksdue')
    
    def setFilteredByDueDate(self, dueDateString):
        self.settings.set(self.settingsSection(), 'tasksdue', dueDateString)
        self.presentation().setFilteredByDueDate(dueDateString)
        
    def getFilteredByDueDate(self):
        return self.settings.get(self.settingsSection(), 'tasksdue')
    
    def hideActiveTasks(self, hide=True):
        self.__setBooleanSetting('hideactivetasks', hide)
        self.presentation().hideActiveTasks(hide)
        
    def isHidingActiveTasks(self):
        return self.__getBooleanSetting('hideactivetasks')

    def hideInactiveTasks(self, hide=True):
        self.__setBooleanSetting('hideinactivetasks', hide)
        self.presentation().hideInactiveTasks(hide)
        
    def isHidingInactiveTasks(self):
        return self.__getBooleanSetting('hideinactivetasks')
    
    def hideCompletedTasks(self, hide=True):
        self.__setBooleanSetting('hidecompletedtasks', hide)
        self.presentation().hideCompletedTasks(hide)
        
    def isHidingCompletedTasks(self):
        return self.__getBooleanSetting('hidecompletedtasks')
    
    def hideOverdueTasks(self, hide=True):
        self.__setBooleanSetting('hideoverduetasks', hide)
        self.presentation().hideOverdueTasks(hide)
        
    def isHidingOverdueTasks(self):
        return self.__getBooleanSetting('hideoverduetasks')
    
    def hideOverbudgetTasks(self, hide=True):
        self.__setBooleanSetting('hideoverbudgettasks', hide)
        self.presentation().hideOverbudgetTasks(hide)
    
    def isHidingOverbudgetTasks(self):
        return self.__getBooleanSetting('hideoverbudgettasks')
    
    def hideCompositeTasks(self, hide=True):
        self.__setBooleanSetting('hidecompositetasks', hide)
        self.presentation().hideCompositeTasks(hide)
        
    def isHidingCompositeTasks(self):
        return self.__getBooleanSetting('hidecompositetasks')
    
    def resetFilter(self):
        self.hideActiveTasks(False)
        self.hideInactiveTasks(False)
        self.hideCompletedTasks(False)
        self.hideOverdueTasks(False)
        self.hideOverbudgetTasks(False)
        self.hideCompositeTasks(False)
        self.setFilteredByDueDate('Unlimited')
        for eachCategory in self.taskFile.categories():
            eachCategory.setFiltered(False)
        
    def getFilterUICommands(self):
        if not self.__filterUICommands:
            self.__filterUICommands = self.createFilterUICommands()
        return self.__filterUICommands

    def createFilterUICommands(self):
        def dueDateFilter(menuText, helpText, value):
            return uicommand.ViewerFilterByDueDate(menuText=menuText, 
                                                   helpText=helpText,
                                                   value=value, viewer=self)
        dueDateFilterCommands = (_('Show only tasks &due before end of'),
            dueDateFilter(_('&Unlimited'), _('Show all tasks'), 'Unlimited'),
            dueDateFilter(_('&Today'),_('Only show tasks due today'), 'Today'),
            dueDateFilter(_('T&omorrow'),
                          _('Only show tasks due today and tomorrow'), 
                          'Tomorrow'),
            dueDateFilter(_('Wo&rkweek'), 
                          _('Only show tasks due this work week (i.e. before Friday)'),
                          'Workweek'),
            dueDateFilter(_('&Week'), 
                          _('Only show tasks due this week (i.e. before Sunday)'),
                          'Week'),
            dueDateFilter(_('&Month'), _('Only show tasks due this month'), 
                          'Month'),
            dueDateFilter(_('&Year'), _('Only show tasks due this year'),
                          'Year'))
        statusFilterCommands = [_('&Hide tasks that are'),
            uicommand.ViewerHideActiveTasks(viewer=self),
            uicommand.ViewerHideInactiveTasks(viewer=self),
            uicommand.ViewerHideCompletedTasks(viewer=self),
            None,
            uicommand.ViewerHideOverdueTasks(viewer=self),
            uicommand.ViewerHideCompositeTasks(viewer=self)]
        if self.settings.getboolean('feature', 'effort'):
            statusFilterCommands.insert(-2,
                uicommand.ViewerHideOverbudgetTasks(viewer=self))
        return [uicommand.ResetFilter(viewer=self), None, dueDateFilterCommands, 
                tuple(statusFilterCommands)]

    def __getBooleanSetting(self, setting):
        return self.settings.getboolean(self.settingsSection(), setting)
    
    def __setBooleanSetting(self, setting, booleanValue):
        self.settings.setboolean(self.settingsSection(), setting, booleanValue)
        
                
class SortableViewerMixin(object):
    ''' A viewer that is sortable. This is a mixin class. '''

    def __init__(self, *args, **kwargs):
        self._sortUICommands = []
        super(SortableViewerMixin, self).__init__(*args, **kwargs)

    def isSortable(self):
        return True

    def registerPresentationObservers(self):
        super(SortableViewerMixin, self).registerPresentationObservers()
        patterns.Publisher().registerObserver(self.onPresentationChanged, 
            eventType=self.presentation().sortEventType(),
            eventSource=self.presentation())

    def createSorter(self, presentation):
        return self.SorterClass(presentation, **self.sorterOptions())
    
    def sorterOptions(self):
        return dict(sortBy=self.sortKey(),
                    sortAscending=self.isSortOrderAscending(),
                    sortCaseSensitive=self.isSortCaseSensitive())
        
    def sortBy(self, sortKey):
        if self.isSortedBy(sortKey):
            self.setSortOrderAscending(not self.isSortOrderAscending())
        else:
            self.settings.set(self.settingsSection(), 'sortby', sortKey)
            self.presentation().sortBy(sortKey)
        
    def isSortedBy(self, sortKey):
        return sortKey == self.sortKey()

    def sortKey(self):
        return self.settings.get(self.settingsSection(), 'sortby')
    
    def isSortOrderAscending(self):
        return self.settings.getboolean(self.settingsSection(), 
            'sortascending')
    
    def setSortOrderAscending(self, ascending=True):
        self.settings.set(self.settingsSection(), 'sortascending', 
            str(ascending))
        self.presentation().sortAscending(ascending)
        
    def isSortCaseSensitive(self):
        return self.settings.getboolean(self.settingsSection(), 
            'sortcasesensitive')
        
    def setSortCaseSensitive(self, caseSensitive=True):
        self.settings.set(self.settingsSection(), 'sortcasesensitive', 
            str(caseSensitive))
        self.presentation().sortCaseSensitive(caseSensitive)

    def getSortUICommands(self):
        if not self._sortUICommands:
            self.createSortUICommands()
        return self._sortUICommands

    def createSortUICommands(self):
        ''' (Re)Create the UICommands for sorting. These UICommands are put
            in the View->Sort menu and are used when the user clicks a column
            header. '''
        self._sortUICommands = []


class SortableViewerForTasksMixin(SortableViewerMixin):
    SorterClass = task.sorter.Sorter
    
    def __init__(self, *args, **kwargs):
        self.__sortKeyUnchangedCount = 0
        super(SortableViewerForTasksMixin, self).__init__(*args, **kwargs)
    
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
        super(SortableViewerForTasksMixin, self).sortBy(sortKey)

    def isSortByTaskStatusFirst(self):
        return self.settings.getboolean(self.settingsSection(),
            'sortbystatusfirst')
        
    def setSortByTaskStatusFirst(self, sortByTaskStatusFirst):
        self.settings.set(self.settingsSection(), 'sortbystatusfirst',
            str(sortByTaskStatusFirst))
        self.presentation().sortByTaskStatusFirst(sortByTaskStatusFirst)
        
    def sorterOptions(self):
        options = super(SortableViewerForTasksMixin, self).sorterOptions()
        options.update(treeMode=self.isTreeViewer(), 
            sortByTaskStatusFirst=self.isSortByTaskStatusFirst())
        return options

    def createSortUICommands(self):
        self._sortUICommands = \
            [uicommand.ViewerSortOrderCommand(viewer=self),
             uicommand.ViewerSortCaseSensitive(viewer=self),
             uicommand.ViewerSortByTaskStatusFirst(viewer=self),
             None]
        effortOn = self.settings.getboolean('feature', 'effort')
        dependsOnEffortFeature = ['budget', 'totalBudget', 
                                  'timeSpent', 'totalTimeSpent',
                                  'budgetLeft', 'totalBudgetLeft', 
                                  'hourlyFee', 'fixedFee', 'totalFixedFee',
                                  'revenue', 'totalRevenue']
        for menuText, helpText, value in [\
            (_('Sub&ject'), _('Sort tasks by subject'), 'subject'),
            (_('&Description'), _('Sort by description'), 'description'),
            (_('&Category'), _('Sort by category'), 'categories'),
            (_('Overall categories'), _('Sort by overall categories'), 'totalCategories'),
            (_('&Start date'), _('Sort tasks by start date'), 'startDate'),
            (_('&Due date'), _('Sort tasks by due date'), 'dueDate'),
            (_('&Completion date'), _('Sort tasks by completion date'), 'completionDate'),
            (_('D&ays left'), _('Sort tasks by number of days left'), 'timeLeft'),
            (_('&Percentage complete'), _('Sort tasks by percentage complete'), 'percentageComplete'),
            (_('&Overall percentage complete'), _('Sort tasks by overall percentage complete'), 'totalPercentageComplete'),
            (_('&Recurrence'), _('Sort tasks by recurrence'), 'recurrence'),
            (_('&Budget'), _('Sort tasks by budget'), 'budget'),
            (_('Total b&udget'), _('Sort tasks by total budget'), 'totalBudget'),
            (_('&Time spent'), _('Sort tasks by time spent'), 'timeSpent'),
            (_('T&otal time spent'), _('Sort tasks by total time spent'), 'totalTimeSpent'),
            (_('Budget &left'), _('Sort tasks by budget left'), 'budgetLeft'),
            (_('Total budget l&eft'), _('Sort tasks by total budget left'), 'totalBudgetLeft'),
            (_('&Priority'), _('Sort tasks by priority'), 'priority'),
            (_('Overall priority'), _('Sort tasks by overall priority'), 'totalPriority'),
            (_('&Hourly fee'), _('Sort tasks by hourly fee'), 'hourlyFee'),
            (_('&Fixed fee'), _('Sort tasks by fixed fee'), 'fixedFee'),
            (_('Total fi&xed fee'), _('Sort tasks by total fixed fee'), 'totalFixedFee'),
            (_('&Revenue'), _('Sort tasks by revenue'), 'revenue'),
            (_('Total re&venue'), _('Sort tasks by total revenue'), 'totalRevenue'),
            (_('&Reminder'), _('Sort tasks by reminder date and time'), 'reminder')]:
            if value not in dependsOnEffortFeature or (value in dependsOnEffortFeature and effortOn):
                self._sortUICommands.append(uicommand.ViewerSortByCommand(\
                    viewer=self, value=value, menuText=menuText, helpText=helpText))


class SortableViewerForEffortMixin(SortableViewerMixin):
    def sorterOptions(self):
        return dict()
    

class SortableViewerForCategoriesMixin(SortableViewerMixin):
    def createSortUICommands(self):
        self._sortUICommands = [uicommand.ViewerSortOrderCommand(viewer=self),
                                uicommand.ViewerSortCaseSensitive(viewer=self)]


class SortableViewerForAttachmentsMixin(SortableViewerMixin):
    def createSortUICommands(self):
        self._sortUICommands = \
            [uicommand.ViewerSortOrderCommand(viewer=self),
             uicommand.ViewerSortCaseSensitive(viewer=self),
             None,
             uicommand.ViewerSortByCommand(viewer=self, value='subject',
                 menuText=_('Sub&ject'),
                 helpText=_('Sort attachments by subject')),
             uicommand.ViewerSortByCommand(viewer=self, value='description',
                 menuText=_('&Description'),
                 helpText=_('Sort attachments by description')),
             uicommand.ViewerSortByCommand(viewer=self, value='categories',
                 menuText=_('&Category'),
                 helpText=_('Sort attachments by category')),
             uicommand.ViewerSortByCommand(viewer=self,
                 value='totalCategories', menuText=_('Overall categories'),
                 helpText=_('Sort attachments by overall categories'))]


class SortableViewerForNotesMixin(SortableViewerMixin):
    def createSortUICommands(self):
        self._sortUICommands = \
            [uicommand.ViewerSortOrderCommand(viewer=self),
             uicommand.ViewerSortCaseSensitive(viewer=self),
             None,
             uicommand.ViewerSortByCommand(viewer=self, value='subject',
                 menuText=_('Sub&ject'),
                 helpText=_('Sort notes by subject')),
             uicommand.ViewerSortByCommand(viewer=self, value='description',
                 menuText=_('&Description'),
                 helpText=_('Sort notes by description')),
             uicommand.ViewerSortByCommand(viewer=self, value='categories',
                 menuText=_('&Category'),
                 helpText=_('Sort notes by category')),
             uicommand.ViewerSortByCommand(viewer=self,
                 value='totalCategories', menuText=_('Overall categories'),
                 helpText=_('Sort notes by overall categories'))]


class AttachmentDropTargetMixin(object):
    ''' Mixin class for viewers that are drop targets for attachments. '''

    def widgetCreationKeywordArguments(self):
        kwargs = super(AttachmentDropTargetMixin, self).widgetCreationKeywordArguments()
        kwargs['onDropURL'] = self.onDropURL
        kwargs['onDropFiles'] = self.onDropFiles
        kwargs['onDropMail'] = self.onDropMail
        return kwargs
        
    def _addAttachments(self, attachments, index, **itemDialogKwargs):
        ''' Add attachments. If index refers to an existing domain object, 
            add the attachments to that object. If index is None, use the 
            newItemDialog to create a new domain object and add the attachments
            to that new object. '''
        if index is None:
            newItemDialog = self.newItemDialog(bitmap='new',
                attachments=attachments, **itemDialogKwargs)
            newItemDialog.Show()
        else:
            addAttachment = command.AddAttachmentCommand(self.presentation(),
                [self.getItemWithIndex(index)], attachments=attachments)
            addAttachment.do()

    def onDropURL(self, index, url):
        ''' This method is called by the widget when a URL is dropped on an 
            item. '''
        attachments = [attachment.URIAttachment(url)]
        self._addAttachments(attachments, index)

    def onDropFiles(self, index, filenames):
        ''' This method is called by the widget when one or more files
            are dropped on an item. '''
        attachmentBase = self.settings.get('file', 'attachmentbase')
        if base:
            func = lambda x: attachment.getRelativePath(x, attachmentBase)
        else:
            func = lambda x: x
        attachments = [attachment.FileAttachment(func(name)) for name in filenames]
        self._addAttachments(attachments, index)

    def onDropMail(self, index, mail):
        ''' This method is called by the widget when a mail message is dropped
            on an item. '''
        att = attachment.MailAttachment(mail)
        subject, content = att.read()
        self._addAttachments([att], index, subject=subject, 
                             description=content)


class NoteColumnMixin(object):
    def noteImageIndex(self, item, which): # pylint: disable-msg=W0613
        return self.imageIndex['note'] if item.notes() else -1
    

class AttachmentColumnMixin(object):    
    def attachmentImageIndex(self, item, which): # pylint: disable-msg=W0613
        return self.imageIndex['attachment'] if item.attachments() else -1 

