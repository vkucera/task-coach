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

from taskcoachlib.changes import ChangeMonitor


class ChangeSynchronizer(object):
    def __init__(self, monitor, allChanges):
        self._monitor = monitor
        self._allChanges = allChanges

    def sync(self, lists):
        self.diskChanges = ChangeMonitor()

        for devGUID, changes in self._allChanges.items():
            if devGUID == self._monitor.guid():
                self.diskChanges = changes
            else:
                changes.merge(self._monitor)
        self._allChanges[self._monitor.guid()] = self._monitor

        self.allSelfMap = dict()
        self.allOtherMap = dict()

        for oldList, newList in lists:
            self.mergeObjects(oldList, newList)

    def mergeObjects(self, oldList, newList):
        # Map id to object
        def addIds(objects, idMap):
            for obj in objects:
                idMap[obj.id()] = obj
                addIds(obj.children(), idMap)
        selfMap = dict()
        addIds(oldList, selfMap)
        self.allSelfMap.update(selfMap)
        otherMap = dict()
        addIds(newList, otherMap)
        self.allOtherMap.update(otherMap)

        # Objects added on disk or removed from memory
        for otherObject in newList.allItemsSorted():
            memChanges = self._monitor.getChanges(otherObject)
            if memChanges is not None and '__del__' in memChanges:
                newList.remove(otherObject)
                del otherMap[otherObject.id()]
            elif otherObject.id() not in selfMap:
                for child in otherObject.children():
                    otherObject.removeChild(child)
                parent = otherObject.parent()
                if parent is not None:
                    parent = selfMap[parent.id()]
                    parent.addChild(otherObject)
                    otherObject.setParent(parent)
                oldList.append(otherObject)
                self._monitor.setChanges(otherObject.id(), set())
                selfMap[otherObject.id()] = otherObject

        # Objects removed from disk
        for selfObject in oldList.allItemsSorted():
            ch = self.diskChanges.getChanges(selfObject)
            if ch is not None and '__del__' in ch:
                oldList.remove(selfObject)
                self._monitor.setChanges(selfObject.id(), None)
                del selfMap[selfObject.id()]

        # Objects changed on disk
        for selfObject in oldList.allItemsSorted():
            objChanges = self.diskChanges.getChanges(selfObject)
            if objChanges is not None and objChanges:
                memChanges = self._monitor.getChanges(selfObject)
                otherObject = otherMap[selfObject.id()]
                conflicts = []
                for changeName in objChanges:
                    if changeName == '__parent__':
                        # Note: no conflict resolution for this one,
                        # it would be a bit tricky... Instead, the
                        # "memory" version wins.
                        def sameParents(a, b):
                            if a is None and b is None:
                                return True
                            elif a is None or b is None:
                                return False
                            return a.id() == b.id()

                        if not (memChanges is not None and \
                                '__parent__' in memChanges and \
                                not sameParents(selfObject.parent(), otherObject.parent())):
                            oldParent = selfObject.parent()
                            newParent = otherObject.parent()
                            if oldParent is not None:
                                oldParent.removeChild(selfObject)
                            if newParent is not None:
                                newParent = selfMap[newParent.id()]
                                newParent.addChild(selfObject)
                            selfObject.setParent(newParent)
                    elif changeName == '__categories__':
                        otherCategories = set([self.allSelfMap[category.id()] for category in otherObject.categories()])
                        if memChanges is not None and \
                           '__categories__' in memChanges and \
                           otherCategories != selfObject.categories():
                            conflicts.append('__categories__')
                        else:
                            for cat in selfObject.categories():
                                cat.removeCategorizable(selfObject)
                                selfObject.removeCategory(cat)
                            for cat in otherCategories:
                                cat.addCategorizable(selfObject)
                                selfObject.addCategory(cat)
                    elif changeName == 'appearance':
                        attrNames = ['foregroundColor', 'backgroundColor', 'font', 'icon', 'selectedIcon']
                        if memChanges is not None and \
                           'appearance' in memChanges:
                            for attrName in attrNames:
                                if getattr(selfObject, attrName)() != getattr(otherObject, attrName)():
                                    conflicts.append(attrName)
                        else:
                            for attrName in attrNames:
                                getattr(selfObject, 'set' + attrName[0].upper() + attrName[1:])(getattr(otherObject, attrName)())
                    elif changeName == 'expandedContexts':
                        # Note: no conflict resolution for this one.
                        selfObject.expand(otherObject.isExpanded())
                    else:
                        if memChanges is not None and \
                               changeName in memChanges and \
                               getattr(selfObject, changeName)() != getattr(otherObject, changeName)():
                            conflicts.append(changeName)
                        else:
                            getattr(selfObject, 'set' + changeName[0].upper() + changeName[1:])(getattr(otherObject, changeName)())

                if conflicts:
                    print conflicts # XXXTODO
