'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2009 Frank Niessink <frank@niessink.com>

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

from taskcoachlib import patterns
from taskcoachlib.domain import base, note, attachment


class Category(attachment.AttachmentOwner, note.NoteOwner, base.CompositeObject):
    def __init__(self, subject, categorizables=None, children=None, filtered=False, 
                 parent=None, description='', color=None, *args, **kwargs):
        super(Category, self).__init__(subject=subject, children=children or [], 
                                       parent=parent, description=description,
                                       color=color, *args, **kwargs)
        self.__categorizables = categorizables or []
        self.__filtered = filtered
            
    @classmethod
    def filterChangedEventType(class_):
        return 'category.filter'
    
    @classmethod
    def categorizableAddedEventType(class_):
        return 'category.categorizable.added'
    
    @classmethod
    def categorizableRemovedEventType(class_):
        return 'category.categorizable.removed'
    
    @classmethod
    def modificationEventTypes(class_):
        eventTypes = super(Category, class_).modificationEventTypes()
        return eventTypes + [class_.filterChangedEventType(),
                             class_.categorizableAddedEventType(),
                             class_.categorizableRemovedEventType()]
                
    def __getstate__(self):
        state = super(Category, self).__getstate__()
        state.update(dict(categorizables=self.__categorizables[:], 
                          filtered=self.__filtered))
        return state
        
    def __setstate__(self, state):
        super(Category, self).__setstate__(state)
        self.__categorizables = state['categorizables']
        self.__filtered = state['filtered']

    def __getcopystate__(self):
        state = super(Category, self).__getcopystate__()
        state.update(dict(categorizables=self.__categorizables[:], 
                          filtered=self.__filtered))
        return state

    def setSubject(self, *args, **kwargs):
        if super(Category, self).setSubject(*args, **kwargs):
            for categorizable in self.categorizables(recursive=True):
                categorizable.notifyObserversOfCategorySubjectChange(self)
    
    def categorizables(self, recursive=False):
        result = []
        if recursive:
            for child in self.children():
                result.extend(child.categorizables(recursive))
        result.extend(self.__categorizables)
        return result
    
    def addCategorizable(self, categorizable):
        if categorizable not in self.__categorizables: # FIXME: use set
            self.__categorizables.append(categorizable)
            self.notifyObservers(patterns.Event(self, 
                self.categorizableAddedEventType(), categorizable))
            
    def removeCategorizable(self, categorizable):
        if categorizable in self.__categorizables:
            self.__categorizables.remove(categorizable)
            self.notifyObservers(patterns.Event(self, 
                self.categorizableRemovedEventType(), categorizable))
            
    def isFiltered(self):
        return self.__filtered
    
    def setFiltered(self, filtered=True):
        if filtered != self.__filtered:
            self.__filtered = filtered
            self.notifyObservers(patterns.Event(self, 
                self.filterChangedEventType(), filtered))
        if filtered:
            self._turnOffFilteringOfParent()
            self._turnOffFilteringOfChildren()
            
    def _turnOffFilteringOfChildren(self):
        for child in self.children():
            child.setFiltered(False)
            child._turnOffFilteringOfChildren()
            
    def _turnOffFilteringOfParent(self):
        parent = self.parent()
        if parent:
            parent.setFiltered(False)
            parent._turnOffFilteringOfParent()
        
    def contains(self, categorizable, treeMode=False):
        containedCategorizables = self.categorizables(recursive=True)
        if treeMode:
            categorizablesToInvestigate = categorizable.family()
        else:
            categorizablesToInvestigate = [categorizable] + categorizable.ancestors()
        for categorizableToInvestigate in categorizablesToInvestigate:
            if categorizableToInvestigate in containedCategorizables:
                return True
        return False
                            
    def notifyObserversOfColorChange(self, color):
        super(Category, self).notifyObserversOfColorChange(color)
        for categorizable in self.categorizables(recursive=True):
            categorizable.notifyObserversOfColorChange(color)

