import patterns
from i18n import _

class NoteContainer(patterns.CompositeSet):
    newItemMenuText = _('New note...')
    newItemHelpText =  _('Insert a new note')
    editItemMenuText = _('Edit note...')
    editItemHelpText = _('Edit the selected notes')
    deleteItemMenuText = _('Delete note')
    deleteItemHelpText = _('Delete the selected notes')
    newSubItemMenuText = _('New subnote...')
    newSubItemHelpText = _('Insert a new subnote')