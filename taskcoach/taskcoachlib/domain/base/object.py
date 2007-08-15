import patterns

    
class Object(patterns.Observable):
    def __init__(self, *args, **kwargs):
        self.__subject = kwargs.pop('subject', '')
        self.__description = kwargs.pop('description', '')
        super(Object, self).__init__(*args, **kwargs)
    
    def __getstate__(self):
        try:
            state = super(Object, self).__getstate__()
        except AttributeError:
            state = dict()
        state.update(dict(subject=self.__subject, 
                          description=self.__description))
        return state
    
    def __setstate__(self, state):
        try:
            super(Object, self).__setstate__(state)
        except AttributeError:
            pass
        self.setSubject(state['subject'])
        self.setDescription(state['description'])
    
    def copy(self):
        return self.__class__(**self.__getstate__())
    
    def subject(self):
        return self.__subject
    
    def setSubject(self, subject):
        if subject != self.__subject:
            self.__subject = subject
            self.notifyObservers(patterns.Event(self, 
                self.subjectChangedEventType(), subject))
    
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
        
    @classmethod    
    def descriptionChangedEventType(class_):
        return '%s.description'%class_
