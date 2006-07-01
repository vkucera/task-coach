import os, patterns, codecs, shutil, xml
import domain.date as date
import domain.task as task

class TaskFile(task.TaskList):
    def __init__(self, filename='', *args, **kwargs):
        self.__needSave = False
        self.__loading = False
        self.__lastFilename = ''
        self.__filename = filename
        super(TaskFile, self).__init__(*args, **kwargs)
        # Register for tasks being added and removed to we can monitor
        # when the task file needs saving (i.e. is 'dirty'):
        self.registerObserver(self.onAddItem, 'list.add')
        self.registerObserver(self.onRemoveItem, 'list.remove')
        
    def __str__(self):
        return self.filename()

    def onAddItem(self, event):
        self.markDirty()
        for task in event.values():
            task.registerObserver(self.markDirty, 'task.subject',
                'task.description', 'task.startDate', 'task.dueDate',
                'task.completionDate', 'task.priority', 
                'task.budget', 'task.hourlyFee', 'task.fixedFee',
                'task.reminder',
                'task.setting.shouldMarkCompletedWhenAllChildrenCompleted',
                'task.child.add', 'task.child.remove',
                'task.effort.add', 'task.effort.remove', 
                'task.category.add', 'task.category.remove', 
                'task.attachment.add', 'task.attachment.remove')
            task.registerObserver(self.onAddEffort, 'task.effort.add')

    def onRemoveItem(self, event):
        self.markDirty()
        for task in event.values():
            task.removeObserver(self.markDirty)

    def onAddEffort(self, event):
        for effort in event.values():
            effort.registerObserver(self.markDirty, 'effort.description', 
                'effort.start', 'effort.stop')
            # We don't need to observe 'effort.task', because when an
            # effort record is assigned to a different task we already will 
            # get a notification through 'task.effort.add'

    def onRemoveEffort(self, event):
        for effort in event.values():
            effort.removeObserver(self.markDirty)

    def setFilename(self, filename):
        if filename != '':
            self.__lastFilename = filename
        self.__filename = filename
        self.notifyObservers(patterns.Event(self, 'taskfile.filenameChanged', 
            filename))

    def filename(self):
        return self.__filename
        
    def lastFilename(self):
        return self.__lastFilename
        
    def markDirty(self, event=None):
        if not self.__needSave:
            self.__needSave = True
            self.notifyObservers(patterns.Event(self, 'taskfile.dirty', True))

    def markClean(self):
        if self.__needSave:
            self.__needSave = False
            self.notifyObservers(patterns.Event(self, 'taskfile.dirty', False))
        
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
        self.notifyObservers(patterns.Event(self, 'taskfile.aboutToSave'))
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
    def __init__(self, settings, taskFile):
        self.__settings = settings
        self.__taskFile = taskFile
        self.__taskFile.registerObserver(self.onTaskFileDirty,
            'taskfile.dirty')
        self.__taskFile.registerObserver(self.onTaskFileAboutToSave, 
            'taskfile.aboutToSave')
        
    def onTaskFileDirty(self, event):
        if self._needSave():
            self.__taskFile.save()
        
    def onTaskFileAboutToSave(self, event):
        if self._needBackup():
            self._createBackup()
    
    def _needSave(self):
        return self.__taskFile.filename() and self.__taskFile.needSave() and \
            self._isOn('autosave')
    
    def _needBackup(self):        
        return self._isOn('backup') and self.__taskFile.exists()
    
    def _createBackup(self):
        shutil.copyfile(self.__taskFile.filename(), self._backupFilename())
        
    def _backupFilename(self, now=date.DateTime.now):
        now = now().strftime('%Y%m%d-%H%M%S')
        return self.__taskFile.filename() + '.%s.bak'%now
        
    def _isOn(self, booleanSetting):
        return self.__settings.getboolean('file', booleanSetting)
