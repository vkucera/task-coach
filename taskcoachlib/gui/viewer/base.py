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
from taskcoachlib import patterns, widgets, command
from taskcoachlib.domain import date
from taskcoachlib.i18n import _
from taskcoachlib.gui import uicommand, toolbar
import mixin


class Viewer(wx.Panel):
    __metaclass__ = patterns.NumberedInstances
    
    ''' A Viewer shows domain objects (e.g. tasks or efforts) by means of a 
        widget (e.g. a ListCtrl or a TreeListCtrl).'''
        
    def __init__(self, parent, taskFile, settings, *args, **kwargs):
        super(Viewer, self).__init__(parent, -1)
        self.parent = parent # FIXME: Make instance variables private
        self.taskFile = taskFile
        self.settings = settings
        self.__settingsSection = kwargs.pop('settingsSection')
        self.__instanceNumber = kwargs.pop('instanceNumber')
        self.__selection = []
        # Flag so that we don't notify observers while we're selecting all items
        self.__selectingAllItems = False
        self.__toolbarUICommands = None
        self.__presentation = self.createSorter(self.createFilter(self.domainObjectsToView()))
        self.widget = self.createWidget()
        self.toolbar = toolbar.ToolBar(self, (16, 16))
        self.initLayout()
        self.registerPresentationObservers()
        self.refresh()
        
    def domainObjectsToView(self):
        ''' Return the domain objects that this viewer should display. For
            global viewers this will be part of the task file, 
            e.g. self.taskFile.tasks(), for local viewers this will be a list
            of objects passed to the viewer constructor. '''
        raise NotImplementedError
    
    def registerPresentationObservers(self):
        patterns.Publisher().removeObserver(self.onPresentationChanged)
        registerObserver = patterns.Publisher().registerObserver
        registerObserver(self.onPresentationChanged, 
                         eventType=self.presentation().addItemEventType(),
                         eventSource=self.presentation())
        registerObserver(self.onPresentationChanged, 
                         eventType=self.presentation().removeItemEventType(),
                         eventSource=self.presentation())
        
    def detach(self):
        ''' Should be called by viewer.container before closing the viewer '''
        patterns.Publisher().removeInstance(self.presentation())
        patterns.Publisher().removeInstance(self)

    @classmethod
    def selectEventType(class_):
        return '%s.select'%class_
    
    def title(self):
        return self.settings.get(self.settingsSection(), 'title') or self.defaultTitle
    
    def setTitle(self, title):
        titleToSaveInSettings = '' if title == self.defaultTitle else title
        self.settings.set(self.settingsSection(), 'title', titleToSaveInSettings)
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
        ''' This method can be overridden to decorate the presentation with a 
            sorter. '''
        return collection
        
    def createFilter(self, collection):
        ''' This method can be overridden to decorate the presentation with a 
            filter. '''
        return collection

    def onAttributeChanged(self, event):
        self.refreshItems(*event.sources())
        
    def onPresentationChanged(self, event):
        ''' Whenever our presentation is changed (items added, items removed,
            order changed) the viewer refreshes itself. '''
        self.refresh()
        
    def onSelect(self, *args):
        ''' The selection of items in the widget has been changed. Notify 
            our observers and remember the current selection so we can
            restore it later, e.g. after the sort order is changed. '''
        if self.IsBeingDeleted() or self.__selectingAllItems:
            # Some widgets change the selection and send selection events when 
            # deleting all items as part of the Destroy process. Ignore.
            return
        # Be sure all wx events are handled before we notify our observers: 
        wx.CallAfter(lambda: patterns.Event(self.selectEventType(), self, self.curselection()).send())
        # Remember the current selection so we can restore it after a refresh:
        self.__selection = self.curselection()

    def refresh(self):
        self.widget.RefreshAllItems(len(self.presentation()))
        # Restore the selection:
        self.widget.select([self.getIndexOfItem(item) for item \
                            in self.__selection if item in self.presentation()])
    
    def refreshItems(self, *items):
        indices = [self.getIndexOfItem(item) for item in items \
                   if item in self.presentation()]
        self.widget.RefreshItems(*indices)
                        
    def curselection(self):
        ''' Return a list of items (domain objects) currently selected in our
            widget. '''
        # Translate indices returned by the widget into actual domain objects:
        return [self.getItemWithIndex(index) for index in \
                self.widget.curselection()]
        
    def curselectionIsInstanceOf(self, class_):
        ''' Return whether all items in the current selection are instances of
            class_. Can be overridden in subclasses that show only one type
            of items to simply check the class. '''
        return all(isinstance(item, class_) for item in self.curselection())

    def isselected(self, item):
        """Returns True if the given item is selected. See
        L{EffortViewer} for an explanation of why this may be
        different than 'if item in viewer.curselection()'."""

        return item in self.curselection()

    def selectall(self):
        ''' Select all items in the presentation. Since some of the widgets we
            use may send events for each individual item (!) we stop processing
            selection events while we select all items. '''
        self.__selectingAllItems = True
        self.widget.selectall()
        # Use CallAfter to make sure we start processing selection events 
        # after all selection events have been fired (and ignored):
        wx.CallAfter(self.endOfSelectAll)
        # Pretend we received one selection event for the selectall() call:
        self.onSelect()
        
    def endOfSelectAll(self):
        self.__selectingAllItems = False
        
    def invertselection(self):
        self.widget.invertselection()
        
    def clearselection(self):
        self.widget.clearselection()
        
    def size(self):
        return self.widget.GetItemCount()
    
    def presentation(self):
        ''' Return the domain objects that this viewer is currently 
            displaying. '''
        return self.__presentation
        
    def setPresentation(self, presentation):
        ''' Change the presentation of the viewer. '''
        self.__presentation = presentation
    
    def widgetCreationKeywordArguments(self):
        return {}

    def isViewerContainer(self):
        return False
    
    def isShowingTasks(self): 
        return False

    def isShowingEffort(self): 
        return False
    
    def isShowingCategories(self):
        return False
    
    def isShowingNotes(self):
        return False

    def isShowingAttachments(self):
        return False

    def visibleColumns(self):
        return [widgets.Column('subject', _('Subject'))]
    
    def itemEditor(self, *args, **kwargs):
        raise NotImplementedError
    
    def getColor(self, item):
        return wx.BLACK
    
    def getBackgroundColor(self, item):
        return None
    
    def bitmap(self):
        ''' Return the bitmap that represents this viewer. Used for the 
            'Viewer->New viewer' menu item, for example. '''
        return self.defaultBitmap # Class attribute of concrete viewers
    
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
        return [
            uicommand.EditCut(viewer=self),
            uicommand.EditCopy(viewer=self),
            uicommand.EditPaste()
            ]
    
    def deleteItemCommand(self):
        return command.DeleteCommand(self.presentation(), self.curselection())


class ListViewer(Viewer):
    def isTreeViewer(self):
        return False

    def visibleItems(self):
        ''' Iterate over the items in the presentation. '''
        for item in self.presentation():
            yield item
    
    def getItemWithIndex(self, index):
        return self.presentation()[index]
            
    def getIndexOfItem(self, item):
        return self.presentation().index(item)
    

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
            item.expand(expanded, context=self.settingsSection())
    
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

    def onPresentationChanged(self, *args, **kwargs):
        self.__itemsByIndex = dict()
        super(TreeViewer, self).onPresentationChanged(*args, **kwargs)
    
    def visibleItems(self):
        ''' Iterate over the items in the presentation. '''            
        def yieldAllChildren(parent):
            for item in self.presentation():
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
        ''' Return the item in the presentation with the specified index. index
            is a tuple of indices that specifies the path to the item. E.g.,
            (0,2,1) is (read the tuple from right to left) the second child 
            of the third child of the first root item. '''
        # This is performance critical code
        try:
            return self.__itemsByIndex[index]
        except KeyError:
            pass
        children = self.getRootItems()
        presentation = self.presentation()
        for i in index[:-1]:
            item = children[i]
            childIndices = [presentation.index(child) for child in item.children() \
                            if child in presentation]
            childIndices.sort()
            children = [presentation[childIndex] for childIndex in childIndices]
        self.__itemsByIndex[index] = item = children[index[-1]]
        return item
        
    def getRootItems(self):
        ''' Allow for overriding what the rootItems are. '''
        return self.presentation().rootItems()

    def getIndexOfItem(self, item):
        parent = self.getItemParent(item)
        if parent:
            children = [child for child in self.presentation() if child.parent() == parent]
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
            return len([child for child in item.children() if child in self.presentation()])
    
    def getItemExpanded(self, index):
        item = self.getItemWithIndex(index)
        return item.isExpanded(context=self.settingsSection())
    
    
class UpdatePerSecondViewer(Viewer, date.ClockObserver):
    def __init__(self, *args, **kwargs):
        self.__trackedItems = set()
        super(UpdatePerSecondViewer, self).__init__(*args, **kwargs)
        patterns.Publisher().registerObserver(self.onStartTracking,
            eventType=self.trackStartEventType())
        patterns.Publisher().registerObserver(self.onStopTracking,
            eventType=self.trackStopEventType())
        self.setTrackedItems(self.trackedItems(self.presentation()))
        
    def setPresentation(self, presentation):
        super(UpdatePerSecondViewer, self).setPresentation(presentation)
        self.setTrackedItems(self.trackedItems(self.presentation()))
                        
    def trackStartEventType(self):
        raise NotImplementedError
    
    def trackStopEventType(self):
        raise NotImplementedError

    def onPresentationChanged(self, event):
        self.setTrackedItems(self.trackedItems(self.presentation()))
        super(UpdatePerSecondViewer, self).onPresentationChanged(event)

    def onStartTracking(self, event):
        self.addTrackedItems([item for item in event.sources() \
                              if item in self.presentation()])

    def onStopTracking(self, event):
        self.removeTrackedItems([item for item in event.sources() \
                                 if item in self.presentation()])
            
    def currentlyTrackedItems(self):
        return list(self.__trackedItems)

    def onEverySecond(self, event):
        self.refreshItems(*self.__trackedItems)
        
    def setTrackedItems(self, items):
        self.__trackedItems = set(items)
        self.startClockIfNecessary()
        self.stopClockIfNecessary()
            
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
        self.__columnUICommands = []
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

    def showColumn(self, column, show=True, refresh=True):
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
        if refresh:
            self.widget.RefreshAllItems(len(self.presentation()))

    def hideColumn(self, visibleColumnIndex):
        column = self.visibleColumns()[visibleColumnIndex]
        self.showColumn(column, show=False)
                
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
                self.settings.getlist(self.settingsSection(), 
                                      'columnsalwaysvisible')]
                
    def isHideableColumn(self, visibleColumnIndex):
        column = self.visibleColumns()[visibleColumnIndex]
        unhideableColumns = self.settings.getlist(self.settingsSection(), 
                                                  'columnsalwaysvisible')
        return column.name() not in unhideableColumns

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

    def getItemTooltipData(self, index, column=0):
        if self.settings.getboolean('view', 'descriptionpopups'):
            item = self.getItemWithIndex(index)
            column = self.visibleColumns()[column]
            if column.renderDescription(item):
                result = [(None, map(lambda x: x.rstrip('\n'),
                                     column.renderDescription(item).split('\n')))]
            else:
                result = []
            try:
                result.append(('note', [note.subject() for note in item.notes()]))
            except AttributeError:
                pass
            try:
                result.append(('attachment', [unicode(attachment) for attachment in item.attachments()]))
            except AttributeError:
                pass
            return result
        else:
            return []

    def getItemImage(self, index, which, column=0): 
        item = self.getItemWithIndex(index)
        column = self.visibleColumns()[column]
        return column.imageIndex(item, which) 
            
    def __startObserving(self, eventTypes):
        for eventType in eventTypes:
            patterns.Publisher().registerObserver(self.onAttributeChanged, 
                eventType=eventType)                    
        
    def __stopObserving(self, eventTypes):
        # Collect the event types that the currently visible columns are
        # interested in and make sure we don't stop observing those event types.
        eventTypesOfVisibleColumns = []
        for column in self.visibleColumns():
            eventTypesOfVisibleColumns.extend(column.eventTypes())
        for eventType in eventTypes:
            if eventType in eventTypesOfVisibleColumns:
                continue
            patterns.Publisher().removeObserver(self.onAttributeChanged, 
                eventType=eventType)

    def renderCategory(self, item, recursive=False):
        return ', '.join(sorted([category.subject(recursive=True) for category in \
                                 item.categories(recursive=recursive)]))


class SortableViewerWithColumns(mixin.SortableViewer, ViewerWithColumns):
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

