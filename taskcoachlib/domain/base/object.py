# -*- coding: utf-8 -*-

'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2009 Frank Niessink <frank@niessink.com>
Copyright (C) 2008 Jerome Laheurte <fraca7@free.fr>

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

import time
from taskcoachlib import patterns
from taskcoachlib.domain import date


class SynchronizedObject(patterns.Observable):
    STATUS_NONE    = 0
    STATUS_NEW     = 1
    STATUS_CHANGED = 2
    STATUS_DELETED = 3

    def __init__(self, *args, **kwargs):
        self.__status = kwargs.pop('status', self.STATUS_NEW)
        super(SynchronizedObject, self).__init__(*args, **kwargs)

    @classmethod
    def markDeletedEventType(class_):
        return 'object.markdeleted'

    @classmethod
    def markNotDeletedEventType(class_):
        return 'object.marknotdeleted'
        
    def __getstate__(self):
        try:
            state = super(SynchronizedObject, self).__getstate__()
        except AttributeError:
            state = dict()

        state['status'] = self.__status
        return state

    def __setstate__(self, state):
        try:
            super(SynchronizedObject, self).__setstate__(state)
        except AttributeError:
            pass
        if state['status'] == self.__status:
            return
        if state['status'] == self.STATUS_CHANGED:
            self.markDirty()
        elif state['status'] == self.STATUS_DELETED:
            self.markDeleted()
        elif state['status'] == self.STATUS_NEW:
            self.markNew()
        elif state['status'] == self.STATUS_NONE:
            self.cleanDirty()

    def getStatus(self):
        return self.__status

    def markDirty(self, force=False):
        oldstatus = self.__status
        if self.__status == self.STATUS_NONE or force:
            self.__status = self.STATUS_CHANGED
            if oldstatus == self.STATUS_DELETED:
                self.notifyObservers(patterns.Event( \
                    self.markNotDeletedEventType(), self, self.__status))

    def markNew(self):
        oldstatus = self.__status
        self.__status = self.STATUS_NEW
        if oldstatus == self.STATUS_DELETED:
            self.notifyObservers(patterns.Event( \
                 self.markNotDeletedEventType(), self, self.__status))

    def markDeleted(self):
        self.__status = self.STATUS_DELETED
        self.notifyObservers(patterns.Event( \
            self.markDeletedEventType(), self, self.__status))

    def cleanDirty(self):
        oldstatus = self.__status
        self.__status = self.STATUS_NONE
        if oldstatus == self.STATUS_DELETED:
            self.notifyObservers(patterns.Event( \
                 self.markNotDeletedEventType(), self, self.__status))

    def isNew(self):
        return self.__status == self.STATUS_NEW

    def isModified(self):
        return self.__status == self.STATUS_CHANGED

    def isDeleted(self):
        return self.__status == self.STATUS_DELETED


class Object(SynchronizedObject):
    def __init__(self, *args, **kwargs):
        self.__subject = kwargs.pop('subject', '')
        self.__description = kwargs.pop('description', '')
        self.__color = kwargs.pop('color', None)
        self.__id = kwargs.pop('id', None) or '%s:%s'%(id(self), time.time())
        # FIXME: Not a valid XML id
        # FIXME: When dropping support for python 2.4, use the uuid module
        super(Object, self).__init__(*args, **kwargs)
        
    def __repr__(self):
        return self.subject()

    def __getstate__(self):
        try:
            state = super(Object, self).__getstate__()
        except AttributeError:
            state = dict()
        state.update(dict(id=self.__id, subject=self.__subject, 
                          description=self.__description,
                          color=self.__color))
        return state
    
    def __setstate__(self, state):
        try:
            super(Object, self).__setstate__(state)
        except AttributeError:
            pass
        self.setId(state['id'])
        self.setSubject(state['subject'])
        self.setDescription(state['description'])
        self.setColor(state['color'])

    def __getcopystate__(self):
        ''' Return a dictionary that can be passed to __init__ when creating
            a copy of the object. 
            
            E.g. copy = obj.__class__(**original.__getcopystate__()) '''
        try:
            state = super(Object, self).__getcopystate__()
        except AttributeError:
            state = dict()
        # Note: we don't put the id in the state dict, because a copy should
        # get a new id:
        state.update(dict(\
            subject=self.__subject, description=self.__description,
            color=self.__color))
        return state
    
    def copy(self):
        return self.__class__(**self.__getcopystate__())
 
    # Id:
       
    def id(self):
        return self.__id
    
    def setId(self, id):
        self.__id = id
        
    # Subject:
    
    def subject(self):
        return self.__subject
    
    def setSubject(self, subject):
        if subject != self.__subject:
            self.__subject = subject
            self.notifyObservers(patterns.Event( \
                self.subjectChangedEventType(), self, subject))
            return True # Subject was changed
        else:
            return False # Subject was not changed
    
    @classmethod    
    def subjectChangedEventType(class_):
        return '%s.subject'%class_
    
    # Description:
    
    def description(self):
        return self.__description
    
    def setDescription(self, description):
        if description != self.__description:
            self.__description = description
            self.notifyObservers(patterns.Event( \
                self.descriptionChangedEventType(), self, description))
            return True # Description was changed
        else:
            return False # Description was not changed
        
    @classmethod    
    def descriptionChangedEventType(class_):
        return '%s.description'%class_
    
    # Color:
    
    def setColor(self, color):
        if color != self.__color:
            self.__color = color
            self.notifyObserversOfColorChange(color)
        
    def color(self, recursive=True):
        # The 'recursive' argument isn't  actually used here, but some
        # code assumes  composite objects where there  aren't. This is
        # the simplest workaround.
        return self.__color

    @classmethod
    def colorChangedEventType(class_):
        return '%s.color'%class_
    
    def notifyObserversOfColorChange(self, color):
        self.notifyObservers(patterns.Event(self.colorChangedEventType(), 
                                            self, color))
        
    # Event types:
    
    @classmethod
    def modificationEventTypes(class_):
        eventTypes = super(Object, class_).modificationEventTypes()
        return eventTypes + [class_.subjectChangedEventType(),
                             class_.descriptionChangedEventType(),
                             class_.colorChangedEventType()]


class CompositeObject(Object, patterns.ObservableComposite):
    def __init__(self, *args, **kwargs):
        self.__expandedContexts = set()
        for context in kwargs.pop('expandedContexts', []):
            self.__expandedContexts.add(context)
        super(CompositeObject, self).__init__(*args, **kwargs)

    def __getcopystate__(self):
        state = super(CompositeObject, self).__getcopystate__()
        state.update(dict(expandedContexts=self.expandedContexts()))
        return state

    # Subject:
    
    def subject(self, recursive=False):
        subject = super(CompositeObject, self).subject()
        if recursive and self.parent():
            subject = u'%s -> %s'%(self.parent().subject(recursive=True), subject)
        return subject
        
    # Description:
        
    def description(self, recursive=False):
        # Allow for the recursive flag, but ignore it
        return super(CompositeObject, self).description()
        
    # Expansion state:

    # Note: expansion state is stored by context. A context is a simple string
    # identifier (without comma's) to distinguish between different contexts,
    # i.e. viewers. A composite object may be expanded in one context and
    # collapsed in another.
    
    def isExpanded(self, context='None'):
        ''' Returns a boolean indicating whether the composite object is 
            expanded in the specified context. ''' 
        return context in self.__expandedContexts

    def expandedContexts(self):
        ''' Returns a list of contexts where this composite object is 
            expanded. ''' 
        return list(self.__expandedContexts)
    
    def expand(self, expand=True, context='None'):
        ''' Expands (or collapses) the composite object in the specified 
            context. ''' 
        wasExpanded = self.isExpanded(context)
        if expand:
            self.__expandedContexts.add(context)
        elif context in self.__expandedContexts:
            self.__expandedContexts.remove(context)
        if expand != wasExpanded:
            self.notifyObserversOfExpansionChange()

    @classmethod
    def expansionChangedEventType(class_):
        return '%s.expanded'%class_

    def notifyObserversOfExpansionChange(self):
        self.notifyObservers(patterns.Event(self.expansionChangedEventType(), 
                                            self))
        
    # Color:
        
    def color(self, recursive=True):
        myColor = super(CompositeObject, self).color()
        if not myColor and recursive and self.parent():
            return self.parent().color()
        else:
            return myColor
        
    def notifyObserversOfColorChange(self, color):
        super(CompositeObject, self).notifyObserversOfColorChange(color)
        for child in self.children():
            child.notifyObserversOfParentColorChange(color)

    def notifyObserversOfParentColorChange(self, color):
        ''' If this object has its own color, do nothing. If this object
            uses the color of its parent, notify its observers of the color 
            change. And similarly for the children of this object. '''
        if self.color(recursive=False) is None:
            self.notifyObservers(patterns.Event(self.colorChangedEventType(),
                                                self, color))
            for child in self.children():
                child.notifyObserversOfParentColorChange(color)

    # Event types:

    @classmethod
    def modificationEventTypes(class_):
        return super(CompositeObject, class_).modificationEventTypes() + \
            [class_.expansionChangedEventType()]

    # Override SynchronizedObject methods to also mark child objects

    def markDeleted(self, *args, **kwargs):
        super(CompositeObject, self).markDeleted(*args, **kwargs)
        for child in self.children():
            child.markDeleted(*args, **kwargs)
            
    def markNew(self, *args, **kwargs):
        super(CompositeObject, self).markNew(*args, **kwargs)
        for child in self.children():
            child.markNew(*args, **kwargs)

    def markDirty(self, *args, **kwargs):
        super(CompositeObject, self).markDirty(*args, **kwargs)
        for child in self.children():
            child.markDirty(*args, **kwargs)
            
    def cleanDirty(self, *args, **kwargs):        
        super(CompositeObject, self).cleanDirty(*args, **kwargs)
        for child in self.children():
            child.cleanDirty(*args, **kwargs)

