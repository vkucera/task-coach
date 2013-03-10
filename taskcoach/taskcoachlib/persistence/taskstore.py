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

from __future__ import absolute_import # Or we can't import ElementTree :(

import os
from taskcoachlib import patterns, render
from taskcoachlib.domain import base, task, category, note, effort, attachment
from taskcoachlib.thirdparty.guid import generate
from taskcoachlib.thirdparty.pubsub import pub
from taskcoachlib.persistence.backends import FileBackend
from taskcoachlib.persistence.xml import reader, writer
from taskcoachlib.i18n import _
from xml.etree import ElementTree as ET
import datetime


class TaskStore(patterns.Observer):
    """
    This class is a container for domain objects in memory.
    """

    def __init__(self, settings):
        super(TaskStore, self).__init__()

        self.__settings = settings
        self.__backends = list()
        self.__tasks = task.TaskList()
        self.__categories = category.CategoryList()
        self.__notes = note.NoteContainer()
        self.__efforts = effort.EffortList(self.tasks())
        self.__locked = list()
        self.__guid = generate()
        self.__name = _('Session created on %s') % render.dateTime(datetime.datetime.now())
        self.__master = FileBackend(self)
        self.__dirty = False
        self.__lastFilename = ''

        pub.subscribe(self.onMonitorDirty, 'monitor.dirty')

    def needSave(self): # For autosave
        return self.__master.dirty() or self.__dirty

    def exists(self, fileExists=os.path.exists):
        return fileExists(os.path.join(self.__settings.pathToDataDir(), self.__guid + '.store'))

    def guid(self):
        return self.__guid

    def name(self):
        return self.__name

    def setName(self, name):
        self.__name = name
        self__dirty = True
        pub.sendMessage('taskstore.filenameChanged', filename=self.name())
        pub.sendMessage('taskstore.dirty', taskStore=self)

    def backends(self):
        return self.__backends[:]

    def saveSession(self):
        if self.isEmpty() and not self.exists():
            return
        pub.sendMessage('taskstore.aboutToSave', taskStore=self)
        try:
            root = ET.Element('store')
            ET.SubElement(root, 'name').text = self.__name
            for backend in self.__backends:
                node = ET.SubElement(root, 'backend')
                if isinstance(backend, FileBackend):
                    node.attrib['type'] = u'file'
                else:
                    raise RuntimeError('Unknown backend: %s' % backend)
                backend.toElement(node)
            with file(os.path.join(self.__settings.pathToDataDir(), self.__guid + '.store'), 'wb') as fd:
                ET.ElementTree(root).write(fd, encoding='UTF-8')

            with file(os.path.join(self.__settings.pathToDataDir(), self.__guid + '.storedata'), 'wb') as fd:
                writer.XMLWriter(fd).write(self.tasks(), self.categories(), self.notes(), self.__guid)

            self.__master.monitor().resetAllChanges()
            self.__dirty = False
            pub.sendMessage('taskstore.dirty', taskStore=self)
        finally:
            pub.sendMessage('taskstore.justSaved', taskStore=self)

    def loadSession(self, guid):
        pub.sendMessage('taskstore.aboutToRead', taskStore=self)
        try:
            self.clear()
            self.__guid = guid
            if os.path.exists(os.path.join(self.__settings.pathToDataDir(), guid + '.store')):
                with file(os.path.join(self.__settings.pathToDataDir(), guid + '.store'), 'rb') as fd:
                    root = ET.parse(fd)
                    self.__name = root.find('name').text
                    for node in root.findall('backend'):
                        if node.attrib['type'] == u'file':
                            backend = FileBackend(self)
                        else:
                            raise RuntimeError('Unknown backend type: "%s"' % node.attrib['type'])
                        backend.fromElement(node)
                with file(os.path.join(self.__settings.pathToDataDir(), guid + '.storedata'), 'rU') as fd:
                    tasks, categories, notes, allChanges, guid = reader.XMLReader(fd).read()
                    self.tasks().extend(tasks)
                    self.categories().extend(categories)
                    self.notes().extend(notes)
            else:
                self.__name = _('Session created on %s') % render.dateTime(datetime.datetime.now())

            self.__master.monitor().resetAllChanges()
            self.__dirty = False
            pub.sendMessage('taskstore.filenameChanged', filename=self.name())
        finally:
            pub.sendMessage('taskstore.justRead', taskStore=self)

    def isEmpty(self):
        return 0 == len(self.tasks()) == len(self.notes()) == len(self.categories())

    def onMonitorDirty(self, monitor):
        if monitor == self.__master.monitor():
            pub.sendMessage('taskstore.dirty', taskStore=self)

    def addBackend(self, backend):
        self.__backends.append(backend)
        self.__dirty = True
        pub.sendMessage('taskstore.dirty', taskStore=self)

    def tasks(self):
        return self.__tasks

    def categories(self):
        return self.__categories

    def notes(self):
        return self.__notes

    def efforts(self):
        return self.__efforts

    def dirty(self):
        return self.__master.dirty() or self.__dirty

    def lockAll(self):
        self.__locked = list()
        try:
            for backend in self.__backends:
                backend.lock()
                self.__locked.append(backend)
        except:
            for backend in self.__locked:
                try:
                    backend.unlock()
                except:
                    pass # XXXTODO: log
            self.__locked = list()
            raise

    def unlockAll(self):
        for backend in self.__locked:
            try:
                backend.unlock()
            except:
                pass # XXXTODO: idem
        self.__locked = list()

    def clear(self):
        pub.sendMessage('taskstore.aboutToClear', taskStore=self)
        try:
            self.__master.stop(self)
            event = patterns.Event()
            for collection in [self.tasks(), self.notes(), self.categories()]:
                collection.clear(event=event)
            event.send()
            self.lockAll()
            try:
                for backend in self.__backends:
                    backend.stop(self)
                    backend.clear(self)
                self.__backends = list()
            finally:
                self.unlockAll()
            self.__guid = generate()
            self.__master = FileBackend(self)
            self.__dirty = False
        finally:
            pub.sendMessage('taskstore.justCleared', taskStore=self)

    def stop(self):
        for backend in self.__backends:
            backend.stop(self)

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

    # Convenience methods

    def __createNewSessionWithFile(self, filename, doSave=True):
        if filename:
            self.__lastFilename = filename
        for backend in self.__backends:
            backend.stop(self)
        backend = FileBackend(self)
        backend.setFilename(filename)
        self.__backends = [backend]
        if filename:
            self.setName(os.path.split(filename)[-1])
        else:
            self.setName(_('Session created on %s') % render.dateTime(datetime.datetime.now()))
        if doSave:
            backend.lock()
            try:
                backend.put(self, backend.get(self))
            finally:
                backend.unlock()
        self.__master.monitor().resetAllChanges()
        self.saveSession()
        self.__dirty = False

    def save(self):
        self.lockAll()
        try:
            data = list()
            for backend in self.__backends:
                if backend.isAutomatic():
                    data.append(backend.get(self))
            for backend in self.__backends:
                if backend.isAutomatic():
                    backend.put(self, data.pop(0))
        finally:
            self.unlockAll()
        self.saveSession()

    def saveas(self, filename):
        if os.path.exists(filename):
            os.remove(filename)
        self.__createNewSessionWithFile(filename)

    def load(self, filename=None):
        if filename is None:
            for backend in self.__backends:
                if isinstance(backend, FileBackend):
                    filename = backend.filename()
                    break
        self.clear()
        self.__createNewSessionWithFile(filename, doSave=filename and os.path.exists(filename))

    def close(self):
        self.saveSession()
        self.clear()

    def filename(self):
        for backend in self.__backends:
            if isinstance(backend, FileBackend):
                return backend.filename()
        return ''

    def setFilename(self, filename):
        self.__lastFilename = filename or ''
        if filename:
            for backend in self.__backends:
                if isinstance(backend, FileBackend):
                    backend.setFilename(filename)
                    return
            self.__createNewSessionWithFile(filename, doSave=False)
        else:
            self.clear()

    def lastFilename(self):
        return self.__lastFilename
