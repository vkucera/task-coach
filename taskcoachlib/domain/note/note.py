import patterns

class Note(patterns.ObservableComposite):
    def __init__(self, subject='', description='', *args, **kwargs):
        super(Note, self).__init__(*args, **kwargs)
        self.__subject = subject
        self.__description = description
        
    def subject(self):
        return self.__subject
    
    def setSubject(self, subject):
        self.__subject = subject
        patterns.Publisher().notifyObservers(patterns.Event(self, 
            self.subjectChangedEventType(), subject))

    @classmethod
    def subjectChangedEventType(class_):
        return 'note.subject'
        
    def description(self):
        return self.__description
    
    def setDescription(self, description):
        self.__description = description
        patterns.Publisher().notifyObservers(patterns.Event(self, 
            'note.description', description))


    def __getstate__(self):
        state = super(Note, self).__getstate__()
        state.update(dict(subject=self.subject(), 
            description=self.description()))
        return state
    
    def __setstate__(self, state):
        self.setSubject(state.pop('subject'))
        self.setDescription(state.pop('description'))
        super(Note, self).__setstate__(state)
        