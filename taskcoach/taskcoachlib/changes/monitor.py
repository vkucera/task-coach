'''
Task Coach - Your friendly task manager
Copyright (C) 2011 Task Coach developers <developers@taskcoach.org>

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

from taskcoachlib.patterns import Publisher, Singleton, ObservableComposite
from taskcoachlib.domain.categorizable import CategorizableCompositeObject
from taskcoachlib.domain.note import NoteOwner
from taskcoachlib.domain.task import Task
from taskcoachlib.domain.attachment import AttachmentOwner
from taskcoachlib.thirdparty import guid

class ChangeMonitor(object):
    """
    This class monitors change to object on a per-attribute basis.
    """

    def __init__(self, id_=None):
        super(ChangeMonitor, self).__init__()

        self.__guid = id_ or guid.generate()
        self.__frozen = False

        self.reset()

    def freeze(self):
        self.__frozen = True

    def thaw(self):
        self.__frozen = False

    def guid(self):
        return self.__guid

    def reset(self):
        self._changes = dict()
        self._classes = set()

    def monitorClass(self, klass):
        if klass not in self._classes:
            for name in klass.monitoredAttributes():
                Publisher().registerObserver(self.onAttributeChanged, getattr(klass, '%sChangedEventType' % name)())
                self._classes.add(klass)
            if issubclass(klass, ObservableComposite):
                Publisher().registerObserver(self.onChildAdded, klass.addChildEventType())
                Publisher().registerObserver(self.onChildRemoved, klass.removeChildEventType())
            if issubclass(klass, CategorizableCompositeObject):
                Publisher().registerObserver(self.onCategoryAdded, klass.categoryAddedEventType())
                Publisher().registerObserver(self.onCategoryRemoved, klass.categoryRemovedEventType())
            if issubclass(klass, Task):
                Publisher().registerObserver(self.onOtherObjectAdded, 'task.effort.add')
                Publisher().registerObserver(self.onOtherObjectRemoved, 'task.effort.remove')
            if issubclass(klass, NoteOwner):
                Publisher().registerObserver(self.onOtherObjectAdded, klass.noteAddedEventType())
                Publisher().registerObserver(self.onOtherObjectRemoved, klass.noteRemovedEventType())
            if issubclass(klass, AttachmentOwner):
                Publisher().registerObserver(self.onOtherObjectAdded, klass.attachmentAddedEventType())
                Publisher().registerObserver(self.onOtherObjectRemoved, klass.attachmentRemovedEventType())

    def unmonitorClass(self, klass):
        if klass in self._classes:
            for name in klass.monitoredAttributes():
                Publisher().removeObserver(self.onAttributeChanged, getattr(klass, '%sChangedEventType' % name)())
            if issubclass(klass, ObservableComposite):
                Publisher().removeObserver(self.onChildAdded, klass.addChildEventType())
                Publisher().removeObserver(self.onChildRemoved, klass.removeChildEventType())
            if issubclass(klass, CategorizableCompositeObject):
                Publisher().removeObserver(self.onCategoryAdded, klass.categoryAddedEventType())
                Publisher().removeObserver(self.onCategoryRemoved, klass.categoryRemovedEventType())
            if issubclass(klass, Task):
                Publisher().removeObserver(self.onOtherObjectAdded, 'task.effort.add')
                Publisher().removeObserver(self.onOtherObjectRemoved, 'task.effort.remove')
            if issubclass(klass, NoteOwner):
                Publisher().removeObserver(self.onOtherObjectAdded, klass.noteAddedEventType())
                Publisher().removeObserver(self.onOtherObjectRemoved, klass.noteRemovedEventType())
            if issubclass(klass, AttachmentOwner):
                Publisher().removeObserver(self.onOtherObjectAdded, klass.attachmentAddedEventType())
                Publisher().removeObserver(self.onOtherObjectRemoved, klass.attachmentRemovedEventType())
            self._classes.remove(klass)

    def monitorCollection(self, collection):
        Publisher().registerObserver(self.onObjectAdded, collection.addItemEventType(), eventSource=collection)
        Publisher().registerObserver(self.onObjectRemoved, collection.removeItemEventType(), eventSource=collection)

    def unmonitorCollection(self, collection):
        Publisher().removeObserver(self.onObjectAdded, collection.addItemEventType(), eventSource=collection)
        Publisher().removeObserver(self.onObjectRemoved, collection.removeItemEventType(), eventSource=collection)

    def onAttributeChanged(self, event):
        if self.__frozen:
            return

        for type_, valBySource in event.sourcesAndValuesByType().items():
            for obj in valBySource.keys():
                for name in obj.monitoredAttributes():
                    if type_ == getattr(obj, '%sChangedEventType' % name)():
                        if obj.id() in self._changes and self._changes[obj.id()] is not None:
                            self._changes[obj.id()].add(name)

    def _objectsAdded(self, event):
        for obj in event.values():
            if obj.id() in self._changes:
                if self._changes[obj.id()] is not None and \
                       '__del__' in self._changes[obj.id()]:
                    self._changes[obj.id()].remove('__del__')
            else:
                self._changes[obj.id()] = None

    def _objectsRemoved(self, event):
        for obj in event.values():
            if obj.id() in self._changes:
                if self._changes[obj.id()] is None:
                    del self._changes[obj.id()]
                else:
                    self._changes[obj.id()].add('__del__')

    def onChildAdded(self, event):
        if self.__frozen:
            return

        self._objectsAdded(event)
        for obj in event.values():
            if self._changes[obj.id()] is not None:
                self._changes[obj.id()].add('__parent__')

    def onChildRemoved(self, event):
        if self.__frozen:
            return

        self._objectsRemoved(event)
        for obj in event.values():
            if obj in self._changes and self._changes[obj.id()] is not None:
                self._changes[obj.id()].add('__parent__')

    def onObjectAdded(self, event):
        if self.__frozen:
            return

        self._objectsAdded(event)

    def onObjectRemoved(self, event):
        if self.__frozen:
            return

        self._objectsRemoved(event)

    def onOtherObjectAdded(self, event):
        if self.__frozen:
            return

        self._objectsAdded(event)

    def onOtherObjectRemoved(self, event):
        if self.__frozen:
            return

        self._objectsRemoved(event)

    def _categoryChange(self, event):
        for obj in event.sources():
            if obj.id() in self._changes and self._changes[obj.id()] is not None:
                self._changes[obj.id()].add('__categories__')

    def onCategoryAdded(self, event):
        if self.__frozen:
            return

        self._categoryChange(event)

    def onCategoryRemoved(self, event):
        if self.__frozen:
            return

        self._categoryChange(event)

    def allChanges(self):
        return self._changes

    def getChanges(self, obj):
        return self._changes.get(obj.id(), None)

    def setChanges(self, id_, changes):
        if changes is None:
            del self._changes[id_]
        else:
            self._changes[id_] = changes

    def isRemoved(self, obj):
        return obj.id() in self._changes and \
               self._changes[obj.id()] is not None and \
               '__del__' in self._changes[obj.id()]

    def resetChanges(self, obj):
        self._changes[obj.id()] = set()

    def resetAllChanges(self):
        for id_, changes in self._changes.items():
            if changes is not None and '__del__' in changes:
                del self._changes[id_]
            else:
                self._changes[id_] = set()

    def empty(self):
        self._changes = dict()

    def merge(self, monitor):
        for id_, changes in self._changes.items():
            theirChanges = monitor._changes.get(id_, None)
            if theirChanges is not None:
                changes.update(theirChanges)
