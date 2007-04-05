import base
from i18n import _
from domain import note

class NewNoteCommand(base.BaseCommand):
    def name(self):
        return _('New note')

    def __init__(self, *args, **kwargs):
        super(NewNoteCommand, self).__init__(*args, **kwargs)
        self.items = self.createNewNotes()
        
    def createNewNotes(self):
        return [note.Note(subject=_('New note'))]
        
    def do_command(self):
        self.list.extend(self.items)

    def undo_command(self):
        self.list.removeItems(self.items)

    def redo_command(self):
        self.list.extend(self.items)


class NewSubNoteCommand(NewNoteCommand):
    def name(self):
        return _('New subnote')
            
    def createNewNotes(self):
        return [parent.newChild(subject=_('New subnote')) for parent in self.items]


class EditNoteCommand(base.EditCommand):
    def name(self):
        return _('Edit note')
    
    def getItemsToSave(self):
        return self.items
    
    
class DragAndDropNoteCommand(base.DragAndDropCommand):
    def name(self):
        return _('Drag and drop note')
