import os, writer, reader, tasklist

class TaskFile(tasklist.TaskList):
    def __init__(self, effortList, filename='', *args, **kwargs):
        self._effortList = effortList
        self.setFilename(filename)
        super(TaskFile, self).__init__(*args, **kwargs)
        notify = [self.notifyNeedSave]*3
        self.registerObserver(*notify)
        self._effortList.registerObserver(*notify)
        self._needSave = False

    def __str__(self):
        return self.filename()

    def __nonzero__(self):
        return self.filename() != ''

    def setFilename(self, filename):
        self._filename = filename

    def notifyNeedSave(self, *args):
        self._needSave = True

    def filename(self):
        return self._filename

    def close(self):
        self.setFilename('')
        del self[:]
        del self._effortList[:]
        self._needSave = False

    def load(self):
        if os.path.isfile(self._filename):
            fd = file(self._filename, 'rU')
            tasks, efforts = reader.TaskReader(fd).read()
            fd.close()
        else: 
            tasks, efforts = [], []
        del self[:]
        del self._effortList[:]
        self.extend(tasks)
        self._effortList.extend(efforts)
        self._needSave = False

    def save(self):
        fd = file(self._filename, 'w')
        writer.TaskWriter(fd).write(self, self._effortList)
        fd.close()
        self._needSave = False

    def saveas(self, filename):
        self.setFilename(filename)
        self.save()

    def merge(self, filename):
        mergeFile = TaskFile(self._effortList, filename)
        mergeFile.load()
        self.extend(mergeFile.rootTasks())
        self._needSave = True

    def needSave(self):
        return self._needSave

    def effortList(self):
        return self._effortList
        
    def exportToXML(self, filename):
        fd = file(filename, 'w')
        writer.XMLWriter(fd).write(self, self._effortList)
        fd.close()
