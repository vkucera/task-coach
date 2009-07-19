'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2009 Frank Niessink <frank@niessink.com>

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

from taskcoachlib.domain import base
from taskcoachlib.i18n import _
from taskcoachlib import patterns


class NoteContainer(base.Collection):
    newItemMenuText = _('New note...')
    newItemHelpText =  _('Insert a new note')
    editItemMenuText = _('Edit note...')
    editItemHelpText = _('Edit the selected notes')
    deleteItemMenuText = _('Delete note')
    deleteItemHelpText = _('Delete the selected notes')
    newSubItemMenuText = _('New subnote...')
    newSubItemHelpText = _('Insert a new subnote')

    def extend(self, notes, event=None):
        notify = event is None
        event = event or patterns.Event()
        event = super(NoteContainer, self).extend(notes, event)
        for note in self._compositesAndAllChildren(notes):
            for category in note.categories():
                event = category.addCategorizable(note, event=event)
        if notify:
            event.send()
        else:
            return event
                
    def removeItems(self, notes, event=None):
        notify = event is None
        event = event or patterns.Event()
        event = super(NoteContainer, self).removeItems(notes, event)
        for note in self._compositesAndAllChildren(notes):
            for category in note.categories():
                category.removeCategorizable(note, event=event)
        if notify:
            event.send()
        else:
            return event
                
