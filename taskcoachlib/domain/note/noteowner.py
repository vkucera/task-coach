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

from taskcoachlib import patterns


class NoteOwner(patterns.Observable):
    ''' Mixin class for (other) domain objects that may contain notes. '''
    
    def __init__(self, *args, **kwargs):
        self.__notes = kwargs.pop('notes', []) 
        # NB: self.__notes is a simple list and not a NoteContainer. Maybe a 
        # NoteContainer would be a better choice, but I'm not sure at the 
        # moment.
        super(NoteOwner, self).__init__(*args, **kwargs)

    def __getstate__(self):
        ''' Return a dict, reflecting our current state. '''
        try:
            state = super(NoteOwner, self).__getstate__()
        except AttributeError:
            state = dict()
        state.update(dict(notes=self.__notes[:]))
        return state

    def __setstate__(self, state):
        ''' Update our state according to the state dict passed. '''
        try:
            super(NoteOwner, self).__setstate__(state)
        except AttributeError:
            pass
        self.setNotes(state['notes'])

    def __getcopystate__(self):
        ''' Return a dict, suitable for creating a copy. '''
        try:
            state = super(NoteOwner, self).__getcopystate__()
        except AttributeError:
            state = dict()
        state.update(dict(notes=[note.copy() for note in self.__notes]))
        return state
            
    def addNote(self, note):
        ''' Add a note and notify our observers. '''
        self.__notes.append(note)
        self.__notifyObservers()
    
    def removeNote(self, note):
        ''' Remove a note and notify our observers. '''
        self.__notes.remove(note)
        self.__notifyObservers()

    def setNotes(self, notes):
        ''' Replace all our notes and notify our observers. '''
        self.__notes = notes
        self.__notifyObservers()

    def notes(self):
        ''' Return our notes. '''
        return self.__notes
            
    @classmethod    
    def notesChangedEventType(class_):
        ''' The event type used to notify our observers about notes added or 
            removed. '''
        return '%s.note'%class_
        
    def __notifyObservers(self):
        ''' Notify our observers that notes were added or removed. '''
        self.notifyObservers(patterns.Event(self, self.notesChangedEventType(),
            *self.__notes))

