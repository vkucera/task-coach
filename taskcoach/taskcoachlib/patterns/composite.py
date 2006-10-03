import patterns

class Composite(object):
    def __init__(self, *args, **kwargs):
        children = kwargs.pop('children', [])
        parent = kwargs.pop('parent', None)
        super(Composite, self).__init__(*args, **kwargs)
        self.__parent = parent
        self.__children = children
        for child in children:
            child.setParent(self)
        
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
            return self.__children + [descendent for child in self.__children 
                for descendent in child.children(recursive=True)]
        else:
            return self.__children
    
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
        

class ObservableComposite(Composite, patterns.Observable):
    @classmethod
    def addChildEventType(class_):
        return 'composite(%s).child.add'%class_
    
    @classmethod
    def removeChildEventType(class_):
        return 'composite(%s).child.remove'%class_
    
    def addChild(self, child):
        super(ObservableComposite, self).addChild(child)
        self.notifyObservers(patterns.Event(self, self.addChildEventType(), 
                                            child))
                                            
    def removeChild(self, child):
        super(ObservableComposite, self).removeChild(child)
        self.notifyObservers(patterns.Event(self, self.removeChildEventType(),
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
            self.notifyObservers(patterns.Event(parent,
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
                self.notifyObservers(patterns.Event(parent,
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


class CompositeSet(CompositeCollection, patterns.ObservableSet):
    pass

    
class CompositeList(CompositeCollection, patterns.ObservableList):
    pass