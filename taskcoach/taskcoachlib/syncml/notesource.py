
from taskcoachlib.domain.note import Note
from taskcoachlib.syncml.basesource import BaseSource

class NoteSource(BaseSource):
    def _getItem(self, ls):
        item, note = super(NoteSource, self)._getItem(ls)

        if item is not None:
            item.data = (note.subject() + '\n' + note.description()).encode('UTF-8')
            item.dataType = 'text/plain'

        return item

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

    def addItem(self, item):
        super(NoteSource, self).addItem(item)

        return 201

    def doUpdateItem(self, note, local):
        local.setDescription(note.description())

        return 200
