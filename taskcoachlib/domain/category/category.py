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
import categorizable


class Category(attachment.AttachmentOwner, note.NoteOwner, base.CompositeObject):
    def __init__(self, subject, categorizables=None, children=None, filtered=False, 
                 parent=None, description='', color=None, *args, **kwargs):
        super(Category, self).__init__(subject=subject, children=children or [], 
                                       parent=parent, description=description,
                                       color=color, *args, **kwargs)
        self.__categorizables = set(categorizables or [])
        self.__filtered = filtered
            
    @classmethod
    def filterChangedEventType(class_):
        ''' Event type to notify observers that categorizables belonging to
            this category are filtered or not. '''
        return 'category.filter'
    
    @classmethod
    def categorizableAddedEventType(class_):
        ''' Event type to notify observers that categorizables have been added
            to this category. '''
        return 'category.categorizable.added'
    
    @classmethod
    def categorizableRemovedEventType(class_):
        ''' Event type to notify observers that categorizables have been removed
            from this category. ''' 
        return 'category.categorizable.removed'
    
    @classmethod
    def modificationEventTypes(class_):
        eventTypes = super(Category, class_).modificationEventTypes()
        return eventTypes + [class_.filterChangedEventType(),
                             class_.categorizableAddedEventType(),
                             class_.categorizableRemovedEventType()]
                
    def __getstate__(self):
        state = super(Category, self).__getstate__()
        state.update(dict(categorizables=self.__categorizables.copy(), 
                          filtered=self.__filtered))
        return state
        
    def __setstate__(self, state, event=None):
        notify = event is None
        event = event or patterns.Event()
        event = super(Category, self).__setstate__(state, event)
        event = self.setCategorizables(state['categorizables'], event)
        event = self.setFiltered(state['filtered'], event)
        if notify:
            event.send()
        else:
            return event

    def __getcopystate__(self):
        state = super(Category, self).__getcopystate__()
        state.update(dict(categorizables=self.__categorizables.copy(), 
                          filtered=self.__filtered))
        return state
            
    def subjectChangedEvent(self, event):
        event = super(Category, self).subjectChangedEvent(event)
        event = self.categorySubjectChangedEvent(event)
        return event
    
    def categorySubjectChangedEvent(self, event):
        subject = self.subject()
        for eachCategorizable in self.categorizables(recursive=True):
            event = eachCategorizable.categorySubjectChangedEvent(event, subject)
            event = eachCategorizable.totalCategorySubjectChangedEvent(event, subject)
        return event        
                    
    def categorizables(self, recursive=False):
        result = self.__categorizables.copy()
        if recursive:
            for child in self.children():
                result |= child.categorizables(recursive)
        return result
    
    def addCategorizable(self, *categorizables, **kwargs):
        categorizables = set(categorizables)
        event = kwargs.pop('event', None)
        if categorizables <= self.__categorizables:
            return event
        notify = event is None
        event = event or patterns.Event()
        self.__categorizables |= categorizables
        event = self.categorizableAddedEvent(event, *categorizables)
        if notify:
            event.send()
        else:
            return event
        
    def categorizableAddedEvent(self, event, *categorizables):
        event.addSource(self, *categorizables, 
                        **dict(type=self.categorizableAddedEventType()))
        return event
            
    def removeCategorizable(self, *categorizables, **kwargs):
        categorizables = set(categorizables)
        event = kwargs.pop('event', None)
        if categorizables & self.__categorizables == set():
            return event
        notify = event is None
        event = event or patterns.Event()
        self.__categorizables -= categorizables
        event = self.categorizableRemovedEvent(event, *categorizables)
        if notify:
            event.send()
        else:
            return event
    
    def categorizableRemovedEvent(self, event, *categorizables):
        event.addSource(self, *categorizables,
                        **dict(type=self.categorizableRemovedEventType()))
        return event
    
    def setCategorizables(self, categorizables, event=None):
        if set(categorizables) == self.__categorizables:
            return event
        notify = event is None
        event = event or patterns.Event()
        event = self.removeCategorizable(*self.categorizables(), **dict(event=event))
        event = self.addCategorizable(*categorizables, **dict(event=event))
        if notify:
            event.send()
        else:
            return event
            
    def isFiltered(self):
        return self.__filtered
    
    def setFiltered(self, filtered=True, event=None, recursive=True):
        if filtered == self.__filtered:
            return event
        notify = event is None
        event = event or patterns.Event()
        self.__filtered = filtered
        event = self.filterChangedEvent(event)
        if filtered and recursive:
            for familyMember in self.ancestors() + self.children(recursive=True):
                event = familyMember.setFiltered(False, event, recursive=False)
        if notify:
            event.send()
        else:
            return event
                    
    def filterChangedEvent(self, event):
        event.addSource(self, self.isFiltered(), type=self.filterChangedEventType())
        return event
                                
    def contains(self, categorizable, treeMode=False):
        ''' Return whether the categorizable belongs to this category. If an
            ancestor of the categorizable belong to this category, the 
            categorizable itself belongs to this category too. '''
        containedCategorizables = self.categorizables(recursive=True)
        if treeMode:
            categorizablesToInvestigate = categorizable.family()
        else:
            categorizablesToInvestigate = [categorizable] + categorizable.ancestors()
        for categorizableToInvestigate in categorizablesToInvestigate:
            if categorizableToInvestigate in containedCategorizables:
                return True
        return False
    
    def colorChangedEvent(self, event):
        ''' Override to include all categorizables (recursively) in the event 
            that belong to this category since their colors (may) have 
            changed too. ''' 
        event = super(Category, self).colorChangedEvent(event)
        for categorizable in self.categorizables(recursive=True):
            event = categorizable.colorChangedEvent(event)
        return event
