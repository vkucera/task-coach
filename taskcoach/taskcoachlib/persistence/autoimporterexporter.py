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

import codecs, os
from taskcoachlib import patterns
import todotxt


class AutoImporterExporter(patterns.Observer):
    ''' AutoImporterExporter observes task files. If a task file is saved, 
        either by the user or automatically (when autosave is on) and auto 
        import and/or export is on, AutoImporterExporter imports and/or exports 
        the task file. '''
        
    def __init__(self, settings):
        super(AutoImporterExporter, self).__init__()
        self.__settings = settings
        self.registerObserver(self.onTaskFileAboutToBeSaved, 
                              eventType='taskfile.aboutToSave')
        self.registerObserver(self.onTaskFileJustRead,
                              eventType='taskfile.justRead')
        
    def onTaskFileJustRead(self, event):
        ''' After a task file has been read and if auto import is on, 
            import it. '''
        self.importFiles(event)
            
    def onTaskFileAboutToBeSaved(self, event):
        ''' When a task file is about to be saved and auto import and/or 
            export is on, import and/or export it. '''
        self.importFiles(event)
        self.exportFiles(event)
        
    def importFiles(self, event):
        importFormats = self.__settings.getlist('file', 'autoimport')
        for importFormat in importFormats:
            if importFormat == 'Todo.txt':
                self.importTodoTxt(event)
                
    def exportFiles(self, event):
        exportFormats = self.__settings.getlist('file', 'autoexport')
        for exportFormat in exportFormats:
            if exportFormat == 'Todo.txt':
                self.exportTodoTxt(event)
    
    @classmethod            
    def importTodoTxt(cls, event):
        for taskFile in event.sources():
            filename = cls.todoTxtFilename(taskFile)
            if os.path.exists(filename):
                todotxt.TodoTxtReader(taskFile.tasks(), taskFile.categories()).read(filename)

    @classmethod
    def exportTodoTxt(cls, event):
        for taskFile in event.sources():
            filename = cls.todoTxtFilename(taskFile)
            with codecs.open(filename, 'w', 'utf-8') as todoFile:
                todotxt.TodoTxtWriter(todoFile, filename).writeTasks(taskFile.tasks())
    
    @staticmethod   
    def todoTxtFilename(taskFile):
        return taskFile.filename()[:-len('tsk')] + 'txt'
