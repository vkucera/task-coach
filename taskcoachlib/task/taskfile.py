import os, writer, reader, tasklist, patterns, codecs

class TaskFile(tasklist.TaskList):
    def __init__(self, filename='', *args, **kwargs):
        self.__needSave = False
        super(TaskFile, self).__init__(*args, **kwargs)
        self.setFilename(filename)
        
    def __str__(self):
        return self.filename()

    def __nonzero__(self):
        return self.filename() != ''

    def setFilename(self, filename):
        self.__filename = filename
        notification = patterns.observer.Notification(self, filename=filename)
        super(TaskFile, self).notifyObservers(notification)

    def filename(self):
        return self.__filename
        
    def notifyObservers(self, notification):
        self.__needSave = True
        super(TaskFile, self).notifyObservers(notification)
        
    def _clear(self):
        self.removeItems(list(self))
        
    def close(self):
        self.setFilename('')
        self._clear()
        self.__needSave = False

    def load(self):
        if os.path.isfile(self.__filename):
            fd = file(self.__filename, 'rU')
            line = fd.readline()
            if line.startswith('<?xml'):
                fd.close()
                fd = file(self.__filename, 'r')
                ReaderClass = reader.XMLReader
            else:
                fd.seek(0)
                ReaderClass = reader.TaskReader
            tasks = ReaderClass(fd).read()
            fd.close()
        else: 
            tasks = []
        self._clear()
        self.extend(tasks)
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
        mergeFile = TaskFile(filename)
        mergeFile.load()
        self.extend(mergeFile.rootTasks())

    def needSave(self):
        return self.__needSave
        
