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

import test
from taskcoachlib import patterns
from taskcoachlib.domain import note


class NoteTest(test.TestCase):
    def setUp(self):
        self.note = note.Note()
        self.child = note.Note()
        self.events = []
        
    def onEvent(self, event):
        self.events.append(event)
        
    def testDefaultSubject(self):
        self.assertEqual('', self.note.subject())
        
    def testGivenSubject(self):
        aNote = note.Note(subject='Note')
        self.assertEqual('Note', aNote.subject())
        
    def testSetSubject(self):
        self.note.setSubject('Note')
        self.assertEqual('Note', self.note.subject())
        
    def testSubjectChangeNotification(self):
        patterns.Publisher().registerObserver(self.onEvent, 
            self.note.subjectChangedEventType())
        self.note.setSubject('Note')
        self.assertEqual(patterns.Event(self.note, 
            self.note.subjectChangedEventType(), 'Note'), self.events[0])
        
    def testDefaultDescription(self):
        self.assertEqual('', self.note.description())
        
    def testGivenDescription(self):
        aNote = note.Note(description='Description')
        self.assertEqual('Description', aNote.description())
        
    def testSetDescription(self):
        self.note.setDescription('Description')
        self.assertEqual('Description', self.note.description())
        
    def testDescriptionChangeNotification(self):
        patterns.Publisher().registerObserver(self.onEvent, 
            self.note.descriptionChangedEventType())
        self.note.setDescription('Description')
        self.assertEqual(patterns.Event(self.note, 
            self.note.descriptionChangedEventType(), 'Description'), 
            self.events[0])
        
    def testAddChild(self):
        self.note.addChild(self.child)
        self.assertEqual([self.child], self.note.children())

    def testRemoveChild(self):
        self.note.addChild(self.child)
        self.note.removeChild(self.child)
        self.assertEqual([], self.note.children())
        
    def testAddChildNotification(self):
        patterns.Publisher().registerObserver(self.onEvent, 
            note.Note.addChildEventType())
        self.note.addChild(self.child)
        self.assertEqual(patterns.Event(self.note, 
            note.Note.addChildEventType(), self.child), self.events[0])
        
    def testRemoveChildNotification(self):
        patterns.Publisher().registerObserver(self.onEvent, 
            note.Note.removeChildEventType())
        self.note.addChild(self.child)
        self.note.removeChild(self.child)
        self.assertEqual(patterns.Event(self.note, 
            note.Note.removeChildEventType(), self.child), self.events[0])
        
    def testNewChild(self):
        child = self.note.newChild(subject='child')
        self.assertEqual('child', child.subject())
        
    def testGetState(self):
        self.assertEqual(dict(id=self.note.id(), subject='', description='', parent=None,
            categories=set(), children=self.note.children(),
            status=self.note.getStatus()), self.note.__getstate__())
        
    def testSetState(self):
        self.note.__setstate__(dict(id='id', subject='new', description='new', 
            parent=None, children=[], status=42))
        self.assertEqual('new', self.note.description())

