'''
Task Coach - Your friendly task manager
Copyright (C) 2013 Task Coach developers <developers@taskcoach.org>

Task Coach is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Task Coach is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


import os
from taskcoachlib import patterns
from taskcoachlib.domain import base, task, category, note, effort, attachment
from taskcoachlib.thirdparty.guid import generate
from taskcoachlib.thirdparty.pubsub import pub
from taskcoachlib.persistence.backends import FileBackend
from taskcoachlib.persistence.xml import reader


class TaskStore(patterns.Observer):
    """
    This class is a container for domain objects in memory.
    """

    def __init__(self):
        super(TaskStore, self).__init__()

        self.__backends = list()
        self.__tasks = task.TaskList()
        self.__categories = category.CategoryList()
        self.__notes = note.NoteContainer()
        self.__efforts = effort.EffortList(self.tasks())

        self.__lastFilename = ''
        pub.subscribe(self.onMonitorDirty, 'monitor.dirty')

    def onMonitorDirty(self, monitor):
        for backend in self.__backends:
            if backend.monitor() == monitor:
                pub.sendMessage('taskstore.dirty', taskStore=self)
                break

    def addBackend(self, backend):
        self.__backends.append(backend)

    def tasks(self):
        return self.__tasks

    def categories(self):
        return self.__categories

    def notes(self):
        return self.__notes

    def efforts(self):
        return self.__efforts

    def dirty(self):
        return any([backend.dirty() for backend in self.__backends])

    def clear(self):
        pub.sendMessage('taskstore.aboutToClear', taskStore=self)
        try:
            event = patterns.Event()
            for collection in [self.tasks(), self.notes(), self.categories()]:
                collection.clear(event=event)
            event.send()
            for backend in self.__backends:
                backend.stop(self)
                backend.clear(self)
            self.__backends = list()
        finally:
            pub.sendMessage('taskstore.justCleared', taskStore=self)

    def stop(self):
        for backend in self.__backends:
            backend.stop(self)

    def isEmpty(self):
        return 0 == len(self.tasks()) == len(self.notes()) == len(self.categories())

    def fileBackend(self):
        for backend in self.__backends:
            if isinstance(backend, FileBackend):
                return backend
        return None

    # Methods making this almost compatible with the old TaskFile interface

    def filename(self):
        for backend in self.__backends:
            if isinstance(backend, FileBackend):
                return backend.filename()
        return ''

    def setFilename(self, filename):
        for backend in self.__backends:
            if isinstance(backend, FileBackend):
                break
        else:
            backend = FileBackend(self)
            self.__backends.append(backend)
        backend.setFilename(filename)
        self.__lastFilename = filename
        pub.sendMessage('taskstore.filenameChanged', filename=filename)

    def lastFilename(self):
        return self.__lastFilename

    def close(self):
        self.clear()

    def exists(self):
        for backend in self.__backends:
            if isinstance(backend, FileBackend):
                return backend.exists()
        return False

    def load(self, filename=None):
        if filename is None:
            filename = self.filename()
        pub.sendMessage('taskstore.aboutToRead', taskStore=self)
        try:
            self.clear()
            backend = FileBackend(self)
            self.__backends.append(backend)
            backend.setFilename(filename)
            if self.exists():
                backend.monitor().reset()
                backend.sync(self)
                backend.monitor().resetAllChanges()
            self.__lastFilename = filename
        finally:
            pub.sendMessage('taskstore.justRead', taskStore=self)

    def save(self):
        pub.sendMessage('taskstore.aboutToSave', taskStore=self)
        try:
            for backend in self.__backends:
                if isinstance(backend, FileBackend):
                    backend.sync(self)
        finally:
            pub.sendMessage('taskstore.justSaved')

    def saveas(self, filename):
        if os.path.exists(filename):
            os.remove(filename)
        if os.path.exists(filename + '.delta'):
            os.remove(filename + '.delta')
        for backend in self.__backends:
            backend.stop(self)
            backend.clear(self)
        backend = FileBackend(self)
        backend.setFilename(filename)
        self.__backends = [backend]
        self.save()
        self.__lastFilename = filename

    # XXXTODO: merge file

    def needSave(self):
        hasFile = False
        for backend in self.__backends:
            if isinstance(backend, FileBackend):
                hasFile = True
                if backend.dirty():
                    return True
        if hasFile:
            return False
        return not self.isEmpty()

    def is_locked(self):
        # XXXTODO
        return False

    def __contains__(self, item):
        return item in self.tasks() or item in self.notes() or \
               item in self.categories() or item in self.efforts()

    def merge(self, filename):
        with file(filename, 'rU') as fd:
            tasks, categories, notes, allChanges, guid = reader.XMLReader(fd).read()
        tasks = task.TaskList(tasks)
        categories = category.CategoryList(categories)
        notes = note.NoteContainer(notes)

        categoryMap = dict()
        self.tasks().removeItems(self.objectsToOverwrite(self.tasks(), tasks))
        self.rememberCategoryLinks(categoryMap, self.tasks())
        self.tasks().extend(tasks.rootItems())
        self.notes().removeItems(self.objectsToOverwrite(self.notes(), notes))
        self.rememberCategoryLinks(categoryMap, self.notes())
        self.notes().extend(notes.rootItems())
        self.categories().removeItems(self.objectsToOverwrite(self.categories(),
                                                              categories))
        self.categories().extend(categories.rootItems())
        self.restoreCategoryLinks(categoryMap)

    def objectsToOverwrite(self, originalObjects, objectsToMerge):
        objectsToOverwrite = []
        for domainObject in objectsToMerge:
            try:
                objectsToOverwrite.append(originalObjects.getObjectById(domainObject.id()))
            except IndexError:
                pass
        return objectsToOverwrite
        
    def rememberCategoryLinks(self, categoryMap, categorizables):
        for categorizable in categorizables:
            for categoryToLinkLater in categorizable.categories():
                categoryMap.setdefault(categoryToLinkLater.id(), []).append(categorizable)
            
    def restoreCategoryLinks(self, categoryMap):
        categories = self.categories()
        for categoryId, categorizables in categoryMap.iteritems():
            try:
                categoryToLink = categories.getObjectById(categoryId)
            except IndexError:
                continue  # Subcategory was removed by the merge
            for categorizable in categorizables:
                categorizable.addCategory(categoryToLink)
                categoryToLink.addCategorizable(categorizable)
