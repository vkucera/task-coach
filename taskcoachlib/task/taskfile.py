import os, writer, reader, tasklist

class TaskFile(tasklist.TaskList):
    def __init__(self, filename='', *args, **kwargs):
        self.setFilename(filename)
        super(TaskFile, self).__init__(*args, **kwargs)
        self.registerObserver(self.onNotifyNeedSave)
        self._needSave = False

    def __str__(self):
        return self.filename()

    def __nonzero__(self):
        return self.filename() != ''

    def setFilename(self, filename):
        self._filename = filename

    def onNotifyNeedSave(self, *args, **kwargs):
        self._needSave = True

    def filename(self):
        return self._filename

    def close(self):
        self.setFilename('')
        del self[:]
        self._needSave = False

    def load(self):
        if os.path.isfile(self._filename):
            fd = file(self._filename, 'rU')
            tasks = reader.TaskReader(fd).read()
            fd.close()
        else: 
            tasks = []
        del self[:]
        self.extend(tasks)
        self._needSave = False

    def save(self):
        fd = file(self._filename, 'w')
        writer.TaskWriter(fd).write(self)
        fd.close()
        self._needSave = False

    def saveas(self, filename):
        self.setFilename(filename)
        self.save()

    def merge(self, filename):
        mergeFile = TaskFile(filename)
        mergeFile.load()
        self.extend(mergeFile.rootTasks())
        self._needSave = True

    def needSave(self):
        return self._needSave
        
    def exportToXML(self, filename):
        fd = file(filename, 'w')
        writer.XMLWriter(fd).write(self)
        fd.close()
