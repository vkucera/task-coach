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
        
    def __str__(self):
        return self.filename()

    def setFilename(self, filename):
        if filename != '':
            self.__lastFilename = filename
        self.__filename = filename
        notification = patterns.Notification(self, filename=filename)
        super(TaskFile, self).notifyObservers(notification, 'FilenameChanged')

    def filename(self):
        return self.__filename
        
    def lastFilename(self):
        return self.__lastFilename
        
    def notifyObservers(self, notification, *args, **kwargs):
        if notification.changeNeedsSave:
            self.__needSave = True
        super(TaskFile, self).notifyObservers(notification, *args, **kwargs)
        
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
        self.notifyObservers(patterns.Notification(self), 'TaskFileAboutToSave')
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
        self.__taskFile.registerObserver(self.onTaskFileChanged)
        self.__taskFile.registerObserver(self.onTaskFileAboutToSave, 
            'TaskFileAboutToSave')
        
    def onTaskFileChanged(self, notification, *args, **kwargs):
        if self._needSave():
            self.__taskFile.save()
        
    def onTaskFileAboutToSave(self, notification, *args, **kwargs):
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
