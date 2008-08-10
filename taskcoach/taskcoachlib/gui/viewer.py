'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>
Copyright (C) 2007-2008 Jerome Laheurte <fraca7@free.fr>
Copyright (C) 2008 Rob McMullen <rob.mcmullen@gmail.com>

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
from taskcoachlib import patterns, command, widgets, mailer
from taskcoachlib.domain import base, task, category, effort, date, note, \
    attachment
from taskcoachlib.i18n import _
import uicommand, menu, color, render, dialog, toolbar


class SearchableViewer(object):
    ''' A viewer that is searchable. This is a mixin class. '''

    def isSearchable(self):
        return True
    
    def createFilter(self, model):
        model = super(SearchableViewer, self).createFilter(model)
        return base.SearchFilter(model, **self.searchOptions())

    def searchOptions(self):
        searchString, matchCase, includeSubItems = self.getSearchFilter()
        return dict(searchString=searchString, matchCase=matchCase, 
                    includeSubItems=includeSubItems, 
                    treeMode=self.isTreeViewer())
    
    def setSearchFilter(self, searchString, matchCase=False, 
                        includeSubItems=False):
        section = self.settingsSection()
        self.settings.set(section, 'searchfilterstring', searchString)
        self.settings.set(section, 'searchfiltermatchcase', str(matchCase))
        self.settings.set(section, 'searchfilterincludesubitems', str(includeSubItems))
        self.model().setSearchFilter(searchString, matchCase, includeSubItems)
        
    def getSearchFilter(self):
        section = self.settingsSection()
        searchString = self.settings.get(section, 'searchfilterstring')
        matchCase = self.settings.getboolean(section, 'searchfiltermatchcase')
        includeSubItems = self.settings.getboolean(section, 'searchfilterincludesubitems')
        return searchString, matchCase, includeSubItems
    
    def createToolBarUICommands(self):
        ''' UI commands to put on the toolbar of this viewer. '''
        searchUICommand = uicommand.Search(viewer=self, settings=self.settings)
        return super(SearchableViewer, self).createToolBarUICommands() + \
            [None, searchUICommand]
            

class FilterableViewer(object):
    ''' A viewer that is filterable. This is a mixin class. '''

    def isFilterable(self):
        return True
    
    '''
    def createFilter(self, model):
        model = super(FilterableViewer, self).createFilter(model)
        return self.FilterClass(model, **self.filterOptions())
    '''    

class FilterableViewerForNotes(FilterableViewer):
    def createFilter(self, notesContainer):
        notesContainer = super(FilterableViewerForNotes, self).createFilter(notesContainer)
        return category.filter.CategoryFilter(notesContainer, 
            categories=self.categories, treeMode=self.isTreeViewer(),
            filterOnlyWhenAllCategoriesMatch=self.settings.getboolean('view',
            'categoryfiltermatchall'))
        
            
class FilterableViewerForTasks(FilterableViewer):
    def __init__(self, *args, **kwargs):
        self.__filterUICommands = None
        super(FilterableViewerForTasks, self).__init__(*args, **kwargs)

    def createFilter(self, taskList):
        taskList = super(FilterableViewerForTasks, self).createFilter(taskList)
        return category.filter.CategoryFilter( \
            task.filter.ViewFilter(taskList, treeMode=self.isTreeViewer(), 
                                   **self.viewFilterOptions()), 
            categories=self.categories, treeMode=self.isTreeViewer(),
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
        self.model().setFilteredByDueDate(dueDateString)
        
    def getFilteredByDueDate(self):
        return self.settings.get(self.settingsSection(), 'tasksdue')
    
    def hideActiveTasks(self, hide=True):
        self.__setBooleanSetting('hideactivetasks', hide)
        self.model().hideActiveTasks(hide)
        
    def isHidingActiveTasks(self):
        return self.__getBooleanSetting('hideactivetasks')

    def hideInactiveTasks(self, hide=True):
        self.__setBooleanSetting('hideinactivetasks', hide)
        self.model().hideInactiveTasks(hide)
        
    def isHidingInactiveTasks(self):
        return self.__getBooleanSetting('hideinactivetasks')
    
    def hideCompletedTasks(self, hide=True):
        self.__setBooleanSetting('hidecompletedtasks', hide)
        self.model().hideCompletedTasks(hide)
        
    def isHidingCompletedTasks(self):
        return self.__getBooleanSetting('hidecompletedtasks')
    
    def hideOverdueTasks(self, hide=True):
        self.__setBooleanSetting('hideoverduetasks', hide)
        self.model().hideOverdueTasks(hide)
        
    def isHidingOverdueTasks(self):
        return self.__getBooleanSetting('hideoverduetasks')
    
    def hideOverbudgetTasks(self, hide=True):
        self.__setBooleanSetting('hideoverbudgettasks', hide)
        self.model().hideOverbudgetTasks(hide)
    
    def isHidingOverbudgetTasks(self):
        return self.__getBooleanSetting('hideoverbudgettasks')
    
    def hideCompositeTasks(self, hide=True):
        self.__setBooleanSetting('hidecompositetasks', hide)
        self.model().hideCompositeTasks(hide)
        
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
        for category in self.categories:
            category.setFiltered(False)
        
    def getFilterUICommands(self):
        if not self.__filterUICommands:
            self.__filterUICommands = self.createFilterUICommands()
        return self.__filterUICommands

    def createFilterUICommands(self):
        return [uicommand.ResetFilter(viewer=self),
                None,
                (_('Show only tasks &due before end of'),
                    uicommand.ViewerFilterByDueDate(menuText=_('&Unlimited'),
                        helpText=_('Show all tasks'), value='Unlimited',
                        viewer=self),
                    uicommand.ViewerFilterByDueDate(menuText=_('&Today'),
                        helpText=_('Only show tasks due today'), value='Today',
                        viewer=self),
                    uicommand.ViewerFilterByDueDate(menuText=_('T&omorrow'),
                        helpText=_('Only show tasks due today and tomorrow'),
                        value='Tomorrow', viewer=self),
                    uicommand.ViewerFilterByDueDate(menuText=_('Wo&rkweek'),
                        helpText=_('Only show tasks due this work week (i.e. before Friday)'),
                        value='Workweek', viewer=self),
                    uicommand.ViewerFilterByDueDate(menuText=_('&Week'),
                        helpText=_('Only show tasks due this week (i.e. before Sunday)'),
                        value='Week', viewer=self),
                    uicommand.ViewerFilterByDueDate(menuText=_('&Month'),
                        helpText=_('Only show tasks due this month'),
                        value='Month', viewer=self),
                    uicommand.ViewerFilterByDueDate(menuText=_('&Year'),
                        helpText=_('Only show tasks due this year'),
                        value='Year', viewer=self)),
                (_('&Hide tasks that are'),
                    uicommand.ViewerHideActiveTasks(viewer=self),
                    uicommand.ViewerHideInactiveTasks(viewer=self),
                    uicommand.ViewerHideCompletedTasks(viewer=self),
                    None,
                    uicommand.ViewerHideOverdueTasks(viewer=self),
                    uicommand.ViewerHideOverbudgetTasks(viewer=self),
                    uicommand.ViewerHideCompositeTasks(viewer=self))]

    def __getBooleanSetting(self, setting):
        return self.settings.getboolean(self.settingsSection(), setting)
    
    def __setBooleanSetting(self, setting, booleanValue):
        self.settings.setboolean(self.settingsSection(), setting, booleanValue)
        
                
class SortableViewer(object):
    ''' A viewer that is sortable. This is a mixin class. '''

    def __init__(self, *args, **kwargs):
        self.__sortUICommands = None
        super(SortableViewer, self).__init__(*args, **kwargs)

    def isSortable(self):
        return True

    def createSorter(self, model):
        return self.SorterClass(model, **self.sorterOptions())
    
    def sorterOptions(self):
        return dict(sortBy=self.sortKey(),
                    sortAscending=self.isSortOrderAscending(),
                    sortCaseSensitive=self.isSortCaseSensitive())
        
    def sortBy(self, sortKey):
        if self.isSortedBy(sortKey):
            self.setSortOrderAscending(not self.isSortOrderAscending())
        else:
            self.settings.set(self.settingsSection(), 'sortby', sortKey)
            self.model().sortBy(sortKey)
        
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
        self.model().sortAscending(ascending)
        
    def isSortCaseSensitive(self):
        return self.settings.getboolean(self.settingsSection(), 
            'sortcasesensitive')
        
    def setSortCaseSensitive(self, caseSensitive=True):
        self.settings.set(self.settingsSection(), 'sortcasesensitive', 
            str(caseSensitive))
        self.model().sortCaseSensitive(caseSensitive)

    def getSortUICommands(self):
        if not self.__sortUICommands:
            self.__sortUICommands = self.createSortUICommands()
        return self.__sortUICommands

    def createSortUICommands(self):
        raise NotImplementedError

        
class SortableViewerForTasks(SortableViewer):
    SorterClass = task.sorter.Sorter
    
    def isSortByTaskStatusFirst(self):
        return self.settings.getboolean(self.settingsSection(),
            'sortbystatusfirst')
        
    def setSortByTaskStatusFirst(self, sortByTaskStatusFirst):
        self.settings.set(self.settingsSection(), 'sortbystatusfirst',
            str(sortByTaskStatusFirst))
        self.model().sortByTaskStatusFirst(sortByTaskStatusFirst)
        
    def sorterOptions(self):
        options = super(SortableViewerForTasks, self).sorterOptions()
        options.update(treeMode=self.isTreeViewer(), 
            sortByTaskStatusFirst=self.isSortByTaskStatusFirst())
        return options

    def createSortUICommands(self):
        commands = [uicommand.ViewerSortOrderCommand(viewer=self),
                    uicommand.ViewerSortCaseSensitive(viewer=self),
                    uicommand.ViewerSortByTaskStatusFirst(viewer=self),
                    None]
        for menuText, helpText, value in [\
            (_('Sub&ject'), _('Sort tasks by subject'), 'subject'),
            (_('&Description'), _('Sort by description'), 'description'),
            (_('&Category'), _('Sort by category'), 'categories'),
            (_('Overall categories'), _('Sort by overall categories'), 'totalCategories'),
            (_('&Start date'), _('Sort tasks by start date'), 'startDate'),
            (_('&Due date'), _('Sort tasks by due date'), 'dueDate'),
            (_('&Completion date'), _('Sort tasks by completion date'), 'completionDate'),
            (_('D&ays left'), _('Sort tasks by number of days left'), 'timeLeft'),
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
            commands.append(uicommand.ViewerSortByCommand(viewer=self,
                value=value, menuText=menuText, helpText=helpText))
        return commands


class SortableViewerForEffort(SortableViewer):
    def sorterOptions(self):
        return dict()
    

class SortableViewerForCategories(SortableViewer):
    def createSortUICommands(self):
        return [uicommand.ViewerSortOrderCommand(viewer=self),
                uicommand.ViewerSortCaseSensitive(viewer=self)]


class SortableViewerForNotes(SortableViewer):
    def createSortUICommands(self):
        return [uicommand.ViewerSortOrderCommand(viewer=self),
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


class AttachmentDropTarget(object):
    ''' Mixin class for viewers that are drop targets for attachments. '''

    def widgetCreationKeywordArguments(self):
        kwargs = super(AttachmentDropTarget, self).widgetCreationKeywordArguments()
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
            addAttachment = command.AddAttachmentCommand(self.model(),
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
        base = self.settings.get('file', 'attachmentbase')
        if base:
            func = lambda x: attachment.getRelativePath(x, base)
        else:
            func = lambda x: x
        attachments = [attachment.FileAttachment(func(name)) for name in filenames]
        self._addAttachments(attachments, index)

    def onDropMail(self, index, mail):
        ''' This method is called by the widget when a mail message is dropped
            on an item. '''
        attachments = [attachment.MailAttachment(mail)]
        subject, content = mailer.readMail(mail)
        self._addAttachments(attachments, index, subject=subject, 
                             description=content)


class Viewer(wx.Panel):
    __metaclass__ = patterns.NumberedInstances
    
    ''' A Viewer shows the contents of a model (a list of tasks or a list of 
        efforts) by means of a widget (e.g. a ListCtrl or a TreeListCtrl).'''
        
    def __init__(self, parent, list, settings, *args, **kwargs):
        super(Viewer, self).__init__(parent, -1) # FIXME: Pass *args, **kwargs
        self.parent = parent # FIXME: Make instance variables private
        self.settings = settings
        self.__settingsSection = kwargs.pop('settingsSection')
        self.__instanceNumber = kwargs.pop('instanceNumber')
        self.__selection = []
        self.__toolbarUICommands = None
        self.list = self.createSorter(self.createFilter(list))
        self.toolbar = toolbar.ToolBar(self, (16, 16))
        self.widget = self.createWidget()
        self.initLayout()
        self.registerModelObservers()
        self.refresh()
    
    def registerModelObservers(self):
        for eventHandler in self.onAddItem, self.onRemoveItem, self.onSorted:
            patterns.Publisher().removeObserver(eventHandler)
        patterns.Publisher().registerObserver(self.onAddItem, 
            eventType=self.list.addItemEventType())
        patterns.Publisher().registerObserver(self.onRemoveItem, 
            eventType=self.list.removeItemEventType())
        patterns.Publisher().registerObserver(self.onSorted, 
            eventType=self.list.sortEventType())
        
    def detach(self):
        ''' Should be called by viewercontainer before closing the viewer '''
        patterns.Publisher().removeInstance(self)

    def selectEventType(self):
        return '%s (%s).select'%(self.__class__, id(self))
    
    def title(self):
        return self.settings.get(self.settingsSection(), 'title') or self.defaultTitle
    
    def setTitle(self, title):
        self.settings.set(self.settingsSection(), 'title', title)
        self.parent.SetPageText(self.parent.GetPageIndex(self), title)

    def initLayout(self):
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self._sizer.Add(self.toolbar, flag=wx.EXPAND)
        self._sizer.Add(self.widget, proportion=1, flag=wx.EXPAND)
        self.SetSizerAndFit(self._sizer)
    
    def createWidget(self, *args):
        raise NotImplementedError

    def getWidget(self):
        return self.widget
            
    def createSorter(self, collection):
        ''' This method can be overridden to decorate the model with a 
            sorter. '''
        return collection
        
    def createFilter(self, collection):
        ''' This method can be overridden to decorate the model with a 
            filter. '''
        return collection

    def onAddItem(self, event):
        ''' One or more items were added to our model, refresh the widget. '''
        self.refresh()

    def onRemoveItem(self, event):
        ''' One or more items were removed from our model, refresh the 
            widget. '''
        self.refresh()

    def onSorted(self, event):
        ''' The sort order of our items was changed, refresh the widget. '''
        # FIXME: move to SortableViewer?
        self.refresh()

    def onSelect(self, *args):
        ''' The selection of items in the widget has been changed. Notify 
            our observers and remember the current selection so we can
            restore it later, e.g. after the sort order is changed. '''
        if self.IsBeingDeleted():
            # Some widgets change the selection and send selection events when 
            # deleting all items as part of the Destroy process. Ignore.
            return
        # Be sure all wx events are handled before we notify our observers: 
        wx.CallAfter(lambda: patterns.Publisher().notifyObservers(\
            patterns.Event(self, self.selectEventType(), self.curselection())))
        # Remember the current selection so we can restore it after a refresh:
        self.__selection = self.curselection()
        
    def refresh(self):
        self.widget.refresh(len(self.list))
        # Restore the selection:
        self.widget.select([self.getIndexOfItem(item) for item \
                            in self.__selection if item in self.model()])
                            
    def curselection(self):
        ''' Return a list of items (domain objects) currently selected in our
            widget. '''
        # Translate indices returned by the widget into actual domain objects:
        return [self.getItemWithIndex(index) for index in \
                self.widget.curselection()]
    
    def selectall(self):
        self.widget.selectall()
        
    def invertselection(self):
        self.widget.invertselection()
        
    def clearselection(self):
        self.widget.clearselection()
        
    def size(self):
        return self.widget.GetItemCount()
    
    def model(self):
        ''' Return the model of the viewer. '''
        return self.list
        
    def setModel(self, model):
        ''' Change the model of the viewer. '''
        self.list = model
    
    def widgetCreationKeywordArguments(self):
        return {}

    def isShowingTasks(self): 
        return False

    def isShowingEffort(self): 
        return False
    
    def isShowingCategories(self):
        return False
    
    def isShowingNotes(self):
        return False
    
    def visibleColumns(self):
        return [widgets.Column('subject', _('Subject'))]
    
    def itemEditor(self, *args, **kwargs):
        raise NotImplementedError
    
    def getColor(self, item):
        return wx.BLACK
    
    def getBackgroundColor(self, item):
        return None
    
    def settingsSection(self):
        ''' Return the settings section of this viewer. '''
        section = self.__settingsSection
        if self.__instanceNumber > 0:
            # We're not the first viewer of our class, so we need a different
            # settings section than the default one.
            section += str(self.__instanceNumber)
            if not self.settings.has_section(section):
                # Our section does not exist yet. Create it and copy the 
                # settings from the previous section as starting point. We're 
                # copying from the previous section instead of the default
                # section so that when the user closes a viewer and then opens
                # a new one, the settings of that closed viewer are reused. 
                self.settings.add_section(section, 
                    copyFromSection=self.previousSettingsSection())
        return section
        
    def previousSettingsSection(self):
        ''' Return the settings section of the previous viewer of this 
            class. '''
        previousSectionNumber = self.__instanceNumber - 1
        while previousSectionNumber > 0:
            previousSection = self.__settingsSection + str(previousSectionNumber)
            if self.settings.has_section(previousSection):
                return previousSection
            previousSectionNumber -= 1
        return self.__settingsSection
    
    def isSortable(self):
        return False

    def getSortUICommands(self):
        return []
    
    def isSearchable(self):
        return False
        
    def hasHideableColumns(self):
        return False
    
    def getColumnUICommands(self):
        return []

    def isFilterable(self):
        return False
    
    def getFilterUICommands(self):
        return []
    
    def getToolBarUICommands(self):
        if not self.__toolbarUICommands:
            self.__toolbarUICommands = self.createToolBarUICommands()
        return self.__toolbarUICommands

    def createToolBarUICommands(self):
        ''' UI commands to put on the toolbar of this viewer. '''
        # Keep this around for unit tests
        self.deleteUICommand = uicommand.DeleteDomainObject(viewer=self)
        return [
            uicommand.EditCut(viewer=self),
            uicommand.EditCopy(viewer=self),
            uicommand.EditPaste(),
            None,
            uicommand.NewDomainObject(viewer=self),
            uicommand.NewSubDomainObject(viewer=self),
            uicommand.EditDomainObject(viewer=self),
            self.deleteUICommand]

    
    def canCreateNewDomainObject(self):
        return True
    

class ListViewer(Viewer):
    def isTreeViewer(self):
        return False

    def visibleItems(self):
        ''' Iterate over the items in the model. '''
        for item in self.model():
            yield item
    
    def getItemWithIndex(self, index):
        return self.model()[index]
            
    def getIndexOfItem(self, item):
        return self.model().index(item)
    

class TreeViewer(Viewer):
    def __init__(self, *args, **kwargs):
        self.__itemsByIndex = dict()
        super(TreeViewer, self).__init__(*args, **kwargs)
        self.widget.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.onItemExpanded)
        self.widget.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.onItemCollapsed)

    def onItemExpanded(self, event):
        self.__handleExpandedOrCollapsedItem(event, expanded=True)
        
    def onItemCollapsed(self, event):
        self.__handleExpandedOrCollapsedItem(event, expanded=False)
        
    def __handleExpandedOrCollapsedItem(self, event, expanded):
        event.Skip()
        treeItem = event.GetItem()
        # If we get an expanded or collapsed event for the root item, ignore it
        if treeItem == self.widget.GetRootItem():
            return
        # Somehow we can get expanded or collapsed events for items that are
        # not the root item, but don't have a parent item either, resulting
        # in an empty index. I don't really understand how that can happen.
        # Ignore these items. See SF bug report #1840111. Also, it seems we
        # can get events for items that have a parent, but are not a child 
        # of that parent item, in which case GetIndexOfItem raises a ValueError.
        try:
            index = self.widget.GetIndexOfItem(treeItem)
        except ValueError:
            index = None
        if index:
            item = self.getItemWithIndex(index)
            item.expand(expanded)
    
    def expandAll(self):
        self.widget.expandAllItems()

    def collapseAll(self):
        self.widget.collapseAllItems()
        
    def expandSelected(self):
        self.widget.expandSelectedItems()

    def collapseSelected(self):
        self.widget.collapseSelectedItems()
        
    def isSelectionExpandable(self):
        return self.widget.isSelectionExpandable()
    
    def isSelectionCollapsable(self):
        return self.widget.isSelectionCollapsable()
        
    def isAnyItemExpandable(self):
        return self.widget.isAnyItemExpandable()

    def isAnyItemCollapsable(self):
        return self.widget.isAnyItemCollapsable()
        
    def isTreeViewer(self):
        return True

    def onAddItem(self, *args, **kwargs):
        self.__itemsByIndex = dict()
        super(TreeViewer, self).onAddItem(*args, **kwargs)

    def onRemoveItem(self, *args, **kwargs):
        self.__itemsByIndex = dict()
        super(TreeViewer, self).onRemoveItem(*args, **kwargs)

    def onSorted(self, *args, **kwargs):
        self.__itemsByIndex = dict()
        super(TreeViewer, self).onSorted(*args, **kwargs)
    
    def visibleItems(self):
        ''' Iterate over the items in the model. '''            
        def yieldAllChildren(parent):
            for item in self.model():
                itemParent = self.getItemParent(item)
                if itemParent and itemParent == parent:
                    yield item
                    for child in yieldAllChildren(item):
                        yield child
        for item in self.getRootItems():
            yield item
            for child in yieldAllChildren(item):
                yield child

    def getItemWithIndex(self, index):
        ''' Return the item in the model with the specified index. index
            is a tuple of indices that specifies the path to the item. E.g.,
            (0,2,1) is (read the tuple from right to left) the second child 
            of the third child of the first root item. '''
        # This is performance critical code
        try:
            return self.__itemsByIndex[index]
        except KeyError:
            pass
        children = self.getRootItems()
        model = self.model()
        for i in index[:-1]:
            item = children[i]
            childIndices = [model.index(child) for child in item.children() \
                            if child in model]
            childIndices.sort()
            children = [model[childIndex] for childIndex in childIndices]
        self.__itemsByIndex[index] = item = children[index[-1]]
        return item
        
    def getRootItems(self):
        ''' Allow for overriding what the rootItems are. '''
        return self.model().rootItems()

    def getIndexOfItem(self, item):
        parent = self.getItemParent(item)
        if parent:
            children = [child for child in self.model() if child.parent() == parent]
            return self.getIndexOfItem(parent) + (children.index(item),)
        else:
            return (self.getRootItems().index(item),)
            
    def getItemParent(self, item):
        ''' Allow for overriding what the parent of an item is. '''
        return item.parent()
        
    def getChildrenCount(self, index):
        if index == ():
            return len(self.getRootItems())
        else:
            item = self.getItemWithIndex(index)
            return len([child for child in item.children() if child in self.model()])
    
    def getItemExpanded(self, index):
        item = self.getItemWithIndex(index)
        return item.isExpanded()
    
    
class UpdatePerSecondViewer(Viewer, date.ClockObserver):
    def __init__(self, *args, **kwargs):
        self.__trackedItems = set()
        super(UpdatePerSecondViewer, self).__init__(*args, **kwargs)
        patterns.Publisher().registerObserver(self.onStartTracking,
            eventType=self.trackStartEventType())
        patterns.Publisher().registerObserver(self.onStopTracking,
            eventType=self.trackStopEventType())
        self.addTrackedItems(self.trackedItems(self.list))
        
    def setModel(self, model):
        self.removeTrackedItems(self.trackedItems(self.model()))
        super(UpdatePerSecondViewer, self).setModel(model)
        self.addTrackedItems(self.trackedItems(self.model()))
                        
    def trackStartEventType(self):
        raise NotImplementedError
    
    def trackStopEventType(self):
        raise NotImplementedError

    def onAddItem(self, event):
        self.addTrackedItems(self.trackedItems(event.values()))
        super(UpdatePerSecondViewer, self).onAddItem(event)

    def onRemoveItem(self, event):
        self.removeTrackedItems(self.trackedItems(event.values()))
        super(UpdatePerSecondViewer, self).onRemoveItem(event)

    def onStartTracking(self, event):
        item = event.source()
        if item in self.list:
            self.addTrackedItems([item])

    def onStopTracking(self, event):
        item = event.source()
        if item in self.list:
            self.removeTrackedItems([item])
            
    def currentlyTrackedItems(self):
        return list(self.__trackedItems)

    def onEverySecond(self, event):
        trackedItemsToRemove = []
        for item in self.__trackedItems:
            # Prepare for a ValueError, because we might receive a clock
            # notification before we receive a 'remove item' notification for
            # an item that has been removed from the observed collection.
            try:
                self.widget.RefreshItem(self.getIndexOfItem(item))
            except ValueError:
                trackedItemsToRemove.append(item)
        self.removeTrackedItems(trackedItemsToRemove)
            
    def addTrackedItems(self, items):
        if items:
            self.__trackedItems.update(items)
            self.startClockIfNecessary()

    def removeTrackedItems(self, items):
        if items:
            self.__trackedItems.difference_update(items)
            self.stopClockIfNecessary()

    def startClockIfNecessary(self):
        if self.__trackedItems and not self.isClockStarted():
            self.startClock()

    def stopClockIfNecessary(self):
        if not self.__trackedItems and self.isClockStarted():
            self.stopClock()

    @staticmethod
    def trackedItems(items):
        return [item for item in items if item.isBeingTracked(recursive=True)]

        
class ViewerWithColumns(Viewer):
    def __init__(self, *args, **kwargs):
        self.__initDone = False
        self.__visibleColumns = []
        self.__columnUICommands = None
        super(ViewerWithColumns, self).__init__(*args, **kwargs)
        self.initColumns()
        self.__initDone = True
        self.refresh()
        
    def hasHideableColumns(self):
        return True
    
    def getColumnUICommands(self):
        if not self.__columnUICommands:
            self.__columnUICommands = self.createColumnUICommands()
        return self.__columnUICommands

    def createColumnUICommands(self):
        raise NotImplementedError
    
    def refresh(self, *args, **kwargs):
        if self.__initDone:
            super(ViewerWithColumns, self).refresh(*args, **kwargs)
                    
    def initColumns(self):
        for column in self.columns():
            self.initColumn(column)

    def initColumn(self, column):
        if column.name() in self.settings.getlist(self.settingsSection(), 
                                                  'columnsalwaysvisible'):
            show = True
        else:
            show = column.name() in self.settings.getlist(self.settingsSection(), 'columns')
            self.widget.showColumn(column, show=show)
        if show:
            self.__visibleColumns.append(column)
            self.__startObserving(column.eventTypes())
    
    def showColumnByName(self, columnName, show=True):
        for column in self.hideableColumns():
            if columnName == column.name():
                isVisibleColumn = self.isVisibleColumn(column)
                if (show and not isVisibleColumn) or \
                   (not show and isVisibleColumn):
                    self.showColumn(column, show)
                break

    def showColumn(self, column, show=True):
        if show:
            self.__visibleColumns.append(column)
            # Make sure we keep the columns in the right order:
            self.__visibleColumns = [c for c in self.columns() if \
                                     c in self.__visibleColumns]
            self.__startObserving(column.eventTypes())
        else:
            self.__visibleColumns.remove(column)
            self.__stopObserving(column.eventTypes())
        self.widget.showColumn(column, show)
        self.settings.set(self.settingsSection(), 'columns', 
            str([column.name() for column in self.__visibleColumns]))
        self.widget.RefreshItems()

    def hideColumn(self, visibleColumnIndex):
        column = self.visibleColumns()[visibleColumnIndex]
        self.showColumn(column, show=False)
                
    def onAttributeChanged(self, event):
        item = event.source()
        if item in self.list:
            self.widget.RefreshItem(self.getIndexOfItem(item))
        
    def columns(self):
        return self._columns
    
    def isVisibleColumnByName(self, columnName):
        return columnName in [column.name() for column in self.__visibleColumns]
        
    def isVisibleColumn(self, column):
        return column in self.__visibleColumns
    
    def visibleColumns(self):
        return self.__visibleColumns
        
    def hideableColumns(self):
        return [column for column in self._columns if column.name() not in \
                self.settings.getlist(self.settingsSection(), 'columnsalwaysvisible')]
                
    def isHideableColumn(self, visibleColumnIndex):
        column = self.visibleColumns()[visibleColumnIndex]
        return column.name() not in self.settings.getlist(self.settingsSection(), 
                                                          'columnsalwaysvisible')

    def getColumnWidth(self, columnName):
        columnWidths = self.settings.getdict(self.settingsSection(),
                                             'columnwidths')
        return columnWidths.get(columnName, wx.gizmos.DEFAULT_COL_WIDTH)

    def onResizeColumn(self, column, width):
        columnWidths = self.settings.getdict(self.settingsSection(), 'columnwidths')
        columnWidths[column.name()] = width
        self.settings.setdict(self.settingsSection(), 'columnwidths', columnWidths)
                            
    def getItemText(self, index, column=0):
        item = self.getItemWithIndex(index)
        column = self.visibleColumns()[column]
        return column.render(item)

    def getItemTooltipText(self, index, column=0):
        if self.settings.getboolean('view', 'descriptionpopups'):
            item = self.getItemWithIndex(index)
            column = self.visibleColumns()[column]
            return column.renderDescription(item)
        else:
            return ''

    def getItemImage(self, index, which, column=0): 
        item = self.getItemWithIndex(index)
        column = self.visibleColumns()[column]
        return column.imageIndex(item, which) 
            
    def __startObserving(self, eventTypes):
        for eventType in eventTypes:
            patterns.Publisher().registerObserver(self.onAttributeChanged, 
                eventType=eventType)                    
        
    def __stopObserving(self, eventTypes):
        for eventType in eventTypes:
            patterns.Publisher().removeObserver(self.onAttributeChanged, 
                eventType=eventType)

    def renderCategory(self, item, recursive=False):
        return ', '.join(sorted([category.subject(recursive=True) for category in \
                                 item.categories(recursive=recursive)]))


class SortableViewerWithColumns(SortableViewer, ViewerWithColumns):
    def initColumn(self, column):
        super(SortableViewerWithColumns, self).initColumn(column)
        if self.isSortedBy(column.name()):
            self.widget.showSortColumn(column)
            self.showSortOrder()

    def setSortOrderAscending(self, *args, **kwargs):
        super(SortableViewerWithColumns, self).setSortOrderAscending(*args, **kwargs)
        self.showSortOrder()
        
    def sortBy(self, *args, **kwargs):
        super(SortableViewerWithColumns, self).sortBy(*args, **kwargs)
        self.showSortColumn()

    def showSortColumn(self):
        for column in self.columns():
            if self.isSortedBy(column.name()):
                self.widget.showSortColumn(column)
                break

    def showSortOrder(self):
        self.widget.showSortOrder(self.imageIndex[self.getSortOrderImageIndex()])
        
    def getSortOrderImageIndex(self):
        if self.isSortOrderAscending():
            return 'ascending' 
        else: 
            return 'descending'


class TaskViewer(AttachmentDropTarget, FilterableViewerForTasks, 
                 SortableViewerForTasks, SearchableViewer, 
                 UpdatePerSecondViewer):
    def __init__(self, *args, **kwargs):
        self.categories = kwargs.pop('categories')
        self.efforts = kwargs.pop('efforts')
        super(TaskViewer, self).__init__(*args, **kwargs)
        self.__registerForColorChanges()
            
    def isShowingTasks(self): 
        return True
    
    def createColumnUICommands(self):
        return [\
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
                 setting='recurrence', viewer=self)
            ),
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
                 setting='totalRevenue', viewer=self)
            ),
            uicommand.ViewColumn(menuText=_('&Description'),
                helpText=_('Show/hide description column'),
                setting='description', viewer=self),
            uicommand.ViewColumn(menuText=_('&Attachments'),
                helpText=_('Show/hide attachment column'),
                setting='attachments', viewer=self),
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
                setting='reminder', viewer=self)]

    def createToolBarUICommands(self):
        ''' UI commands to put on the toolbar of this viewer. '''
        toggleTaskCompletion = uicommand.TaskToggleCompletion(viewer=self)
        effortstart = uicommand.EffortStart(viewer=self)
        effortstop = uicommand.EffortStop(taskList=self.model())
        commands = super(TaskViewer, self).createToolBarUICommands() 
        return commands[:-1] + [toggleTaskCompletion, None, effortstart, 
            effortstop, None] + commands[-1:]
 
    def trackStartEventType(self):
        return 'task.track.start'
    
    def trackStopEventType(self):
        return 'task.track.stop'
   
    def statusMessages(self):
        status1 = _('Tasks: %d selected, %d visible, %d total')%\
            (len(self.curselection()), len(self.list), 
             self.list.originalLength())         
        status2 = _('Status: %d over due, %d inactive, %d completed')% \
            (self.list.nrOverdue(), self.list.nrInactive(),
             self.list.nrCompleted())
        return status1, status2
 
    def createTaskPopupMenu(self):
        return menu.TaskPopupMenu(self.parent, self.settings,
                                  self.model(), self.categories, self.efforts,
                                  self)

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
        if task in self.model():
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
            'descending_with_status', 'attachment']):
            imageList.Add(wx.ArtProvider_GetBitmap(image, wx.ART_MENU, (16,16)))
            self.imageIndex[image] = index
        return imageList
    
    def getImageIndices(self, task):
        bitmap, bitmap_selected = render.taskBitmapNames(task)
        return self.imageIndex[bitmap], self.imageIndex[bitmap_selected]

    # The methods below have two names. This is because there are two types
    # of domain object related UICommands. The generic variant works on
    # whatever type of domain object is shown in the current viewer. The
    # specific variant works on one specific type of domain object.
    # When a generic UICommand is invoked, e.g. uicommand.EditDomainObject, 
    # it will use 'itemEditor' to get a domain object editor for the current 
    # viewer. But when a specific UICommand is invoked, e.g. uicommand.EditTask, 
    # a TaskEditor needs to be returned, independently of which viewer is 
    # current. So, uicommand.NewTask will call taskEditor() to force a 
    # task editor. 
    
    def newItemDialog(self, *args, **kwargs):
        bitmap = kwargs.pop('bitmap')
        kwargs['categories'] = [category for category in self.categories
                                if category.isFiltered()]
        return dialog.editor.TaskEditor(wx.GetTopLevelParent(self), 
            command.NewTaskCommand(self.list, *args, **kwargs), self.list,
            self.settings, self.categories, bitmap=bitmap)
    
    def editItemDialog(self, *args, **kwargs):
        return dialog.editor.TaskEditor(wx.GetTopLevelParent(self),
            command.EditTaskCommand(self.list, self.curselection()),
            self.list, self.settings, self.categories,
            bitmap=kwargs['bitmap'])
    
    editTaskDialog = editItemDialog
    
    def deleteItemCommand(self):
        return command.DeleteTaskCommand(self.list, self.curselection())
        
    deleteTaskCommand = deleteItemCommand
    
    def newSubItemDialog(self, *args, **kwargs):
        return dialog.editor.TaskEditor(wx.GetTopLevelParent(self), 
            command.NewSubTaskCommand(self.list, self.curselection()), 
            self.list, self.settings, self.categories,
            bitmap=kwargs['bitmap'])
        
    newSubTaskDialog = newSubItemDialog
           
            
class TaskViewerWithColumns(TaskViewer, SortableViewerWithColumns):
    def __init__(self, *args, **kwargs):
        self.__sortKeyUnchangedCount = 0
        super(TaskViewerWithColumns, self).__init__(*args, **kwargs)
                            
    def _createColumns(self):
        kwargs = dict(renderDescriptionCallback=lambda task: task.description(),
                      resizeCallback=self.onResizeColumn)
        return [widgets.Column('subject', _('Subject'), 
                task.Task.subjectChangedEventType(), 
                'task.completionDate', 'task.dueDate', 'task.startDate',
                'task.track.start', 'task.track.stop', 
                sortCallback=uicommand.ViewerSortByCommand(viewer=self,
                                                           value='subject',
                    menuText=_('Sub&ject'), helpText=_('Sort by subject')),
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
                renderCallback=lambda task: '', **kwargs)] + \
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
                width=self.getColumnWidth('totalCategories'), **kwargs)] + \
            [widgets.Column(name, columnHeader, 'task.'+name, 
             sortCallback=uicommand.ViewerSortByCommand(viewer=self, value=name),
             renderCallback=renderCallback, width=self.getColumnWidth(name),
             alignment=wx.LIST_FORMAT_RIGHT, **kwargs) \
             for name, columnHeader, renderCallback in \
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
            ('reminder', _('Reminder'), lambda task: render.dateTime(task.reminder()))]
                        
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
                
    def createColumnPopupMenu(self):
        return menu.ColumnPopupMenu(self)

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
        super(TaskViewerWithColumns, self).sortBy(sortKey)
            
    def setSortByTaskStatusFirst(self, *args, **kwargs):
        super(TaskViewerWithColumns, self).setSortByTaskStatusFirst(*args, **kwargs)
        self.showSortOrder()
        
    def getSortOrderImageIndex(self):
        sortOrderImageIndex = super(TaskViewerWithColumns, self).getSortOrderImageIndex()
        if self.isSortByTaskStatusFirst():
            sortOrderImageIndex += '_with_status' 
        return sortOrderImageIndex


class TaskTreeListViewer(TaskViewerWithColumns, TreeViewer):
    defaultTitle = _('Tasks')
     
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('settingsSection', 'tasktreelistviewer')
        super(TaskTreeListViewer, self).__init__(*args, **kwargs)
        self.treeOrListUICommand.setChoice(self.isTreeViewer())
        
    def createWidget(self):
        imageList = self.createImageList() # Has side-effects
        self._columns = self._createColumns()
        widget = widgets.TreeListCtrl(self, self.columns(), self.getItemText,
            self.getItemTooltipText, self.getItemImage, self.getItemAttr,
            self.getChildrenCount, self.getItemExpanded, self.onSelect, 
            uicommand.TaskEdit(taskList=self.model(), viewer=self),
            uicommand.TaskDragAndDrop(taskList=self.model(), viewer=self),
            self.createTaskPopupMenu(), self.createColumnPopupMenu(),
            **self.widgetCreationKeywordArguments())
        widget.AssignImageList(imageList)
        return widget    

    def getToolBarUICommands(self):
        ''' UI commands to put on the toolbar of this viewer. '''
        toolBarUICommands = super(TaskTreeListViewer, self).getToolBarUICommands() 
        toolBarUICommands.insert(-2, None) # Separator
        self.treeOrListUICommand = \
            uicommand.TaskViewerTreeOrListChoice(viewer=self)
        toolBarUICommands.insert(-2, self.treeOrListUICommand)
        return toolBarUICommands

    def setSearchFilter(self, searchString, *args, **kwargs):
        super(TaskTreeListViewer, self).setSearchFilter(searchString, *args, **kwargs)
        if searchString:
            self.expandAll()

    def showTree(self, treeMode):
        self.settings.set(self.settingsSection(), 'treemode', str(treeMode))
        self.model().setTreeMode(treeMode)
        
    def isTreeViewer(self):
        return self.settings.getboolean(self.settingsSection(), 'treemode')
        
    def renderSubject(self, task):
        return task.subject(recursive=not self.isTreeViewer())

    def getRootItems(self):
        ''' If the viewer is in tree mode, return the real root items. If the
            viewer is in list mode, return all items. '''
        if self.isTreeViewer():
            return super(TaskTreeListViewer, self).getRootItems()
        else:
            return self.model()
    
    def getItemParent(self, item):
        if self.isTreeViewer():
            return super(TaskTreeListViewer, self).getItemParent(item)
        else:
            return None
            
    def getChildrenCount(self, index):
        if self.isTreeViewer() or (index == ()):
            return super(TaskTreeListViewer, self).getChildrenCount(index)
        else:
            return 0


class CategoryViewer(AttachmentDropTarget, SortableViewerForCategories, 
                     SearchableViewer, TreeViewer):
    SorterClass = category.CategorySorter
    defaultTitle = _('Categories')
    
    def __init__(self, *args, **kwargs):
        self.tasks = kwargs.pop('tasks')
        self.notes = kwargs.pop('notes')
        kwargs.setdefault('settingsSection', 'categoryviewer')
        super(CategoryViewer, self).__init__(*args, **kwargs)
        for eventType in category.Category.subjectChangedEventType(), \
                         category.Category.filterChangedEventType(), \
                         category.Category.colorChangedEventType():
            patterns.Publisher().registerObserver(self.onCategoryChanged, 
                eventType)
        self.filterUICommand.setChoice(self.settings.getboolean('view',
            'categoryfiltermatchall'))
    
    def createWidget(self):
        widget = widgets.CheckTreeCtrl(self, self.getItemText, self.getItemTooltipText,
            self.getItemImage, self.getItemAttr, self.getChildrenCount,
            self.getItemExpanded,
            self.getIsItemChecked, self.onSelect, self.onCheck,
            uicommand.CategoryEdit(viewer=self, categories=self.model()),
            uicommand.CategoryDragAndDrop(viewer=self, categories=self.model()),
            self.createCategoryPopupMenu(), 
            **self.widgetCreationKeywordArguments())
        return widget

    def createCategoryPopupMenu(self):
        return menu.CategoryPopupMenu(self.parent, self.settings, self.tasks,
                                      self.notes, self.model(), self)

    def createFilter(self, categories):
        return base.SearchFilter(categories, treeMode=True)
    
    def getToolBarUICommands(self):
        ''' UI commands to put on the toolbar of this viewer. '''
        toolBarUICommands = super(CategoryViewer, self).getToolBarUICommands()
        toolBarUICommands.insert(-2, None) # Separator
        self.filterUICommand = \
            uicommand.CategoryViewerFilterChoice(settings=self.settings)
        toolBarUICommands.insert(-2, self.filterUICommand)
        return toolBarUICommands

    def onCategoryChanged(self, event):
        category = event.source()
        if category in self.list:
            self.widget.RefreshItem(self.getIndexOfItem(category))

    def onCheck(self, event):
        category = self.getItemWithIndex(self.widget.GetIndexOfItem(event.GetItem()))
        category.setFiltered(event.GetItem().IsChecked())
        self.onSelect(event) # Notify status bar
            
    def getItemText(self, index):    # FIXME: pull up to TreeViewer
        item = self.getItemWithIndex(index)
        return item.subject()

    def getItemTooltipText(self, index):
        if self.settings.getboolean('view', 'descriptionpopups'):
            item = self.getItemWithIndex(index)
            return item.description()
        else:
            return ''

    def getItemImage(self, index, which):
        return -1
    
    def getBackgroundColor(self, item):
        return item.color()
    
    def getItemAttr(self, index):
        item = self.getItemWithIndex(index)
        return wx.ListItemAttr(colBack=self.getBackgroundColor(item))
    
    def getIsItemChecked(self, index):
        item = self.getItemWithIndex(index)
        if isinstance(item, category.Category):
            return item.isFiltered()
        return False

    def isShowingCategories(self):
        return True

    def statusMessages(self):
        status1 = _('Categories: %d selected, %d total')%\
            (len(self.curselection()), len(self.list))
        status2 = _('Status: %d filtered')%len([category for category in self.list if category.isFiltered()])
        return status1, status2

    def newItemDialog(self, *args, **kwargs):
        return dialog.editor.CategoryEditor(wx.GetTopLevelParent(self), 
            command.NewCategoryCommand(self.list, *args, **kwargs),
            self.settings, self.list, bitmap=kwargs['bitmap'])
    
    # See TaskViewer for why the methods below have two names.
    
    def editItemDialog(self, *args, **kwargs):
        return dialog.editor.CategoryEditor(wx.GetTopLevelParent(self),
            command.EditCategoryCommand(self.list, self.curselection()),
            self.settings, self.list, bitmap=kwargs['bitmap'])
    
    editCategoryDialog = editItemDialog
    
    def deleteItemCommand(self):
        return command.DeleteCommand(self.list, self.curselection())
    
    deleteCategoryCommand = deleteItemCommand
    
    def newSubItemDialog(self, *args, **kwargs):
        return dialog.editor.CategoryEditor(wx.GetTopLevelParent(self), 
            command.NewSubCategoryCommand(self.list, self.curselection()),
            self.settings, self.list, bitmap=kwargs['bitmap'])
        
    newSubCategoryDialog = newSubItemDialog


class NoteViewer(AttachmentDropTarget, FilterableViewerForNotes, 
                 SearchableViewer, SortableViewerWithColumns, 
                 SortableViewerForNotes, TreeViewer):
    SorterClass = note.NoteSorter
    defaultTitle = _('Notes')
    
    def __init__(self, *args, **kwargs):
        self.categories = kwargs.pop('categories')
        kwargs.setdefault('settingsSection', 'noteviewer')
        super(NoteViewer, self).__init__(*args, **kwargs)
        for eventType in [note.Note.subjectChangedEventType()]:
            patterns.Publisher().registerObserver(self.onNoteChanged, 
                eventType)
        patterns.Publisher().registerObserver(self.onColorChange,
            eventType=note.Note.colorChangedEventType())
        
    def onColorChange(self, event):
        note = event.source()
        if note in self.model():
            self.widget.RefreshItem(self.getIndexOfItem(note))

    def createWidget(self):
        imageList = self.createImageList() # Has side-effects
        self._columns = self._createColumns()
        widget = widgets.TreeListCtrl(self, self.columns(), self.getItemText, 
            self.getItemTooltipText, self.getItemImage, self.getItemAttr, 
            self.getChildrenCount, self.getItemExpanded, self.onSelect,
            uicommand.NoteEdit(viewer=self, notes=self.model()),
            uicommand.NoteDragAndDrop(viewer=self, notes=self.model()),
            menu.NotePopupMenu(self.parent, self.settings, self.model(),
                               self.categories, self), 
            menu.ColumnPopupMenu(self),
            **self.widgetCreationKeywordArguments())
        widget.AssignImageList(imageList)
        return widget
    
    def createFilter(self, notes):
        notes = super(NoteViewer, self).createFilter(notes)
        return base.SearchFilter(notes, treeMode=True)
    
    def createImageList(self):
        imageList = wx.ImageList(16, 16)
        self.imageIndex = {}
        for index, image in enumerate(['ascending', 'descending', 'attachment']):
            imageList.Add(wx.ArtProvider_GetBitmap(image, wx.ART_MENU, (16,16)))
            self.imageIndex[image] = index
        return imageList

    def attachmentImageIndex(self, note, which):
        if note.attachments():
            return self.imageIndex['attachment'] 
        else:
            return -1

    def createColumnUICommands(self):
        return [\
            uicommand.ViewColumn(menuText=_('&Description'),
                helpText=_('Show/hide description column'),
                setting='description', viewer=self),
            uicommand.ViewColumn(menuText=_('&Attachments'),
                helpText=_('Show/hide attachments column'),
                setting='attachments', viewer=self),
            uicommand.ViewColumn(menuText=_('&Categories'),
                helpText=_('Show/hide categories column'),
                setting='categories', viewer=self),
            uicommand.ViewColumn(menuText=_('Overall categories'),
                helpText=_('Show/hide overall categories column'),
                setting='totalCategories', viewer=self)]

    def _createColumns(self):
        columns = [widgets.Column(name, columnHeader,
                width=self.getColumnWidth(name), 
                resizeCallback=self.onResizeColumn,
                renderCallback=renderCallback, 
                sortCallback=uicommand.ViewerSortByCommand(viewer=self, 
                    value=name.lower(), menuText=sortMenuText, 
                    helpText=sortHelpText),
                *eventTypes) \
            for name, columnHeader, sortMenuText, sortHelpText, eventTypes, renderCallback in \
            ('subject', _('Subject'), _('&Subject'), _('Sort notes by subject'), 
                (note.Note.subjectChangedEventType(),), 
                lambda note: note.subject(recursive=False)),
            ('description', _('Description'), _('&Description'), 
                _('Sort notes by description'), 
                (note.Note.descriptionChangedEventType(),), 
                lambda note: note.description()),
            ('categories', _('Categories'), _('&Categories'), 
                _('Sort notes by categories'), 
                (note.Note.categoryAddedEventType(), 
                 note.Note.categoryRemovedEventType(), 
                 note.Note.categorySubjectChangedEventType()), 
                self.renderCategory),
            ('totalCategories', _('Overall categories'), 
                _('&Overall categories'), _('Sort notes by overall categories'),
                 (note.Note.totalCategoryAddedEventType(),
                  note.Note.totalCategoryRemovedEventType(),
                  note.Note.totalCategorySubjectChangedEventType()), 
                 self.renderCategory)]
        attachmentsColumn = widgets.Column('attachments', '', 
            note.Note.attachmentsChangedEventType(),
            width=self.getColumnWidth('attachments'),
            alignment=wx.LIST_FORMAT_LEFT,
            imageIndexCallback=self.attachmentImageIndex,
            headerImageIndex=self.imageIndex['attachment'],
            renderCallback=lambda note: '')
        columns.insert(2, attachmentsColumn)
        return columns
                     
    def onNoteChanged(self, event):
        note = event.source()
        if note in self.list:
            self.widget.RefreshItem(self.getIndexOfItem(note))
            
    def getItemText(self, index, column=0):
        item = self.getItemWithIndex(index)
        column = self.visibleColumns()[column]
        return column.render(item)

    def getItemTooltipText(self, index, column=0):
        if self.settings.getboolean('view', 'descriptionpopups'):
            note = self.getItemWithIndex(index)
            return note.description()
        else:
            return None
    
    def getBackgroundColor(self, note):
        return note.color()
    
    def getItemAttr(self, index):
        note = self.getItemWithIndex(index)
        return wx.ListItemAttr(None, self.getBackgroundColor(note))
                
    def isShowingNotes(self):
        return True

    def statusMessages(self):
        status1 = _('Notes: %d selected, %d total')%\
            (len(self.curselection()), len(self.list))
        status2 = _('Status: n/a')
        return status1, status2

    def newItemDialog(self, *args, **kwargs):
        filteredCategories = [category for category in self.categories if
                              category.isFiltered()]
        return dialog.editor.NoteEditor(wx.GetTopLevelParent(self), 
            command.NewNoteCommand(self.list, categories=filteredCategories, 
            *args, **kwargs),
            self.settings, self.categories, bitmap=kwargs['bitmap'])
    
    # See TaskViewer for why the methods below have two names.
    
    def editItemDialog(self, *args, **kwargs):
        return dialog.editor.NoteEditor(wx.GetTopLevelParent(self),
            command.EditNoteCommand(self.list, self.curselection()),
            self.settings, self.categories, bitmap=kwargs['bitmap'])
    
    editNoteDialog = editItemDialog
    
    def deleteItemCommand(self):
        return command.DeleteCommand(self.list, self.curselection())
    
    deleteNoteCommand = deleteItemCommand
    
    def newSubItemDialog(self, *args, **kwargs):
        return dialog.editor.NoteEditor(wx.GetTopLevelParent(self), 
            command.NewSubNoteCommand(self.list, self.curselection()),
            self.settings, self.categories, bitmap=kwargs['bitmap'])
        
    newSubNoteDialog = newSubItemDialog
    
    
class EffortViewer(SortableViewerForEffort, SearchableViewer, 
                   UpdatePerSecondViewer):
    SorterClass = effort.EffortSorter
    
    def isSortable(self):
        return False # FIXME: make effort viewers sortable too?
    
    def isShowingEffort(self):
        return True
    
    def trackStartEventType(self):
        return 'effort.track.start'
    
    def trackStopEventType(self):
        return 'effort.track.stop'

    def getToolBarUICommands(self):
        ''' Names of UI commands to put on the toolbar of this viewer. '''
        toolBarUICommands = super(EffortViewer, self).getToolBarUICommands()
        del toolBarUICommands[5] # Remove 'new subitem'
        return toolBarUICommands

    def statusMessages(self):
        status1 = _('Effort: %d selected, %d visible, %d total')%\
            (len(self.curselection()), len(self.list), 
             self.list.originalLength())         
        status2 = _('Status: %d tracking')% self.list.nrBeingTracked()
        return status1, status2
 
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
    
    editEffortDialog = editItemDialog
    
    def deleteItemCommand(self):
        return command.DeleteCommand(self.list, self.curselection())
    
    deleteEffortCommand = deleteItemCommand
    
    def canCreateNewDomainObject(self):
        return len(self.taskList) > 0
    

class EffortListViewer(ListViewer, EffortViewer, ViewerWithColumns): 
    defaultTitle = _('Effort')  
    
    def __init__(self, parent, list, *args, **kwargs):
        self.aggregation = 'details'
        self.taskList = base.SearchFilter(list)
        kwargs.setdefault('settingsSection', 'effortlistviewer')
        self.__hiddenTotalColumns = []
        super(EffortListViewer, self).__init__(parent, self.taskList, *args, **kwargs)
        self.aggregation = self.settings.get(self.settingsSection(), 'aggregation')
        self.aggregationUICommand.setChoice(self.aggregation)
        
    def showEffortAggregation(self, aggregation):
        ''' Change the aggregation mode. Can be one of 'details', 'day', 'week'
            and 'month'. '''
        assert aggregation in ('details', 'day', 'week', 'month')
        self.aggregation = aggregation
        self.settings.set(self.settingsSection(), 'aggregation', aggregation)
        self.setModel(self.createSorter(self.createAggregator(self.taskList, 
                                                            aggregation)))
        self.registerModelObservers()
        self._showTotalColumns(show=aggregation!='details')
        self.refresh()

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
            self.getItemText, self.getItemTooltipText, self.getItemImage,
            self.getItemAttr, self.onSelect,
            uicommand.EffortEdit(viewer=self, effortList=self.model()),
            menu.EffortPopupMenu(self.parent, self.taskList,
                                 self.model(), self),
            menu.EffortViewerColumnPopupMenu(self.parent, self),
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
                 lambda effort: render.amount(effort.revenue(recursive=True)))]

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

    # Since the  aggregation can change  in the viewer's  lifetime and
    # the UICommands depend on it, this is getColumnUICommands instead
    # of createColumnUICommands.

    def getColumnUICommands(self):
        commands = [uicommand.ViewColumn(menuText=_('&Description'),
                                  helpText=_('Show/hide description column'),
                                  setting='description', viewer=self),
                uicommand.ViewColumn(menuText=_('&Time spent'),
                                  helpText=_('Show/hide time spent column'),
                                  setting='timeSpent', viewer=self),
                uicommand.ViewColumn(menuText=_('&Revenue'),
                                  helpText=_('Show/hide revenue column'),
                                  setting='revenue', viewer=self),]
        if self.aggregation != 'details':
            commands.insert(-1, uicommand.ViewColumn(menuText=_('&Total time spent'),
                   helpText=_('Show/hide total time spent column'),
                   setting='totalTimeSpent',
                   viewer=self))
            commands.append(uicommand.ViewColumn(menuText=_('Total &revenue'),
                   helpText=_('Show/hide total revenue column'),
                   setting='totalRevenue',
                   viewer=self))
        return commands

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
    
    def getItemAttr(self, index):
        return wx.ListItemAttr()

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

