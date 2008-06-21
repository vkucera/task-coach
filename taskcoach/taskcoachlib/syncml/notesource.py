
from taskcoachlib.domain.note import Note
from taskcoachlib.syncml.basesource import BaseSource

from taskcoachlib.i18n import _

import wx

class NoteSource(BaseSource):
    CONFLICT_SUBJECT       = 0x01
    CONFLICT_DESCRIPTION   = 0x02

    def updateItemProperties(self, item, note):
        item.data = (note.subject() + '\n' + note.description()).encode('UTF-8')
        item.dataType = 'text/plain'

    def compareItemProperties(self, local, remote):
        result = 0

        if local.subject() != remote.subject():
            result |= self.CONFLICT_SUBJECT
        if local.description() != remote.description():
            result |= self.CONFLICT_DESCRIPTION

        return result

    def _parseObject(self, item):
        data = item.data.decode('UTF-8')
        idx = data.find('\n')
        if idx == -1:
            subject = data
            description = u''
        else:
            subject = data[:idx].rstrip('\r')
            description = data[idx+1:]

        return Note(subject=subject, description=description)

    def doUpdateItem(self, note, local):
        local.setSubject(note.subject())
        local.setDescription(note.description())

        return 200

    def doResolveConflict(self, note, local, result):
        resolved = self.callback.resolveNoteConflict(result, local, note)

        if resolved.has_key('subject'):
            local.setSubject(resolved['subject'])
        if resolved.has_key('description'):
            local.setDescription(resolved['description'])

        return local

    def objectRemovedOnServer(self, note):
        return wx.MessageBox(_('Note "%s" has been deleted on server,\n') % note.subject() + \
                             _('but locally modified. Should I keep the local version ?'),
                             _('Synchronization conflict'), wx.YES_NO) == wx.YES

    def objectRemovedOnClient(self, note):
        return wx.MessageBox(_('Note "%s" has been locally deleted,\n') % note.subject() + \
                             _('but modified on server. Should I keep the remote version ?'),
                             _('Synchronization conflict'), wx.YES_NO) == wx.YES
