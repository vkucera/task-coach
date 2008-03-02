'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>

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

import viewer, wx
from i18n import _

    
def addEffortViewers(viewerContainer, taskList, uiCommands, settings):
    _addViewers(viewerContainer, viewer.EffortListViewer, (taskList, 
                uiCommands, settings), {}, 'start', settings)
    _addViewers(viewerContainer, viewer.EffortPerDayViewer, (taskList, 
                uiCommands, settings), {}, 'date', settings)
    _addViewers(viewerContainer, viewer.EffortPerWeekViewer, (taskList, 
                uiCommands, settings), {}, 'date', settings)
    _addViewers(viewerContainer, viewer.EffortPerMonthViewer, (taskList, 
                uiCommands, settings), {}, 'date', settings)

def addTaskViewers(viewerContainer, taskList, uiCommands, settings, categories):
    _addViewers(viewerContainer, viewer.TaskListViewer, (taskList, uiCommands,
                settings), dict(categories=categories), 'listview', settings)
    _addViewers(viewerContainer, viewer.TaskTreeListViewer, (taskList,
                uiCommands, settings), dict(categories=categories), 
                'treeview', settings)

def addCategoryViewers(viewerContainer, categoryContainer, uiCommands, 
                       settings):
    _addViewers(viewerContainer, viewer.CategoryViewer, (categoryContainer, 
                uiCommands, settings), {}, 'category', settings)
    
def addNoteViewers(viewerContainer, noteContainer, uiCommands, settings, categories):
    _addViewers(viewerContainer, viewer.NoteViewer, (noteContainer, uiCommands,
                settings), dict(categories=categories), 'note', settings)

def _addViewers(viewerContainer, viewerClass, viewerArgs, viewerKwArgs, 
                bitmap, settings):
    numberOfViewersToAdd = settings.getint('view', 
        viewerClass.__name__.lower() + 'count')
    for i in range(numberOfViewersToAdd):
        viewerInstance = viewerClass(viewerContainer, *viewerArgs, **viewerKwArgs)
        viewerContainer.addViewer(viewerInstance, viewerInstance.title(), bitmap)

