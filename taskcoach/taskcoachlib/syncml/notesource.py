'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2011 Task Coach developers <developers@taskcoach.org>

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

from taskcoachlib.domain.note import Note
from taskcoachlib.domain.category import Category
from taskcoachlib.syncml.basesource import BaseSource
from taskcoachlib.persistence.icalendar import ical

from taskcoachlib.i18n import _

import wx, inspect

class NoteSource(BaseSource):
    CONFLICT_SUBJECT       = 0x01
    CONFLICT_DESCRIPTION   = 0x02

    def __init__(self, callback, noteList, categoryList, *args, **kwargs):
        super(NoteSource, self).__init__(callback, noteList, *args, **kwargs)

        self.categoryList = categoryList

    def updateItemProperties(self, item, note):
        item.dataType = 'text/x-vnote:1.1'
        item.data = ical.VNoteFromNote(note)

    def compareItemProperties(self, local, remote):
        result = 0

        if local.subject() != remote.subject():
            result |= self.CONFLICT_SUBJECT
        if local.description() != remote.description():
            result |= self.CONFLICT_DESCRIPTION

        return result

    def _parseObject(self, item):
        parser = ical.VCalendarParser()
        parser.parse(map(lambda x: x.rstrip('\r'), item.data.strip().split('\n')))
        categories = parser.notes[0].pop('categories', [])

        kwargs = dict([(k, v) for k, v in parser.notes[0].items() if k in ['subject', 'description', 'id']])
        note = Note(**kwargs)

        for category in categories:
            categoryObject = self.categoryList.findCategoryByName(category)
            if categoryObject is None:
                categoryObject = Category(category)
                self.categoryList.extend([categoryObject])
            note.addCategory(categoryObject)

        return note

    def doUpdateItem(self, note, local):
        local.setSubject(note.subject())
        local.setDescription(note.description())

        for category in local.categories():
            category.removeCategorizable(local)

        local.setCategories(note.categories())

        for category in local.categories():
            category.addCategorizable(local)

        return 200

    def doResolveConflict(self, note, local, result):
        resolved = self.callback.resolveNoteConflict(result, local, note)

        if resolved.has_key('subject'):
            local.setSubject(resolved['subject'])
        if resolved.has_key('description'):
            local.setDescription(resolved['description'])

        if resolved.has_key('categories'):
            for category in local.categories().copy():
                category.removeCategorizable(local)
                local.removeCategory(category)

            for category in resolved['categories'].split(','):
                categoryObject = self.categoryList.findCategoryByName(category)
                if categoryObject is None:
                    categoryObject = Category(category)
                    self.categoryList.extend([categoryObject])
                local.addCategory(categoryObject)

            for category in local.categories():
                category.addCategorizable(local)

        return local

    def objectRemovedOnServer(self, note):
        return wx.MessageBox(_('Note "%s" has been deleted on server,\n') % note.subject() + \
                             _('but locally modified. Should I keep the local version?'),
                             _('Synchronization conflict'), wx.YES_NO) == wx.YES

    def objectRemovedOnClient(self, note):
        return wx.MessageBox(_('Note "%s" has been locally deleted,\n') % note.subject() + \
                             _('but modified on server. Should I keep the remote version?'),
                             _('Synchronization conflict'), wx.YES_NO) == wx.YES
