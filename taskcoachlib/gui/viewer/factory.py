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


class addViewers(object):
    ''' addViewers is a class masquerading as a method. It's a class because
        that makes it easier to split the work over different methods that
        use the same instance variables. '''  
    
    def __init__(self, viewerContainer, taskFile, settings):
        self.viewerContainer = viewerContainer
        self.taskFile = taskFile
        self.settings = settings
        self.addAllViewers()
        
    def addAllViewers(self):
        self.addTaskViewers()
        if self.settings.getboolean('feature', 'effort'):
            self.addEffortViewers()
        self.addCategoryViewers()
        if self.settings.getboolean('feature', 'notes'):
            self.addNoteViewers()

    def addTaskViewers(self):
        self._addViewers(task.TaskViewer, 
                         (self.taskFile.tasks(), self.settings), 
                         dict(categories=self.taskFile.categories(), 
                              efforts=self.taskFile.efforts()))
           
    def addEffortViewers(self):
        self._addViewers(effort.EffortViewer, 
                         (self.taskFile.tasks(), self.settings), 
                         {})

    def addCategoryViewers(self):
        self._addViewers(category.CategoryViewer, 
                         (self.taskFile.categories(), self.settings), 
                         dict(tasks=self.taskFile.tasks(), 
                              notes=self.taskFile.notes()))
        
    def addNoteViewers(self):
        self._addViewers(note.NoteViewer, 
                         (self.taskFile.notes(), self.settings), 
                         dict(categories=self.taskFile.categories()))

    def _addViewers(self, viewerClass, viewerArgs, viewerKwArgs):
        numberOfViewersToAdd = self.numberOfViewersToAdd(viewerClass)
        for i in range(numberOfViewersToAdd):
            viewerInstance = viewerClass(self.viewerContainer.containerWidget, 
                                         *viewerArgs, **viewerKwArgs)
            self.viewerContainer.addViewer(viewerInstance)
    
    def numberOfViewersToAdd(self, viewerClass):
        return self.settings.getint('view', viewerClass.__name__.lower() + 'count')


class addOneViewer(addViewers):
    def __init__(self, viewerContainer, taskFile, settings, viewerClass):
        self.viewerClass = viewerClass
        super(addOneViewer, self).__init__(viewerContainer, taskFile, settings)
        
    def numberOfViewersToAdd(self, viewerClass):
        if viewerClass == self.viewerClass:
            return 1
        else:
            return 0