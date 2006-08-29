import os, patterns, codecs, shutil, xml
import domain.date as date
import domain.task as task

class TaskFile(task.TaskList):
    def __init__(self, filename='', *args, **kwargs):
        self.__filename = self.__lastFilename = filename
        self.__needSave = self.__loading = False
        super(TaskFile, self).__init__(*args, **kwargs)
        # Register for tasks and efforts being changed so we can monitor
        # when the task file needs saving (i.e. is 'dirty'):
        for eventType in ('task.subject',
            'task.description', 'task.startDate', 'task.dueDate',
            'task.completionDate', 'task.priority', 
            'task.budget', 'task.hourlyFee', 'task.fixedFee',
            'task.timeSpent', 'task.reminder',
            'task.setting.shouldMarkCompletedWhenAllChildrenCompleted',
            'task.child.add', 'task.child.remove',
            'task.effort.add', 'task.effort.remove', 
            'task.category.add', 'task.category.remove', 
            'task.attachment.add', 'task.attachment.remove'):
            patterns.Publisher().registerObserver(self.onTaskChanged, 
                                                  eventType=eventType)
        for eventType in ('effort.description', 'effort.start', 'effort.stop'):
            # We don't need to observe 'effort.task', because when an
            # effort record is assigned to a different task we already will 
            # get a notification through 'task.effort.add'                
            patterns.Publisher().registerObserver(self.onEffortChanged, 
                                                  eventType=eventType)
        
    def __str__(self):
        return self.filename()

    def extend(self, tasks):
        if tasks:
            super(TaskFile, self).extend(tasks)
            self.markDirty()

    def removeItems(self, tasks):
        if tasks:
            super(TaskFile, self).removeItems(tasks)
            self.markDirty()
        
    def onTaskChanged(self, event):
        if event.source() in self:
            self.markDirty()
            
    def onEffortChanged(self, event):
        if event.source().task() in self:
            self.markDirty()

    def setFilename(self, filename):
        self.__lastFilename = self.__filename or filename
        self.__filename = filename
        patterns.Publisher().notifyObservers(patterns.Event(self, 
            'taskfile.filenameChanged', filename))

    def filename(self):
        return self.__filename
        
    def lastFilename(self):
        return self.__lastFilename
        
    def markDirty(self):
        if not self.__needSave:
            self.__needSave = True
            patterns.Publisher().notifyObservers(patterns.Event(self, 
                'taskfile.dirty', True))
                
    def markClean(self):
        if self.__needSave:
            self.__needSave = False
            patterns.Publisher().notifyObservers(patterns.Event(self, 
                'taskfile.dirty', False))
            
    def _clear(self):
        self.removeItems(list(self))
        
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
                tasks = self._read(fd)
                fd.close()
            else: 
                tasks = []
            self._clear()
            self.extend(tasks)
        finally:
            self.__loading = False
            self.__needSave = False
        
    def save(self):
        patterns.Publisher().notifyObservers(patterns.Event(self, 
            'taskfile.aboutToSave'))
        fd = self._openForWrite()
        xml.XMLWriter(fd).write(self)
        fd.close()
        self.__needSave = False
        
    def saveas(self, filename):
        self.setFilename(filename)
        self.save()

    def merge(self, filename):
        mergeFile = self.__class__(filename)
        mergeFile.load()
        self.extend(mergeFile.rootTasks())

    def needSave(self):
        return not self.__loading and self.__needSave
 

class AutoSaver(object):
    def __init__(self, settings):
        self.__settings = settings
        patterns.Publisher().registerObserver(self.onTaskFileDirty, 
            eventType='taskfile.dirty')
        patterns.Publisher().registerObserver(self.onTaskFileAboutToSave,
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
        return taskFile.filename() + '.%s.bak'%now
        
    def _isOn(self, booleanSetting):
        return self.__settings.getboolean('file', booleanSetting)
