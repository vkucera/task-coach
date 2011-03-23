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
    
    def __init__(self, *args, **kwargs):
        self.__filterUICommands = None
        super(FilterableViewerMixin, self).__init__(*args, **kwargs)

    def isFilterable(self):
        return True

    def getFilterUICommands(self):
        if not self.__filterUICommands:
            self.__filterUICommands = self.createFilterUICommands()
        # Recreate the category filter commands every time because the category
        # filter menu depends on what categories there are
        return self.__filterUICommands[:2] + self.createCategoryFilterCommands() + self.__filterUICommands[2:]

    def createFilterUICommands(self):
        return [uicommand.ResetFilter(viewer=self), None]

    def resetFilter(self):
        self.taskFile.categories().resetAllFilteredCategories()

    def createCategoryFilterCommands(self):
        categories = self.taskFile.categories()
        commands = [_('&Categories'), 
                uicommand.ResetCategoryFilter(categories=categories)]
        if categories:
            commands.append(None)
            commands.extend(self.createToggleCategoryFilterCommands(categories.rootItems()))
        return [tuple(commands)]
    
    def createToggleCategoryFilterCommands(self, categories):
        categories = list(categories)
        categories.sort(key=lambda category: category.subject())
        commands = [uicommand.ToggleCategoryFilter(category=category) for category in categories]
        categoriesWithChildren = [category for category in categories if category.children()]
        if categoriesWithChildren:
            commands.append(None)
            for category in categoriesWithChildren:
                subCommands = [_('%s (subcategories)')%category.subject()]
                subCommands.extend(self.createToggleCategoryFilterCommands(category.children()))
                commands.append(tuple(subCommands))
        return commands


class FilterableViewerForCategorizablesMixin(FilterableViewerMixin):
    def createFilter(self, items):
        items = super(FilterableViewerMixin, self).createFilter(items)
        filterOnlyWhenAllCategoriesMatch = self.settings.getboolean('view', 
            'categoryfiltermatchall')
        return category.filter.CategoryFilter(items, 
            categories=self.taskFile.categories(), treeMode=self.isTreeViewer(), 
            filterOnlyWhenAllCategoriesMatch=filterOnlyWhenAllCategoriesMatch)


class FilterableViewerForTasksMixin(FilterableViewerForCategorizablesMixin):
    def createFilter(self, taskList):
        taskList = super(FilterableViewerForTasksMixin, self).createFilter(taskList)
        return task.filter.ViewFilter(taskList, treeMode=self.isTreeViewer(), 
                                      **self.viewFilterOptions())
                                       
    def viewFilterOptions(self):
        options = dict(dueDateTimeFilter=self.getFilteredByDueDateTime(),
                       completionDateTimeFilter=self.getFilteredByCompletionDateTime(),
                       startDateTimeFilter=self.getFilteredByStartDateTime(),
                       hideActiveTasks=self.isHidingActiveTasks(),
                       hideCompositeTasks=self.isHidingCompositeTasks())
        return options
    
    def isFilteredByDueDateTime(self, dueDateTimeString):
        return dueDateTimeString == self.getFilteredByDueDateTime()
    
    def setFilteredByDueDateTime(self, dueDateTimeString):
        self.settings.set(self.settingsSection(), 'tasksdue', dueDateTimeString)
        self.presentation().setFilteredByDueDateTime(dueDateTimeString)
        
    def getFilteredByDueDateTime(self):
        return self.settings.get(self.settingsSection(), 'tasksdue')
    
    def isFilteredByCompletionDateTime(self, completionDateTimeString):
        return completionDateTimeString == self.getFilteredByCompletionDateTime()
        
    def setFilteredByCompletionDateTime(self, completionDateTimeString):
        self.settings.set(self.settingsSection(), 'taskscompleted', 
                          completionDateTimeString)
        self.presentation().setFilteredByCompletionDateTime(completionDateTimeString)
    
    def getFilteredByCompletionDateTime(self):
        return self.settings.get(self.settingsSection(), 'taskscompleted')
    
    def isFilteredByStartDateTime(self, startDateTimeString):
        return startDateTimeString == self.getFilteredByStartDateTime()
    
    def setFilteredByStartDateTime(self, startDateTimeString):
        self.settings.set(self.settingsSection(), 'tasksinactive', 
                          startDateTimeString)
        self.presentation().setFilteredByStartDateTime(startDateTimeString)
        
    def getFilteredByStartDateTime(self):
        return self.settings.get(self.settingsSection(), 'tasksinactive')
    
    def hideActiveTasks(self, hide=True):
        self.__setBooleanSetting('hideactivetasks', hide)
        self.presentation().hideActiveTasks(hide)

    def isHidingActiveTasks(self):
        return self.__getBooleanSetting('hideactivetasks')
    
    def hideCompositeTasks(self, hide=True):
        self.__setBooleanSetting('hidecompositetasks', hide)
        self.presentation().hideCompositeTasks(hide)
        
    def isHidingCompositeTasks(self):
        return self.__getBooleanSetting('hidecompositetasks')
    
    def resetFilter(self):
        super(FilterableViewerForTasksMixin, self).resetFilter()
        self.hideActiveTasks(False)
        self.hideCompositeTasks(False)
        self.setFilteredByDueDateTime('Never')
        self.setFilteredByCompletionDateTime('Never')
        self.setFilteredByStartDateTime('Never')

    def createFilterUICommands(self):
        def dueDateTimeFilter(menuText, helpText, value):
            return uicommand.ViewerFilterByDueDateTime(menuText=menuText, 
                                                       helpText=helpText,
                                                       value=value, viewer=self)
        def completionDateTimeFilter(menuText, helpText, value):
            return uicommand.ViewerFilterByCompletionDateTime(menuText=menuText,
                                                              helpText=helpText,
                                                              value=value, viewer=self)
        def startDateTimeFilter(menuText, helpText, value):
            return uicommand.ViewerFilterByStartDateTime(menuText=menuText,
                                                         helpText=helpText,
                                                         value=value, viewer=self)
        dueDateTimeFilterCommands = (_('&Due tasks'),
            dueDateTimeFilter(_('&Show all due tasks'), _('Show all due tasks'), 
                              'Never'),
            dueDateTimeFilter(_('&Hide all due tasks'), _('Hide all due tasks'), 
                              'Always'),
            dueDateTimeFilter(_('Only show tasks due &today'),
                              _('Only show tasks due today and hide later ones'), 
                              'Today'),
            dueDateTimeFilter(_('Only show tasks due today or t&omorrow'), 
                              _('Only show tasks due today or tomorrow and hide later ones'), 
                              'Tomorrow'),
            dueDateTimeFilter(_('Only show tasks due this wo&rk week'), 
                              _('Only show tasks due this work week and hide later ones'),
                              'Workweek'),
            dueDateTimeFilter(_('Only show tasks due this &week'), 
                              _('Only show tasks due this week and hide later ones'),
                              'Week'),
            dueDateTimeFilter(_('Only show tasks due within &7 days'),
                              _('Only show tasks due within 7 days and hide later ones'),
                              'Days7'),
            dueDateTimeFilter(_('Only show tasks due within &14 days'),
                              _('Only show tasks due within 14 days and hide later ones'),
                              'Days14'),
            dueDateTimeFilter(_('Only show tasks due this &month'), 
                              _('Only show tasks due this month and hide later ones'), 
                              'Month'),
            dueDateTimeFilter(_('Only show tasks due within &30 days'),
                              _('Only show tasks due within 30 days and hide later ones'),
                              'Days30'),
            dueDateTimeFilter(_('Only show tasks due this &year'), 
                              _('Only show tasks due this year and hide later ones'),
                              'Year'))
        completionDateTimeFilterCommands = (_('&Completed tasks'),
            completionDateTimeFilter(_('&Show all completed tasks'), 
                                     _('Show all completed tasks'), 'Never'),
            completionDateTimeFilter(_('&Hide all completed tasks'), 
                                     _('Hide all completed tasks'), 'Always'),
            completionDateTimeFilter(_('Only show tasks completed &today'), 
                                     _('Only show tasks completed today and hide older ones'), 
                                     'Today'),
            completionDateTimeFilter(_('Only show tasks completed &yesterday and today'), 
                                     _('Only show tasks completed yesterday and today and hide older ones'), 
                                     'Yesterday'),
            completionDateTimeFilter(_('Only show tasks completed this wo&rk week'),
                                     _('Only show tasks completed this work week and hide older ones'),
                                     'Workweek'),
            completionDateTimeFilter(_('Only show tasks completed this &week'),
                                     _('Only show tasks completed this week and hide older ones'),
                                     'Week'),
            completionDateTimeFilter(_('Only show tasks completed the last &7 days'),
                                     _('Only show tasks completed the last 7 days and hide older ones'),
                                     'Days7'),
            completionDateTimeFilter(_('Only show tasks completed the last &14 days'),
                                     _('Only show tasks completed the last 14 days and hide older ones'),
                                     'Days14'),
            completionDateTimeFilter(_('Only show tasks completed this &month'),
                                     _('Only show tasks completed this month and hide older ones'),
                                     'Month'),
            completionDateTimeFilter(_('Only show tasks completed the last &30 days'),
                                     _('Only show tasks completed the last 30 days and hide older ones'),
                                     'Days30'),
            completionDateTimeFilter(_('Only show tasks completed this &year'),
                                     _('Only show tasks completed this year and hide older ones'),
                                     'Year'))
        startDateTimeFilterCommands = (_('&Inactive tasks'),
            startDateTimeFilter(_('&Show all inactive tasks'),
                                _('Show all inactive tasks (tasks with a start date in the future)'), 
                                'Never'),
            startDateTimeFilter(_('&Hide all inactive tasks'),
                                _('Hide all inactive tasks (tasks with a start date in the future)'), 
                                'Always'),
            startDateTimeFilter(_('Only show tasks starting &today'), 
                                _('Only show tasks starting today and hide later ones'), 
                                'Today'),
            startDateTimeFilter(_('Only show tasks starting today or t&omorrow'),
                                _('Only show tasks starting today or tomorrow and hide later ones'),
                                'Tomorrow'),
            startDateTimeFilter(_('Only show tasks starting this wo&rk week'),
                                _('Only show tasks starting this work week and hide later ones'),
                                'Workweek'),
            startDateTimeFilter(_('Only show tasks starting this &week'),
                                _('Only show tasks starting this week and hide later ones'), 
                                'Week'),
            startDateTimeFilter(_('Only show tasks starting the next &7 days'),
                                _('Only show tasks starting the next 7 days and hide later ones'),
                                'Days7'),
            startDateTimeFilter(_('Only show tasks starting the next &14 days'),
                                _('Only show tasks starting the next 14 days and hide later ones'),
                                'Days14'),
            startDateTimeFilter(_('Only show tasks starting this &month'),
                                _('Only show tasks starting this month and hide later ones'),
                                'Month'),
            startDateTimeFilter(_('Only show tasks starting the next &30 days'),
                                _('Only show tasks starting the next 30 days and hide later ones'),
                                'Days30'),
            startDateTimeFilter(_('Only show tasks starting this &year'),
                                _('Only show tasks starting this year and hide later ones'),
                                'Year'))
        return super(FilterableViewerForTasksMixin, 
                     self).createFilterUICommands() + \
            [dueDateTimeFilterCommands, completionDateTimeFilterCommands, 
             startDateTimeFilterCommands, 
             uicommand.ViewerHideActiveTasks(viewer=self),
             uicommand.ViewerHideCompositeTasks(viewer=self)]
            
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
        self._sortUICommands = self.createSortOrderUICommands()
        sortByCommands = self.createSortByUICommands()
        if sortByCommands:
            self._sortUICommands.append(None) # Separator
            self._sortUICommands.extend(sortByCommands)
        
    def createSortOrderUICommands(self):
        ''' Create the UICommands for changing sort order, like ascending/
            descending, and match case. '''
        return [uicommand.ViewerSortOrderCommand(viewer=self),
                uicommand.ViewerSortCaseSensitive(viewer=self)]
        
    def createSortByUICommands(self):
        ''' Create the UICommands for changing what the items are sorted by,
            i.e. the columns. '''
        return [uicommand.ViewerSortByCommand(viewer=self, value='subject',
                    menuText=_('Sub&ject'),
                    helpText=self.sortBySubjectHelpText),
                uicommand.ViewerSortByCommand(viewer=self, value='description',
                    menuText=_('&Description'),
                    helpText=self.sortByDescriptionHelpText)]


class SortableViewerForEffortMixin(SortableViewerMixin):
    def createSortOrderUICommands(self):
        ''' Create the UICommands for changing sort order. The only
            option for efforts is ascending/descending at the moment. '''
        return [uicommand.ViewerSortOrderCommand(viewer=self)]

    def createSortByUICommands(self):
        ''' Create the UICommands for changing what the items are sorted by,
            i.e. the columns. Currently, effort is always sorted by period. '''
        return []

    def sortKey(self):
        ''' Efforts are always sorted by period at the moment. '''
        return 'period'
        

class SortableViewerForCategoriesMixin(SortableViewerMixin):
    sortBySubjectHelpText = _('Sort categories by subject')
    sortByDescriptionHelpText = _('Sort categories by description')


class SortableViewerForCategorizablesMixin(SortableViewerMixin):
    ''' Mixin class to create uiCommands for sorting categorizables. '''

    def createSortByUICommands(self):
        commands = super(SortableViewerForCategorizablesMixin, self).createSortByUICommands()
        commands.append(uicommand.ViewerSortByCommand(viewer=self, 
            value='categories', menuText=_('&Category'),
            helpText=self.sortByCategoryHelpText))
        return commands


class SortableViewerForAttachmentsMixin(SortableViewerForCategorizablesMixin):
    sortBySubjectHelpText = _('Sort attachments by subject')
    sortByDescriptionHelpText = _('Sort attachments by description')
    sortByCategoryHelpText = _('Sort attachments by category')
    

class SortableViewerForNotesMixin(SortableViewerForCategorizablesMixin):
    sortBySubjectHelpText = _('Sort notes by subject')
    sortByDescriptionHelpText = _('Sort notes by description')
    sortByCategoryHelpText = _('Sort notes by category')


class SortableViewerForTasksMixin(SortableViewerForCategorizablesMixin):
    SorterClass = task.sorter.Sorter
    sortBySubjectHelpText = _('Sort tasks by subject')
    sortByDescriptionHelpText = _('Sort tasks by description')
    sortByCategoryHelpText = _('Sort tasks by category')
    
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

    def createSortOrderUICommands(self):
        commands = super(SortableViewerForTasksMixin, self).createSortOrderUICommands()
        commands.append(uicommand.ViewerSortByTaskStatusFirst(viewer=self))
        return commands
    
    def createSortByUICommands(self):
        commands = super(SortableViewerForTasksMixin, self).createSortByUICommands()
        effortOn = self.settings.getboolean('feature', 'effort')
        dependsOnEffortFeature = ['budget', 'timeSpent', 'budgetLeft',  
                                  'hourlyFee', 'fixedFee', 'revenue']
        for menuText, helpText, value in [\
            (_('&Start date'), _('Sort tasks by start date'), 'startDateTime'),
            (_('&Due date'), _('Sort tasks by due date'), 'dueDateTime'),
            (_('&Completion date'), _('Sort tasks by completion date'), 'completionDateTime'),
            (_('&Prerequisites'), _('Sort tasks by prerequisite tasks'), 'prerequisites'),
            (_('&Dependencies'), _('Sort tasks by dependent tasks'), 'dependencies'),
            (_('&Time left'), _('Sort tasks by time left'), 'timeLeft'),
            (_('&Percentage complete'), _('Sort tasks by percentage complete'), 'percentageComplete'),
            (_('&Recurrence'), _('Sort tasks by recurrence'), 'recurrence'),
            (_('&Budget'), _('Sort tasks by budget'), 'budget'),
            (_('&Time spent'), _('Sort tasks by time spent'), 'timeSpent'),
            (_('Budget &left'), _('Sort tasks by budget left'), 'budgetLeft'),
            (_('&Priority'), _('Sort tasks by priority'), 'priority'),
            (_('&Hourly fee'), _('Sort tasks by hourly fee'), 'hourlyFee'),
            (_('&Fixed fee'), _('Sort tasks by fixed fee'), 'fixedFee'),
            (_('&Revenue'), _('Sort tasks by revenue'), 'revenue'),
            (_('&Reminder'), _('Sort tasks by reminder date and time'), 'reminder')]:
            if value not in dependsOnEffortFeature or (value in dependsOnEffortFeature and effortOn):
                commands.append(uicommand.ViewerSortByCommand(\
                    viewer=self, value=value, menuText=menuText, helpText=helpText))
        return commands
    

class AttachmentDropTargetMixin(object):
    ''' Mixin class for viewers that are drop targets for attachments. '''

    def widgetCreationKeywordArguments(self):
        kwargs = super(AttachmentDropTargetMixin, self).widgetCreationKeywordArguments()
        kwargs['onDropURL'] = self.onDropURL
        kwargs['onDropFiles'] = self.onDropFiles
        kwargs['onDropMail'] = self.onDropMail
        return kwargs
        
    def _addAttachments(self, attachments, item, **itemDialogKwargs):
        ''' Add attachments. If index refers to an existing domain object, 
            add the attachments to that object. If index is None, use the 
            newItemDialog to create a new domain object and add the attachments
            to that new object. '''
        if item is None:
            itemDialogKwargs['subject'] = attachments[0].subject()
            newItemDialog = self.newItemDialog(bitmap='new',
                attachments=attachments, **itemDialogKwargs)
            newItemDialog.Show()
        else:
            addAttachment = command.AddAttachmentCommand(self.presentation(),
                [item], attachments=attachments)
            addAttachment.do()

    def onDropURL(self, item, url, **kwargs):
        ''' This method is called by the widget when a URL is dropped on an 
            item. '''
        attachments = [attachment.URIAttachment(url)]
        self._addAttachments(attachments, item, **kwargs)

    def onDropFiles(self, item, filenames, **kwargs):
        ''' This method is called by the widget when one or more files
            are dropped on an item. '''
        attachmentBase = self.settings.get('file', 'attachmentbase')
        if attachmentBase:
            filenames = [attachment.getRelativePath(filename, attachmentBase) \
                         for filename in filenames]
        attachments = [attachment.FileAttachment(filename) for filename in filenames]
        self._addAttachments(attachments, item, **kwargs)

    def onDropMail(self, item, mail, **kwargs):
        ''' This method is called by the widget when a mail message is dropped
            on an item. '''
        att = attachment.MailAttachment(mail)
        subject, content = att.read()
        self._addAttachments([att], item, subject=subject, description=content, **kwargs)


class NoteColumnMixin(object):
    def noteImageIndices(self, item):
        index = self.imageIndex['note_icon'] if item.notes() else -1
        return {wx.TreeItemIcon_Normal: index}
    

class AttachmentColumnMixin(object):    
    def attachmentImageIndices(self, item): # pylint: disable-msg=W0613
        index = self.imageIndex['paperclip_icon'] if item.attachments() else -1
        return {wx.TreeItemIcon_Normal: index}

