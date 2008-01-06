# -*- coding: utf-8 -*-

import patterns, time
from domain import date

    
class Object(patterns.Observable):
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
            subject = u'%s → %s'%(self.parent().subject(recursive=True), subject)
        return subject
        
    def description(self, recursive=False):
        # Allow for the recursive flag, but ignore it
        return super(CompositeObject, self).description()
    
    def isExpanded(self):
        return self.__expanded
    
    def expand(self, expand=True):
        self.__expanded = expand
        
    