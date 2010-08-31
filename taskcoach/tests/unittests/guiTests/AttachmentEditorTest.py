'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2010 Task Coach developers <developers@taskcoach.org>

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

import test, wx
from taskcoachlib import gui, command, config, persistence
from taskcoachlib.domain import note, attachment


class DummyEvent(object):
    def Skip(self):
        pass


class AttachmentEditorTestCase(test.wxTestCase):
    def setUp(self):
        super(AttachmentEditorTestCase, self).setUp()
        self.settings = config.Settings(load=False)
        self.taskFile = persistence.TaskFile()
        self.attachments = attachment.AttachmentList()
        self.attachments.extend(self.createAttachments())
        self.editor = self.createEditor()
        
    def createEditor(self):
        return gui.dialog.editor.AttachmentEditor(self.frame, self.createCommand(),
            self.settings, self.attachments, self.taskFile, raiseDialog=False)


    def createCommand(self):
        raise NotImplementedError # pragma: no cover
    
    def createAttachments(self):
        return []

    def setSubject(self, newSubject):
        page = self.editor._interior[0]
        page._subjectEntry.SetFocus()
        page.setSubject(newSubject)
        if '__WXGTK__' == wx.Platform:
            page.onLeavingSubjectEntry(DummyEvent())
        else:
            page._descriptionEntry.SetFocus()
        
    def setDescription(self, newDescription):
        page = self.editor._interior[0]
        page._descriptionEntry.SetFocus()
        page.setDescription(newDescription)
        if '__WXGTK__' == wx.Platform:
            page.onLeavingDescriptionEntry(DummyEvent())
        else:
            page._subjectEntry.SetFocus()

        
class NewAttachmentTest(AttachmentEditorTestCase):
    def createCommand(self):
        newAttachmentCommand = command.NewAttachmentCommand(self.attachments)
        self.attachment = newAttachmentCommand.items[0] # pylint: disable-msg=W0201
        return newAttachmentCommand

    def testCreate(self):
        # pylint: disable-msg=W0212
        self.assertEqual('New attachment', self.editor._interior[0]._subjectEntry.GetValue())

    def testEditSubject(self):
        self.setSubject('Done')
        self.assertEqual('Done', self.attachment.subject())

    def testEditDescription(self):
        self.setDescription('Description')
        self.assertEqual('Description', self.attachment.description())
        
    def testAddNote(self):
        self.editor._interior[1].notes.append(note.Note(subject='New note'))
        self.editor.ok()
        self.assertEqual(1, len(self.attachment.notes()))
