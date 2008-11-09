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

import effort, task, category, note

def viewerTypes():
    return 'taskviewer', 'noteviewer', 'categoryviewer', 'effortviewer'
            
def addEffortViewers(viewerContainer, taskList, settings):
    _addViewers(viewerContainer, effort.EffortViewer, (taskList, 
                settings), {}, 'start', settings)

def addTaskViewers(viewerContainer, taskList, settings, categories, efforts):
    _addViewers(viewerContainer, task.TaskViewer, (taskList,
                settings), dict(categories=categories, efforts=efforts), 
                'task', settings)

def addCategoryViewers(viewerContainer, categoryContainer, settings, tasks, 
                       notes):
    _addViewers(viewerContainer, category.CategoryViewer, (categoryContainer, 
                settings), dict(tasks=tasks, notes=notes), 'category', settings)
    
def addNoteViewers(viewerContainer, noteContainer, settings, categories):
    _addViewers(viewerContainer, note.NoteViewer, (noteContainer, 
                settings), dict(categories=categories), 'note', settings)

def _addViewers(viewerContainer, viewerClass, viewerArgs, viewerKwArgs, 
                bitmap, settings):
    numberOfViewersToAdd = settings.getint('view', 
        viewerClass.__name__.lower() + 'count')
    for i in range(numberOfViewersToAdd):
        viewerInstance = viewerClass(viewerContainer.containerWidget, 
                                     *viewerArgs, **viewerKwArgs)
        viewerContainer.addViewer(viewerInstance, viewerInstance.title(), 
                                  bitmap)

