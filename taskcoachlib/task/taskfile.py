import os, writer, reader, tasklist, patterns, codecs

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
        notification = patterns.observer.Notification(self, filename=filename)
        super(TaskFile, self).notifyObservers(notification)

    def filename(self):
        return self.__filename
        
    def lastFilename(self):
        return self.__lastFilename
        
    def notifyObservers(self, notification):
        if not self.__loading:
            self.__needSave = True
        super(TaskFile, self).notifyObservers(notification)
        
    def _clear(self):
        self.removeItems(list(self))
        
    def close(self):
        self.setFilename('')
        self._clear()
        self.__needSave = False

    def _read(self, fd):
        line = fd.readline()
        if line.startswith('<?xml'):
            fd.close()
            fd = file(self.__filename, 'r')
            #fd = codecs.open(self.__filename, 'r', 'utf-8')
            ReaderClass = reader.XMLReader
        else:
            fd.seek(0)
            ReaderClass = reader.TaskReader
        return ReaderClass(fd).read()
        
    def _exists(self):
        return os.path.isfile(self.__filename)
        
    def _open(self):
        return file(self.__filename, 'rU')
            
    def load(self):
        self.__loading = True
        if self._exists():
            fd = self._open()
            tasks = self._read(fd)
            fd.close()
        else: 
            tasks = []
        self._clear()
        self.extend(tasks)
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
        return not self.__loading and self.__needSave
        

class AutoSaver:
    def __init__(self, settings, taskFile):
        self.__settings = settings
        self.__taskFile = taskFile
        self.__taskFile.registerObserver(self.onTaskFileChanged)
        
    def onTaskFileChanged(self, notification, *args, **kwargs):
        if self.__taskFile.filename() and self.__taskFile.needSave() and \
            self.__settings.getboolean('file', 'autosave'):
            self.__taskFile.save()
        
    