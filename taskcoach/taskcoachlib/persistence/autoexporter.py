'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2011 Task Coach developers <developers@taskcoach.org>

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

from taskcoachlib import patterns
import todotxt


class AutoExporter(patterns.Observer):
    ''' AutoExporter observes task files. If a task file is saved, either by the 
        user or automatically (when autosave is on) and auto export is on, 
        AutoExporter exports the task file. '''
        
    def __init__(self, settings):
        super(AutoExporter, self).__init__()
        self.__settings = settings
        self.registerObserver(self.onTaskFileAboutToBeSaved, 
                              eventType='taskfile.aboutToSave')
            
    def onTaskFileAboutToBeSaved(self, event):
        ''' When a task file is about to be saved and auto export is on, export it. '''
        exportFormats = self.__settings.getlist('file', 'autoexport')
        for exportFormat in exportFormats:
            if exportFormat == 'Todo.txt':
                self.exportTodoTxt(event)

    def exportTodoTxt(self, event):
        for taskFile in event.sources():
            filename = taskFile.filename()[:-len('tsk')] + 'txt'
            with file(filename, 'w') as todoFile:
                todotxt.TodoTxtWriter(todoFile, filename).writeTasks(taskFile.tasks())
