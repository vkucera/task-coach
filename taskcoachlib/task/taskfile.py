import os, writer, reader, tasklist, patterns, codecs, shutil

class TaskFile(tasklist.TaskList):
    def __init__(self, filename='', *args, **kwargs):
        self.__needSave = False
        self.__loading = False
        self.__lastFilename = ''
        super(TaskFile, self).__init__(*args, **kwargs)
        self.setFilename(filename)
        
    def __str__(self):
        return self.filename()

    def setFilename(self, filename):
        if filename != '':
            self.__lastFilename = filename
        self.__filename = filename
        notification = patterns.observer.Notification(self, filename=filename, changeNeedsSave=True)
        super(TaskFile, self).notifyObservers(notification)

    def filename(self):
        return self.__filename
        
    def lastFilename(self):
        return self.__lastFilename
        
    def notifyObservers(self, notification):
        if not self.__loading and notification.changeNeedsSave:
            self.__needSave = True
        super(TaskFile, self).notifyObservers(notification)
        
    def _clear(self):
        self.removeItems(list(self))
        
    def close(self):
        self.setFilename('')
        self._clear()
        self.__needSave = False

    def _read(self, fd):
        return reader.XMLReader(fd).read()
        
    def _exists(self):
        return os.path.isfile(self.__filename)
        
    def _open(self):
        return file(self.__filename, 'rU')
            
    def load(self):
        self.__loading = True
        try:
            if self._exists():
                fd = self._open()
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
        fd = codecs.open(self.__filename, 'w', 'utf-8')
        writer.XMLWriter(fd).write(self)
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
        return not self.isLoading() and self.__needSave
 
    def isLoading(self):
        return self.__loading


class AutoSaver(object):
    def __init__(self, settings, taskFile):
        self.__settings = settings
        self.__taskFile = taskFile
        self.__taskFile.registerObserver(self.onTaskFileChanged)
        
    def onTaskFileChanged(self, notification, *args, **kwargs):
        if self._needSave():
            self.__taskFile.save()
        elif self._needBackup():
            self._createBackup()
    
    def _needSave(self):
        return self.__taskFile.filename() and self.__taskFile.needSave() and \
            self._isOn('autosave')
            
    def _needBackup(self):
        return self.__taskFile.isLoading() and self._isOn('backup')

    def _createBackup(self):
        backup = self.__taskFile.filename() + '.bak'
        if os.path.isfile(backup):
            backup2 = backup + '.bak'
            shutil.copyfile(backup, backup2)
        shutil.copyfile(self.__taskFile.filename(), backup)
        
    def _isOn(self, booleanSetting):
        return self.__settings.getboolean('file', booleanSetting)