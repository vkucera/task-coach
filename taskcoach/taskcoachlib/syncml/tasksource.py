
from taskcoachlib.syncml import vcal, basesource
from taskcoachlib.domain.task import Task
from taskcoachlib.domain.category import Category

from taskcoachlib.i18n import _

import wx

class TaskSource(basesource.BaseSource):
    CONFLICT_STARTDATE        = 0x01
    CONFLICT_DUEDATE          = 0x02
    CONFLICT_DESCRIPTION      = 0x04
    CONFLICT_SUBJECT          = 0x08
    CONFLICT_PRIORITY         = 0x10
    CONFLICT_CATEGORIES       = 0x20

    def __init__(self, taskList, categoryList, *args, **kwargs):
        super(TaskSource, self).__init__(taskList, *args, **kwargs)

        self.categoryList = categoryList

    def updateItemProperties(self, item, task):
        item.data = vcal.VCalFromTask(task)
        item.dataType = 'text/x-vcalendar'

    def compareItemProperties(self, local, remote):
        result = 0

        if local.startDate() != remote.startDate():
            result |= self.CONFLICT_STARTDATE
        if local.dueDate() != remote.dueDate():
            result |= self.CONFLICT_DUEDATE
        if local.description() != remote.description:
            result |= self.CONFLICT_DESCRIPTION
        if local.subject() != remote.subject():
            result |= self.CONFLICT_SUBJECT
        if local.priority() != remote.priority():
            result |= self.CONFLICT_PRIORITY

        localCategories = map(unicode, local.categories())
        remoteCategories = map(unicode, remote.categories())

        localCategories.sort()
        remoteCategories.sort()

        if localCategories != remoteCategories:
            result |= self.CONFLICT_CATEGORIES

        return result

    def _parseObject(self, item):
        parser = vcal.VCalendarParser()
        parser.parse(map(lambda x: x.rstrip('\r'), item.data.split('\n')))

        categories = parser.tasks[0].pop('categories', [])

        task = Task(**parser.tasks[0])

        for category in categories:
            categoryObject = self.categoryList.findCategoryByName(category)
            if categoryObject is None:
                categoryObject = Category(category)
                self.categoryList.extend([categoryObject])
            task.addCategory(categoryObject)

        return task

    def doAddItem(self, task):
        for category in task.categories():
            category.addCategorizable(task)

        return 201

    def doUpdateItem(self, task, local):
        print 'UPDATE', local.id()

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

    def doResolveConflict(self, task, local, result):
        if wx.MessageBox(_('Task "%s" has been both remotely and locally modified.\n') % task.subject() + \
                         _('Should I keep the local version ?'),
                         _('Synchronization conflict'), wx.YES_NO) == wx.YES:
            return local
        else:
            return task

    def objectRemovedOnServer(self, task):
        return wx.MessageBox(_('Task "%s" has been deleted on server,\n') % task.subject() + \
                             _('but locally modified. Should I keep the local version ?'),
                             _('Synchronization conflict'), wx.YES_NO) == wx.YES

    def objectRemovedOnClient(self, task):
        return wx.MessageBox(_('Task "%s" has been locally deleted,\n') % task.subject() + \
                             _('but modified on server. Should I keep the remote version ?'),
                             _('Synchronization conflict'), wx.YES_NO) == wx.YES
