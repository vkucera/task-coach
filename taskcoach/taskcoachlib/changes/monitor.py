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

class ChangeMonitor(object):
    """
    This class monitors change to object on a per-attribute basis.
    """

    def __init__(self):
        super(ChangeMonitor, self).__init__()

        self.reset()

    def reset(self):
        self._changes = dict()
        self._classes = set()
        self._removed = dict()

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
            self._classes.remove(klass)

    def monitorCollection(self, collection):
        Publisher().registerObserver(self.onObjectAdded, collection.addItemEventType(), eventSource=collection)
        Publisher().registerObserver(self.onObjectRemoved, collection.removeItemEventType(), eventSource=collection)

    def unmonitorCollection(self, collection):
        Publisher().removeObserver(self.onObjectAdded, collection.addItemEventType(), eventSource=collection)
        Publisher().removeObserver(self.onObjectRemoved, collection.removeItemEventType(), eventSource=collection)

    def onAttributeChanged(self, event):
        for obj in event.sources():
            for name in obj.monitoredAttributes():
                if event.type() == getattr(obj, '%sChangedEventType' % name)():
                    changes = None
                    if obj.id() in self._changes:
                        container = self._changes
                        changes = self._changes[obj.id()]
                    elif obj.id() in self._removed:
                        container = self._removed
                        changes = self._removed[obj.id()]
                    if changes is not None:
                        changes.add(name)
                        container[obj.id()] = changes
                    break

    def _objectsAdded(self, event):
        for obj in event.values():
            if obj.id() in self._removed:
                self._changes[obj.id()] = self._removed[obj.id()]
                del self._removed[obj.id()]
            elif obj.id() not in self._changes:
                self._changes[obj.id()] = None

    def _objectsRemoved(self, event):
        for obj in event.values():
            self._removed[obj.id()] = self._changes[obj.id()]
            del self._changes[obj.id()]

    def onChildAdded(self, event):
        self._objectsAdded(event)
        for obj in event.values():
            if self._changes[obj.id()] is not None:
                self._changes[obj.id()].add('__parent__')

    def onChildRemoved(self, event):
        self._objectsRemoved(event)
        for obj in event.values():
            if self._removed[obj.id()] is not None:
                self._removed[obj.id()].add('__parent__')

    def onObjectAdded(self, event):
        self._objectsAdded(event)

    def onObjectRemoved(self, event):
        self._objectsRemoved(event)

    def _categoryChange(self, event):
        for obj in event.sources():
            if obj.id() in self._changes and self._changes[obj.id()] is not None:
                self._changes[obj.id()].add('__categories__')

    def onCategoryAdded(self, event):
        self._categoryChange(event)

    def onCategoryRemoved(self, event):
        self._categoryChange(event)

    def getChanges(self, obj):
        return self._changes.get(obj.id(), None)

    def isRemoved(self, obj):
        return obj.id() in self._removed

    def resetChanges(self, obj):
        self._changes[obj.id()] = set()

    def resetAllChanges(self):
        for id_ in self._changes.keys():
            self._changes[id_] = set()
        self._removed = dict()
