'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2009 Frank Niessink <frank@niessink.com>
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

import os, codecs, shutil, xml
from taskcoachlib import patterns
from taskcoachlib.domain import base, date, task, category, note, effort, attachment
from taskcoachlib.syncml.config import SyncMLConfigNode, createDefaultSyncConfig
from taskcoachlib.thirdparty.guid import generate


class TaskFile(patterns.Observable, patterns.Observer):
    def __init__(self, filename='', *args, **kwargs):
        self.__filename = self.__lastFilename = filename
        self.__needSave = self.__loading = False
        self.__tasks = task.TaskList()
        self.__categories = category.CategoryList()
        self.__notes = note.NoteContainer()
        self.__efforts = effort.EffortList(self.tasks())
        self.__guid = generate()
        self.__syncMLConfig = createDefaultSyncConfig(self.__guid)
        super(TaskFile, self).__init__(*args, **kwargs)
        # Register for tasks, categories, efforts and notes being changed so we 
        # can monitor when the task file needs saving (i.e. is 'dirty'):
        for eventType in (self.tasks().addItemEventType(), 
                          self.tasks().removeItemEventType()):
            self.registerObserver(self.onDomainObjectAddedOrRemoved,
                eventType, eventSource=self.tasks())
        for eventType in (self.categories().addItemEventType(),
                          self.categories().removeItemEventType()):
            self.registerObserver(self.onDomainObjectAddedOrRemoved,
                eventType, eventSource=self.categories())
        for eventType in (self.notes().addItemEventType(),
                          self.notes().removeItemEventType()):
            self.registerObserver(self.onDomainObjectAddedOrRemoved,
                eventType, eventSource=self.notes())
        for eventType in (base.Object.markDeletedEventType(),
                          base.Object.markNotDeletedEventType()):
            self.registerObserver(self.onDomainObjectAddedOrRemoved, eventType)

        for eventType in task.Task.modificationEventTypes():
            self.registerObserver(self.onTaskChanged, eventType)
        for eventType in effort.Effort.modificationEventTypes():
            self.registerObserver(self.onEffortChanged, eventType)
        for eventType in note.Note.modificationEventTypes():
            self.registerObserver(self.onNoteChanged, eventType)
        for eventType in category.Category.modificationEventTypes():
            self.registerObserver(self.onCategoryChanged, eventType)
        for eventType in attachment.FileAttachment.modificationEventTypes() + \
                         attachment.URIAttachment.modificationEventTypes() + \
                         attachment.MailAttachment.modificationEventTypes(): 
            self.registerObserver(self.onAttachmentChanged, eventType) 

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

    def syncMLConfig(self):
        return self.__syncMLConfig

    def guid(self):
        return self.__guid

    def setSyncMLConfig(self, config):
        self.__syncMLConfig = config
        self.markDirty()

    def isEmpty(self):
        return 0 == len(self.categories()) == len(self.tasks()) == len(self.notes())
            
    def onDomainObjectAddedOrRemoved(self, event):
        self.markDirty()
        
    def onTaskChanged(self, event):
        if event.source() in self.tasks() and not self.__loading:
            self.markDirty()
            event.source().markDirty()
            
    def onEffortChanged(self, event):
        if event.source().task() in self.tasks() and not self.__loading:
            self.markDirty()
            event.source().markDirty()
            
    def onCategoryChanged(self, event):
        if event.source() in self.categories() and not self.__loading:
            self.markDirty()
            for categorizable in event.source().categorizables():
                categorizable.markDirty()
            
    def onNoteChanged(self, event):
        if event.source() in self.notes() and not self.__loading:
            self.markDirty()
            event.source().markDirty()
            
    def onAttachmentChanged(self, event):
        if not self.__loading:
            # Attachments don't know their owner, so we can't check whether the
            # attachment is actually in the task file. Assume it is.
            self.markDirty()
            event.source().markDirty()

    def setFilename(self, filename):
        self.__lastFilename = filename or self.__filename
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
        self.__guid = generate()
        self.__syncMLConfig = createDefaultSyncConfig(self.__guid)
        
    def close(self):
        self.setFilename('')
        self.__guid = generate()
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
                tasks, categories, notes, syncMLConfig, guid = self._read(fd)
                fd.close()
            else: 
                tasks = []
                categories = []
                notes = []
                guid = generate()
                syncMLConfig = createDefaultSyncConfig(guid)
            self._clear()
            self.categories().extend(categories)
            self.tasks().extend(tasks)
            self.notes().extend(notes)
            self.__syncMLConfig = syncMLConfig
            self.__guid = guid
        finally:
            self.__loading = False
            self.__needSave = False
        
    def save(self):
        self.notifyObservers(patterns.Event(self, 'taskfile.aboutToSave'))
        fd = self._openForWrite()
        xml.XMLWriter(fd).write(self.tasks(), self.categories(), self.notes(),
                                self.syncMLConfig(), self.guid())
        fd.close()
        self.__needSave = False
        
    def saveas(self, filename):
        self.setFilename(filename)
        self.save()

    def merge(self, filename):
        mergeFile = self.__class__(filename)
        mergeFile.load()
        self.__loading = True
        self.tasks().removeItems(self.objectsToOverwrite(self.tasks(), mergeFile.tasks()))
        self.tasks().extend(mergeFile.tasks().rootItems())
        self.notes().removeItems(self.objectsToOverwrite(self.notes(), mergeFile.notes()))
        self.notes().extend(mergeFile.notes().rootItems())
        self.categories().removeItems(self.objectsToOverwrite(self.categories(),
                                                              mergeFile.categories()))
        self.categories().extend(mergeFile.categories().rootItems())
        self.__loading = False
        self.markDirty(force=True)
        
    def objectsToOverwrite(self, originalObjects, objectsToMerge):
        objectsToOverwrite = []
        for object in objectsToMerge:
            try:
                objectsToOverwrite.append(originalObjects.getObjectById(object.id()))
            except IndexError:
                pass
        return objectsToOverwrite
    
    def needSave(self):
        return not self.__loading and self.__needSave

    def beginSync(self):
        self.__loading = True

    def endSync(self):
        self.__loading = False
        self.__needSave = True


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
