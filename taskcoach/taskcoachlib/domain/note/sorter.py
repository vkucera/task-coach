import patterns
import note

class NoteSorter(patterns.ListDecorator):    
    def __init__(self, *args, **kwargs):
        super(NoteSorter, self).__init__(*args, **kwargs)
        patterns.Publisher().registerObserver(self.reset, 
            note.Note.subjectChangedEventType())
        
    def sortEventType(self):
        return '%s(%s).sorted'%(self.__class__, id(self))
    
    def extendSelf(self, notes):
        super(NoteSorter, self).extendSelf(notes)
        self.reset()
    
    def rootItems(self):
        return [note for note in self if note.parent() is None]

    # We don't override removeItemsFromSelf because there is no need to 
    # call self.reset() when items are removed since after removing items
    # the remaining items are still in the right order.

    def reset(self, event=None):
        oldSelf = self[:]
        self.sort(key=lambda note: note.subject(), reverse=False)
        if self != oldSelf:
            patterns.Publisher().notifyObservers(patterns.Event(self, 
                self.sortEventType()))


