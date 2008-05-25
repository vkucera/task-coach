
from _pysyncml import SyncSource, SyncItem, SYNC_TWO_WAY

import traceback

from taskcoachlib.syncml import vcal

class TaskSource(SyncSource):
    def __init__(self, taskList, *args, **kwargs):
        super(TaskSource, self).__init__(*args, **kwargs)

        self.preferredSyncMode = SYNC_TWO_WAY

        self.taskList = taskList
        self.allTasks = [task for task in taskList]
        self.newTasks = [task for task in taskList if task.isNew()]
        self.changedTasks = [task for task in taskList if task.isModified()]

    def __getTask(self, key):
        for task in self.taskList:
            if task.id() == key:
                return task
        raise KeyError, 'No such task: %s' % key

    def getFirstItemKey(self):
        print 'FIK'
        return None

    def getNextItemKey(self):
        print 'NIK'
        return None

    def __getitem(self, ls):
        try:
            obj = ls.pop(0)
        except IndexError:
            return None

        item = SyncItem(obj.id())
        item.data = vcal.VCalFromTask(obj)
        item.dataType = 'text/x-vcalendar'

        return item

    def getFirstItem(self):
        print 'FI'
        self.allTasksCopy = self.allTasks[:]
        return self.__getitem(self.allTasksCopy)

    def getNextItem(self):
        print 'NI'
        return self.__getitem(self.allTasksCopy)

    def getFirstNewItem(self):
        print 'FNI'
        self.newTasksCopy = self.newTasks[:]
        return self.__getitem(self.newTasksCopy)

    def getNextNewItem(self):
        print 'NNI'
        return self.__getitem(self.newTasksCopy)

    def getFirstUpdatedItem(self):
        print 'FUI'
        self.changedTasksCopy = self.changedTasks[:]
        return self.__getitem(self.changedTasksCopy)

    def getNextUpdatedItem(self):
        print 'NUI'
        return self.__getitem(self.changedTasksCopy)

    def getFirstDeletedItem(self):
        print 'FDI' # TODO

    def getNextDeletedItem(self):
        print 'NDI' # TODO

    def addItem(self, item):
        print 'ADD', item.data

        parser = vcal.VCalendarParser()
        parser.parse(map(lambda x: x.rstrip('\r'), item.data.split('\n')))
        task = parser.tasks[0]

        self.taskList.append(task)
        item.key = task.id() # For ID mapping

        return 201

    def updateItem(self, item):
        print 'UPDATE', item.data

        parser = vcal.VCalendarParser()
        parser.parse(map(lambda x: x.rstrip('\r'), item.data.split('\n')))
        task = parser.tasks[0]

        try:
            local = self.__getTask(item.key)
        except KeyError:
            return 404

        local.setStartDate(task.startDate())
        local.setDueDate(task.dueDate())
        local.setDescription(task.description())
        local.setSubject(task.subject())
        local.setPriority(task.priority())

        return 200 # FIXME

    def deleteItem(self, item):
        try:
            task = self.__getTask(item.key)
        except KeyError:
            return 404

        self.taskList.remove(task)

        return 200 # FIXME

    def setItemStatus(self, key, status):
        task = self.__getTask(key)

        if status in [200, 201, 418]:
            # 200: Generic OK
            # 201: Added.
            # 418: Already exists.

            task.cleanDirty()
            return 200

        print 'UNHANDLED ITEM STATUS %s %d' % (key, status)

        return 501 # TODO
