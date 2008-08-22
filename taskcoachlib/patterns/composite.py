'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>

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

import observer


class Composite(object):
    def __init__(self, *args, **kwargs):
        children = kwargs.pop('children', [])
        parent = kwargs.pop('parent', None)
        super(Composite, self).__init__(*args, **kwargs)
        self.__parent = parent
        self.__children = children
        for child in children:
            child.setParent(self)
        
    def __getstate__(self):
        return dict(children=self.__children[:], 
                    parent=self.__parent)
    
    def __setstate__(self, state):
        self.__parent = state['parent']
        self.__children = state['children']
    
    def parent(self):
        return self.__parent
    
    def ancestors(self):
        parent = self.parent()
        if parent:
            return parent.ancestors() + [parent]
        else:
            return []
    
    def family(self):
        return self.ancestors() + [self] + self.children(recursive=True)
    
    def setParent(self, parent):
        self.__parent = parent
    
    def children(self, recursive=False):
        if recursive:
            result = self.__children[:]
            for child in self.__children:
                result.extend(child.children(recursive=True))
            return result
        else:
            return self.__children

    def copy(self, *args, **kwargs):
        kwargs['parent'] = self.parent()
        kwargs['children'] = [child.copy() for child in self.children()]
        return self.__class__(*args, **kwargs)
        
    def newChild(self, *args, **kwargs):
        kwargs['parent'] = self
        return self.__class__(*args, **kwargs)
    
    def addChild(self, child):
        self.__children.append(child)
        child.setParent(self)
        
    def removeChild(self, child):
        self.__children.remove(child)
        # We don't reset the parent of the child, because that makes restoring
        # the parent-child relationship easier.
    
    # FIXME: this is for do/undo, need a better, generic, implementation
    def replaceChildren(self, children): 
        self.__children = children
    
    def replaceParent(self, parent):
        self.__parent = parent
        

class ObservableComposite(Composite, observer.Observable):
    @classmethod
    def addChildEventType(class_):
        return 'composite(%s).child.add'%class_
    
    @classmethod
    def removeChildEventType(class_):
        return 'composite(%s).child.remove'%class_
    
    def addChild(self, child):
        super(ObservableComposite, self).addChild(child)
        self.notifyObservers(observer.Event(self, self.addChildEventType(), 
                                            child))
                                            
    def removeChild(self, child):
        super(ObservableComposite, self).removeChild(child)
        self.notifyObservers(observer.Event(self, self.removeChildEventType(),
                                            child))


class CompositeCollection(object):
    def __init__(self, initList=None, *args, **kwargs):
        super(CompositeCollection, self).__init__(*args, **kwargs)
        self.extend(initList or [])
    
    def append(self, composite):
        self.extend([composite])

    def extend(self, composites):
        if not composites:
            return
        compositesAndAllChildren = self._compositesAndAllChildren(composites) 
        self.stopNotifying()
        super(CompositeCollection, self).extend(compositesAndAllChildren)
        parentsWithChildrenAdded = self._addCompositesToParent(composites)
        self.startNotifying()
        self.notifyObserversOfItemsAdded(*compositesAndAllChildren)
        for parent, children in parentsWithChildrenAdded.items():
            self.notifyObservers(observer.Event(parent,
                parent.addChildEventType(), *children))
            
    def _compositesAndAllChildren(self, composites):
        compositesAndAllChildren = set(composites) 
        for composite in composites:
            compositesAndAllChildren |= set(composite.children(recursive=True))
        return list(compositesAndAllChildren)

    def _addCompositesToParent(self, composites):
        parents = {}
        for composite in composites:
            parent = composite.parent()
            if parent and parent in self and composite not in parent.children():
                parent.addChild(composite)
                if parent not in composites:
                    parents.setdefault(parent, []).append(composite)
        return parents
    
    def remove(self, composite):
        if composite in self:
            self.removeItems([composite])

    def removeItems(self, composites):
        if not composites:
            return
        parents, children = self._splitCompositesInParentsAndChildren(composites)
        compositesAndAllChildren = self._compositesAndAllChildren(parents)
        self.stopNotifying()
        self._removeCompositesFromCollection(parents)
        parentsWithChildrenRemoved = self._removeCompositesFromParent(composites)
        self.startNotifying()
        self.notifyObserversOfItemsRemoved(*compositesAndAllChildren)
        for parent, children in parentsWithChildrenRemoved.items():
            if parent in self:
                self.notifyObservers(observer.Event(parent,
                    parent.removeChildEventType(), *children))

    def _splitCompositesInParentsAndChildren(self, composites):
        parents, children = [], []
        for composite in composites:
            for ancestor in composite.ancestors():
                if ancestor in composites:
                    children.append(composite)
                    break
            else:
                parents.append(composite)
        return parents, children                      

    def _removeCompositesFromCollection(self, composites):
        for composite in composites:
            if composite in self:
                self._removeCompositeFromCollection(composite)
                
    def _removeCompositeFromCollection(self, composite):
        self._removeCompositesFromCollection(composite.children())
        super(CompositeCollection, self).remove(composite)

    def _removeCompositesFromParent(self, composites):
        parents = {}
        for composite in composites:
            parent = composite.parent()
            if parent:
                parent.removeChild(composite)
                if parent not in composites:
                    parents.setdefault(parent, []).append(composite)
        return parents
                            
    def rootItems(self):
        return [composite for composite in self if composite.parent() is None or \
                composite.parent() not in self]                                            


class CompositeSet(CompositeCollection, observer.ObservableSet):
    pass

    
class CompositeList(CompositeCollection, observer.ObservableList):
    pass

