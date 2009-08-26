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
from taskcoachlib.domain import base, note, attachment, categorizable


class Category(attachment.AttachmentOwner, note.NoteOwner, base.CompositeObject):
    def __init__(self, subject, categorizables=None, children=None, filtered=False, 
                 parent=None, description='', color=None, *args, **kwargs):
        super(Category, self).__init__(subject=subject, children=children or [], 
                                       parent=parent, description=description,
                                       color=color, *args, **kwargs)
        self.__categorizables = base.SetAttribute(set(categorizables or []),
                                                  self,
                                                  self.categorizableAddedEvent,
                                                  self.categorizableRemovedEvent)
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
        state.update(dict(categorizables=self.__categorizables.get(), 
                          filtered=self.__filtered))
        return state
        
    def __setstate__(self, state, event=None):
        notify = event is None
        event = event or patterns.Event()
        super(Category, self).__setstate__(state, event)
        self.setCategorizables(state['categorizables'], event)
        self.setFiltered(state['filtered'], event)
        if notify:
            event.send()

    def __getcopystate__(self):
        state = super(Category, self).__getcopystate__()
        state.update(dict(categorizables=self.__categorizables.get(), 
                          filtered=self.__filtered))
        return state
            
    def subjectChangedEvent(self, event):
        super(Category, self).subjectChangedEvent(event)
        self.categorySubjectChangedEvent(event)
    
    def categorySubjectChangedEvent(self, event):
        subject = self.subject()
        for eachCategorizable in self.categorizables(recursive=True):
            eachCategorizable.categorySubjectChangedEvent(event, subject)
            eachCategorizable.totalCategorySubjectChangedEvent(event, subject)      
                    
    def categorizables(self, recursive=False):
        result = self.__categorizables.get()
        if recursive:
            for child in self.children():
                result |= child.categorizables(recursive)
        return result
    
    def addCategorizable(self, *categorizables, **kwargs):
        self.__categorizables.add(set(categorizables), kwargs.pop('event', None))
        
    def categorizableAddedEvent(self, event, *categorizables):
        event.addSource(self, *categorizables, 
                        **dict(type=self.categorizableAddedEventType()))
            
    def removeCategorizable(self, *categorizables, **kwargs):
        self.__categorizables.remove(set(categorizables), kwargs.pop('event', None))
        
    def categorizableRemovedEvent(self, event, *categorizables):
        event.addSource(self, *categorizables,
                        **dict(type=self.categorizableRemovedEventType()))
    
    def setCategorizables(self, categorizables, event=None):
        self.__categorizables.set(set(categorizables), event)
            
    def isFiltered(self):
        return self.__filtered
    
    def setFiltered(self, filtered=True, event=None, recursive=True):
        if filtered == self.__filtered:
            return
        notify = event is None
        event = event or patterns.Event()
        self.__filtered = filtered
        self.filterChangedEvent(event)
        if filtered and recursive:
            for familyMember in self.ancestors() + self.children(recursive=True):
                familyMember.setFiltered(False, event, recursive=False)
        if notify:
            event.send()
                    
    def filterChangedEvent(self, event):
        event.addSource(self, self.isFiltered(), 
                        type=self.filterChangedEventType())
                                
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
        super(Category, self).colorChangedEvent(event)
        for categorizable in self.categorizables(recursive=True):
            categorizable.colorChangedEvent(event)
