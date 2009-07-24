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


class SynchronizedObject(object):
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

    def __setstate__(self, state, event=None):
        notify = event is None
        event = event or patterns.Event()
        try:
            event = super(SynchronizedObject, self).__setstate__(state, event)
        except AttributeError:
            pass
        if state['status'] != self.__status:
            if state['status'] == self.STATUS_CHANGED:
                event = self.markDirty(event=event)
            elif state['status'] == self.STATUS_DELETED:
                event = self.markDeleted(event)
            elif state['status'] == self.STATUS_NEW:
                event = self.markNew(event)
            elif state['status'] == self.STATUS_NONE:
                event = self.cleanDirty(event)
        if notify:
            event.send()
        else:
            return event

    def getStatus(self):
        return self.__status
        
    def markDirty(self, force=False, event=None):
        if not self.setStatusDirty(force):
            return event
        notify = event is None
        event = event or patterns.Event()
        event.addSource(self, self.__status, 
                        type=self.markNotDeletedEventType())
        if notify:
            event.send()
        else:
            return event

    def setStatusDirty(self, force=False):
        oldStatus = self.__status
        if self.__status == self.STATUS_NONE or force:
            self.__status = self.STATUS_CHANGED
            return oldStatus == self.STATUS_DELETED
        else:
            return False

    def markNew(self, event=None):
        if not self.setStatusNew():
            return event
        notify = event is None
        event = event or patterns.Event()
        event.addSource(self, self.__status,
                        type=self.markNotDeletedEventType())
        if notify:
            event.send()
        else:
            return event
            
    def setStatusNew(self):
        oldStatus = self.__status
        self.__status = self.STATUS_NEW
        return oldStatus == self.STATUS_DELETED

    def markDeleted(self, event=None):
        notify = event is None
        event = event or patterns.Event()
        self.setStatusDeleted()
        event.addSource(self, self.__status, type=self.markDeletedEventType())
        if notify:
            event.send()
        else:
            return event

    def setStatusDeleted(self):
        self.__status = self.STATUS_DELETED

    def cleanDirty(self, event=None):
        if not self.setStatusNone():
            return event
        notify = event is None
        event = event or patterns.Event()
        event.addSource(self, self.__status, 
                        type=self.markNotDeletedEventType())
        if notify:
            event.send()
        else:
            return event
            
    def setStatusNone(self):
        oldStatus = self.__status
        self.__status = self.STATUS_NONE
        return oldStatus == self.STATUS_DELETED

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
    
    def __setstate__(self, state, event=None):
        notify = event is None
        event = event or patterns.Event()
        try:
            event = super(Object, self).__setstate__(state, event)
        except AttributeError:
            pass
        self.setId(state['id'])
        event = self.setSubject(state['subject'], event)
        event = self.setDescription(state['description'], event)
        event = self.setColor(state['color'], event)
        if notify:
            event.send()
        else:
            return event

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
    
    def setSubject(self, subject, event=None):
        if subject == self.__subject:
            return event        
        notify = event is None
        event = event or patterns.Event()
        self.__subject = subject
        event = self.subjectChangedEvent(event)
        if notify:
            event.send()
        else:
            return event
        
    def subjectChangedEvent(self, event):
        event.addSource(self, self.subject(), type=self.subjectChangedEventType())
        return event
    
    @classmethod    
    def subjectChangedEventType(class_):
        return '%s.subject'%class_
    
    # Description:
    
    def description(self):
        return self.__description
    
    def setDescription(self, description, event=None):
        if description == self.__description:
            return event
        notify = event is None
        event = event or patterns.Event()
        self.__description = description
        event = self.descriptionChangedEvent(event)
        if notify:
            event.send()
        else:
            return event
        
    def descriptionChangedEvent(self, event):
        event.addSource(self, self.description(), 
                        type=self.descriptionChangedEventType())
        return event
            
    @classmethod    
    def descriptionChangedEventType(class_):
        return '%s.description'%class_
    
    # Color:
    
    def setColor(self, color, event=None):
        if color == self.__color:
            return event
        notify = event is None
        event = event or patterns.Event()
        self.__color = color
        event = self.colorChangedEvent(event)
        if notify:
            event.send()
        else:
            return event
        
    def color(self, recursive=False):
        # The 'recursive' argument isn't actually used here, but some
        # code assumes composite objects where there aren't. This is
        # the simplest workaround.
        return self.__color

    @classmethod
    def colorChangedEventType(class_):
        return '%s.color'%class_
    
    def colorChangedEvent(self, event):
        event.addSource(self, self.color(), type=self.colorChangedEventType())
        return event
        
    # Event types:
    
    @classmethod
    def modificationEventTypes(class_):
        try:
            eventTypes = super(Object, class_).modificationEventTypes()
        except AttributeError:
            eventTypes = []
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
    
    def expand(self, expand=True, context='None', event=None):
        ''' Expands (or collapses) the composite object in the specified 
            context. ''' 
        if expand == self.isExpanded(context):
            return event
        notify = event is None
        event = event or patterns.Event()
        if expand:
            self.__expandedContexts.add(context)
        else:
            self.__expandedContexts.discard(context)
        event = self.expansionChangedEvent(event)
        if notify:
            event.send()
        else:
            return event

    @classmethod
    def expansionChangedEventType(class_):
        return '%s.expanded'%class_

    def expansionChangedEvent(self, event):
        event.addSource(self, type=self.expansionChangedEventType())
        return event
    
    # Color:
        
    def color(self, recursive=True):
        myColor = super(CompositeObject, self).color()
        if not myColor and recursive and self.parent():
            return self.parent().color()
        else:
            return myColor
                
    def colorChangedEvent(self, event):
        event = super(CompositeObject, self).colorChangedEvent(event)
        children = self.childrenWithoutOwnColor()
        color = self.color(recursive=False)
        for child in children:
            event.addSource(child, color, type=child.colorChangedEventType())
        return event

    def childrenWithoutOwnColor(self, parent=None):
        parent = parent or self
        children = []
        for child in parent.children():
            if child.color(recursive=False) is None:
                children.extend([child] + self.childrenWithoutOwnColor(child))
        return children

    # Event types:

    @classmethod
    def modificationEventTypes(class_):
        return super(CompositeObject, class_).modificationEventTypes() + \
            [class_.expansionChangedEventType()]

    # Override SynchronizedObject methods to also mark child objects

    def markDeleted(self, event=None):
        notify = event is None
        event = event or patterns.Event()
        event = super(CompositeObject, self).markDeleted(event)
        for child in self.children():
            event = child.markDeleted(event)
        if notify:
            event.send()
        else:
            return event
            
    def markNew(self, event=None):
        notify = event is None
        event = event or patterns.Event()
        event = super(CompositeObject, self).markNew(event)
        for child in self.children():
            event = child.markNew(event)
        if notify:
            event.send()
        else:
            return event

    def markDirty(self, force=False, event=None):
        notify = event is None
        event = event or patterns.Event()
        event = super(CompositeObject, self).markDirty(force, event)
        for child in self.children():
            event = child.markDirty(force, event)
        if notify:
            event.send()
        else:
            return event
            
    def cleanDirty(self, event=None):
        notify = event is None
        event = event or patterns.Event()
        event = super(CompositeObject, self).cleanDirty(event)
        for child in self.children():
            event = child.cleanDirty(event)
        if notify:
            event.send()
        else:
            return event

