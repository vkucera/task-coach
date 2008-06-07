# -*- coding: utf-8 -*-

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
        self.__frozenStatus = kwargs.pop('frozenStatus', False)
        super(SynchronizedObject, self).__init__(*args, **kwargs)

    def __getstate__(self):
        try:
            state = super(SynchronizedObject, self).__getstate__()
        except AttributeError:
            pass

        state['status'] = self.__status
        return state

    def __setstate__(self, state):
        try:
            super(SynchronizedObject, self).__setstate__(state)
        except AttributeError:
            pass

        self.__status = state['status']

    def freezeStatus(self):
        self.__frozenStatus = True

    def thawStatus(self):
        self.__frozenStatus = False

    def getStatus(self):
        return self.__status

    def markDirty(self):
        if self.__status == self.STATUS_NONE and not self.__frozenStatus:
            self.__status = self.STATUS_CHANGED

    def markDeleted(self):
        if not self.__frozenStatus:
            self.__status = self.STATUS_DELETED
            self.notifyObservers(patterns.Event(self, 
                'object.markdeleted', self.__status))

    def cleanDirty(self):
        if not self.__frozenStatus:
            self.__status = self.STATUS_NONE

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
                          description=self.__description))
        return state
    
    def __setstate__(self, state):
        try:
            super(Object, self).__setstate__(state)
        except AttributeError:
            pass
        self.setId(state['id'])
        self.setSubject(state['subject'])
        self.setDescription(state['description'])

    def copy(self):
        state = self.__getstate__()
        del state['id'] # Don't copy the id
        return self.__class__(**state)
    
    def id(self):
        return self.__id
    
    def setId(self, id):
        self.__id = id
    
    def subject(self):
        return self.__subject
    
    def setSubject(self, subject):
        if subject != self.__subject:
            self.__subject = subject
            self.notifyObservers(patterns.Event(self, 
                self.subjectChangedEventType(), subject))
            return True # Subject was changed
        else:
            return False # Subject was not changed
    
    @classmethod    
    def subjectChangedEventType(class_):
        return '%s.subject'%class_
    
    def description(self):
        return self.__description
    
    def setDescription(self, description):
        if description != self.__description:
            self.__description = description
            self.notifyObservers(patterns.Event(self, 
                    self.descriptionChangedEventType(), description))
            return True # Description was changed
        else:
            return False # Description was not changed
        
    @classmethod    
    def descriptionChangedEventType(class_):
        return '%s.description'%class_


class CompositeObject(Object, patterns.ObservableComposite):
    def __init__(self, *args, **kwargs):
        self.__expanded = kwargs.pop('expand', False)
        super(CompositeObject, self).__init__(*args, **kwargs)
        
    def subject(self, recursive=False):
        subject = super(CompositeObject, self).subject()
        if recursive and self.parent():
            subject = u'%s -> %s'%(self.parent().subject(recursive=True), subject)
        return subject
        
    def description(self, recursive=False):
        # Allow for the recursive flag, but ignore it
        return super(CompositeObject, self).description()
    
    def isExpanded(self):
        return self.__expanded
    
    def expand(self, expand=True):
        self.__expanded = expand
        

