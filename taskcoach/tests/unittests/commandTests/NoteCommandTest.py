import test, command, patterns
from unittests import asserts
from CommandTestCase import CommandTestCase
from domain import note


class NoteCommandTestCase(CommandTestCase, asserts.CommandAsserts):
    def setUp(self):
        self.notes = note.NoteContainer()
        

class NewNoteCommandTest(NoteCommandTestCase):
    def new(self):
        newNoteCommand = command.NewNoteCommand(self.notes)
        newNote = newNoteCommand.items[0]
        newNoteCommand.do()
        return newNote
        
    def testNewNote(self):
        newNote = self.new()
        self.assertDoUndoRedo(
            lambda: self.assertEqual([newNote], self.notes),
            lambda: self.assertEqual([], self.notes))
        

class NewSubNoteCommandTest(NoteCommandTestCase):
    def setUp(self):
        super(NewSubNoteCommandTest, self).setUp()
        self.note = note.Note('Note')
        self.notes.append(self.note)
        
    def newSubNote(self, notes=None):
        newSubNote = command.NewSubNoteCommand(self.notes, notes or [])
        newSubNote.do()

    def testNewSubNote_WithoutSelection(self):
        self.newSubNote()
        self.assertDoUndoRedo(lambda: self.assertEqual([self.note], 
                                                       self.notes))

    def testNewSubNote(self):
        self.newSubNote([self.note])
        newSubNote = self.note.children()[0]
        self.assertDoUndoRedo(lambda: self.assertEqual([newSubNote], 
                                                       self.note.children()),
            lambda: self.assertEqual([self.note], self.notes))


class EditNoteCommandTest(NoteCommandTestCase):
    def setUp(self):
        super(EditNoteCommandTest, self).setUp()
        self.note = note.Note(subject='Note')
        self.notes.append(self.note)
        
    def editNote(self, notes=None):
        notes = notes or []
        editNote = command.EditNoteCommand(self.notes, notes)
        for note in notes:
            note.setSubject('new')
        editNote.do()
        
    def testEditNote_WithoutSelection(self):
        self.editNote()
        self.assertDoUndoRedo(lambda: self.assertEqual([self.note], 
                                                       self.notes))
        
    def testEditNote_Subject(self):
        self.editNote([self.note])
        self.assertDoUndoRedo(lambda: self.assertEqual('new', self.note.subject()),
            lambda: self.assertEqual('Note', self.note.subject()))


class DragAndDropNoteCommand(NoteCommandTestCase):
    def setUp(self):
        super(DragAndDropNoteCommand, self).setUp()
        self.parent = note.Note('parent')
        self.child = note.Note('child')
        self.grandchild = note.Note('grandchild')
        self.parent.addChild(self.child)
        self.child.addChild(self.grandchild)
        self.notes.extend([self.parent, self.child])
    
    def dragAndDrop(self, dropTarget, notes=None):
        command.DragAndDropNoteCommand(self.notes, notes or [], 
                                       drop=dropTarget).do()
                                       
    def testCannotDropOnParent(self):
        self.dragAndDrop([self.parent], [self.child])
        self.failIf(patterns.CommandHistory().hasHistory())
        
    def testCannotDropOnChild(self):
        self.dragAndDrop([self.child], [self.parent])
        self.failIf(patterns.CommandHistory().hasHistory())
        
    def testCannotDropOnGrandchild(self):
        self.dragAndDrop([self.grandchild], [self.parent])
        self.failIf(patterns.CommandHistory().hasHistory())

    def testDropAsRootTask(self):
        self.dragAndDrop([], [self.grandchild])
        self.assertDoUndoRedo(lambda: self.assertEqual(None, 
            self.grandchild.parent()), lambda:
            self.assertEqual(self.child, self.grandchild.parent()))