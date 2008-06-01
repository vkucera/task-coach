
from taskcoachlib.syncml import vcal, basesource
from taskcoachlib.domain.task import Task
from taskcoachlib.domain.category import Category

class TaskSource(basesource.BaseSource):
    def __init__(self, taskList, categoryList, *args, **kwargs):
        super(TaskSource, self).__init__(taskList, *args, **kwargs)

        self.categoryList = categoryList

    def _getItem(self, ls):
        item, task = super(TaskSource, self)._getItem(ls)

        if item is not None:
            item.data = vcal.VCalFromTask(task)
            item.dataType = 'text/x-vcalendar'

        return item

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

    def addItem(self, item):
        task = super(TaskSource, self).addItem(item)

        for category in task.categories():
            category.addCategorizable(task)

        return 201

    def doUpdateItem(self, task, local):
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
