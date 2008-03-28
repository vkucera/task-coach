'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>
Copyright (C) 2008 Jerome Laheurte <fraca7@free.fr>

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

import os, patterns, codecs, shutil, xml
from domain import date, task, category, note, effort


class TaskFile(patterns.Observable):
    def __init__(self, filename='', *args, **kwargs):
        self.__filename = self.__lastFilename = filename
        self.__needSave = self.__loading = False
        self.__tasks = task.TaskList()
        self.__categories = category.CategoryList()
        self.__notes = note.NoteContainer()
        self.__efforts = effort.EffortList(self.tasks())
        super(TaskFile, self).__init__(*args, **kwargs)
        # Register for tasks, categories, efforts and notes being changed so we 
        # can monitor when the task file needs saving (i.e. is 'dirty'):
        for eventType in (self.tasks().addItemEventType(), 
                          self.tasks().removeItemEventType(), 
                          self.categories().addItemEventType(),
                          self.categories().removeItemEventType(),
                          self.notes().addItemEventType(),
                          self.notes().removeItemEventType()):
            patterns.Publisher().registerObserver(self.onDomainObjectAddedOrRemoved, 
                                                  eventType)

        for eventType in (task.Task.subjectChangedEventType(), 
            task.Task.descriptionChangedEventType(), 'task.startDate', 
            'task.dueDate', 'task.completionDate', 'task.priority', 
            'task.budget', 'task.hourlyFee', 'task.fixedFee',
            'task.timeSpent', 'task.reminder',
            'task.setting.shouldMarkCompletedWhenAllChildrenCompleted',
            task.Task.addChildEventType(), task.Task.removeChildEventType(),
            'task.effort.add', 'task.effort.remove', 
            task.Task.categoryAddedEventType(), 
            task.Task.categoryRemovedEventType(), 
            'task.attachment.add', 'task.attachment.remove', 'task.attachment.changed'):
            patterns.Publisher().registerObserver(self.onTaskChanged, 
                                                  eventType=eventType)
        for eventType in ('effort.description', 'effort.start', 'effort.stop'):
            # We don't need to observe 'effort.task', because when an
            # effort record is assigned to a different task we already will 
            # get a notification through 'task.effort.add'                
            patterns.Publisher().registerObserver(self.onEffortChanged, 
                                                  eventType=eventType)
        for eventType in (note.Note.subjectChangedEventType(), 
                note.Note.descriptionChangedEventType(), 
                note.Note.addChildEventType(), 
                note.Note.removeChildEventType()):
            patterns.Publisher().registerObserver(self.onNoteChanged, 
                                                  eventType=eventType)
        for eventType in (category.Category.filterChangedEventType(), 
                category.Category.subjectChangedEventType(),
                category.Category.descriptionChangedEventType(),
                category.Category.colorChangedEventType()):
            patterns.Publisher().registerObserver(self.onCategoryChanged, 
                eventType=eventType)

    def __str__(self):
        return self.filename()

    def categories(self):
        return self.__categories
    
    def notes(self):
        return self.__notes
    
    def tasks(self):
        return self.__tasks
    
    def efforts(self):
        return self.__efforts
    
    def isEmpty(self):
        return 0 == len(self.categories()) == len(self.tasks()) == len(self.notes())
            
    def onDomainObjectAddedOrRemoved(self, event):
        self.markDirty()
        
    def onTaskChanged(self, event):
        if event.source() in self.tasks():
            self.markDirty()
            
    def onEffortChanged(self, event):
        if event.source().task() in self.tasks():
            self.markDirty()
            
    def onCategoryChanged(self, event):
        if event.source() in self.categories():
            self.markDirty()
            
    def onNoteChanged(self, event):
        if event.source() in self.notes():
            self.markDirty()

    def setFilename(self, filename):
        self.__lastFilename = self.__filename or filename
        self.__filename = filename
        self.notifyObservers(patterns.Event(self, 'taskfile.filenameChanged', 
                                            filename))

    def filename(self):
        return self.__filename
        
    def lastFilename(self):
        return self.__lastFilename
        
    def markDirty(self, force=False):
        if force or not self.__needSave:
            self.__needSave = True
            self.notifyObservers(patterns.Event(self, 'taskfile.dirty', True))
                
    def markClean(self):
        if self.__needSave:
            self.__needSave = False
            self.notifyObservers(patterns.Event(self, 'taskfile.dirty', False))
            
    def _clear(self):
        self.tasks().removeItems(list(self.tasks()))
        self.categories().removeItems(list(self.categories()))
        self.notes().removeItems(list(self.notes()))
        
    def close(self):
        self.setFilename('')
        self._clear()
        self.__needSave = False

    def _read(self, fd):
        return xml.XMLReader(fd).read()
        
    def exists(self):
        return os.path.isfile(self.__filename)
        
    def _openForRead(self):
        return file(self.__filename, 'rU')

    def _openForWrite(self):
        return codecs.open(self.__filename, 'w', 'utf-8')
    
    def load(self):
        self.__loading = True
        try:
            if self.exists():
                fd = self._openForRead()
                tasks, categories, notes = self._read(fd)
                fd.close()
            else: 
                tasks = []
                categories = []
                notes = []
            self._clear()
            self.tasks().extend(tasks)
            self.categories().extend(categories)
            self.notes().extend(notes)
        finally:
            self.__loading = False
            self.__needSave = False
        
    def save(self):
        self.notifyObservers(patterns.Event(self, 'taskfile.aboutToSave'))
        fd = self._openForWrite()
        xml.XMLWriter(fd).write(self.tasks(), self.categories(), self.notes())
        fd.close()
        self.__needSave = False
        
    def saveas(self, filename):
        self.setFilename(filename)
        self.save()

    def merge(self, filename):
        mergeFile = self.__class__(filename)
        mergeFile.load()
        self.__loading = True
        self.tasks().extend(mergeFile.tasks().rootItems())
        self.categories().extend(mergeFile.categories().rootItems())
        self.__loading = False
        self.markDirty(force=True)

    def needSave(self):
        return not self.__loading and self.__needSave
 

class AutoSaver(patterns.Observer):
    def __init__(self, settings, *args, **kwargs):
        super(AutoSaver, self).__init__(*args, **kwargs)
        self.__settings = settings
        self.registerObserver(self.onTaskFileDirty, eventType='taskfile.dirty')
        self.registerObserver(self.onTaskFileAboutToSave,
                              eventType='taskfile.aboutToSave')
            
    def onTaskFileDirty(self, event):
        taskFile = event.source()
        if self._needSave(taskFile):
            taskFile.save()
        
    def onTaskFileAboutToSave(self, event):
        taskFile = event.source()
        if self._needBackup(taskFile):
            self._createBackup(taskFile)
    
    def _needSave(self, taskFile):
        return taskFile.filename() and taskFile.needSave() and \
            self._isOn('autosave')
    
    def _needBackup(self, taskFile):        
        return self._isOn('backup') and taskFile.exists()
    
    def _createBackup(self, taskFile):
        shutil.copyfile(taskFile.filename(), self._backupFilename(taskFile))
        
    def _backupFilename(self, taskFile, now=date.DateTime.now):
        now = now().strftime('%Y%m%d-%H%M%S')
        root, ext = os.path.splitext(taskFile.filename())
        if ext == '.bak':
            root, ext = os.path.splitext(root)
        return root + '.' + now + ext + '.bak'
        
    def _isOn(self, booleanSetting):
        return self.__settings.getboolean('file', booleanSetting)
