
from _pysyncml import SyncSource, SyncItem, SYNC_TWO_WAY

import traceback

from taskcoachlib.syncml import vcal
from taskcoachlib.domain.task import Task
from taskcoachlib.domain.category import Category

class TaskSource(SyncSource):
    def __init__(self, taskList, categoryList, *args, **kwargs):
        super(TaskSource, self).__init__(*args, **kwargs)

        self.preferredSyncMode = SYNC_TWO_WAY

        self.taskList = taskList
        self.categoryList = categoryList

        self.allTasks = [task for task in taskList]
        self.newTasks = [task for task in taskList if task.isNew()]
        self.changedTasks = [task for task in taskList if task.isModified()]

    def __getTask(self, key):
        for task in self.taskList:
            if task.id() == key:
                return task
        raise KeyError, 'No such task: %s' % key

    def getFirstItemKey(self):
        return None

    def getNextItemKey(self):
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
        self.allTasksCopy = self.allTasks[:]
        return self.__getitem(self.allTasksCopy)

    def getNextItem(self):
        return self.__getitem(self.allTasksCopy)

    def getFirstNewItem(self):
        self.newTasksCopy = self.newTasks[:]
        return self.__getitem(self.newTasksCopy)

    def getNextNewItem(self):
        return self.__getitem(self.newTasksCopy)

    def getFirstUpdatedItem(self):
        self.changedTasksCopy = self.changedTasks[:]
        return self.__getitem(self.changedTasksCopy)

    def getNextUpdatedItem(self):
        return self.__getitem(self.changedTasksCopy)

    def getFirstDeletedItem(self):
        print 'FDI' # TODO

    def getNextDeletedItem(self):
        print 'NDI' # TODO

    def __parseTask(self, item):
        parser = vcal.VCalendarParser()
        parser.parse(map(lambda x: x.rstrip('\r'), item.data.split('\n')))

        categories = parser.tasks[0].pop('categories')

        task = Task(**parser.tasks[0])

        for category in categories:
            categoryObject = self.categoryList.findCategoryByName(category)
            if categoryObject is None:
                categoryObject = Category(category)
                self.categoryList.extend([categoryObject])
            task.addCategory(categoryObject)

        return task

    def addItem(self, item):
        task = self.__parseTask(item)
        self.taskList.append(task)
        item.key = task.id() # For ID mapping

        for category in task.categories():
            category.addCategorizable(task)

        return 201

    def updateItem(self, item):
        task = self.__parseTask(item)

        try:
            local = self.__getTask(item.key)
        except KeyError:
            return 404

        local.setStartDate(task.startDate())
        local.setDueDate(task.dueDate())
        local.setDescription(task.description())
        local.setSubject(task.subject())
        local.setPriority(task.priority())

        for category in local.categories():
            category.removeCategorizable(local)

        local.setCategories(task.categories())

        for category in local.categories():
            category.addCategorizable(local)

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
