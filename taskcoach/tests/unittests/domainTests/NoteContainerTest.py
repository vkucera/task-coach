import test
from domain import note

class NoteContainerTest(test.TestCase):
    def setUp(self):
        self.container = note.NoteContainer()
        self.note = note.Note()
        
    def testAddContainer(self):
        self.container.append(self.note)
        self.assertEqual([self.note], self.container)