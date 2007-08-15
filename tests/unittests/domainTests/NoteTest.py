import test, patterns
from domain import note


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
        self.assertEqual(dict(subject='', description='', parent=None,
            children=self.note.children()), self.note.__getstate__())
        
    def testSetState(self):
        self.note.__setstate__(dict(subject='new', description='new', 
            parent=None, children=[]))
        self.assertEqual('new', self.note.description())
        
