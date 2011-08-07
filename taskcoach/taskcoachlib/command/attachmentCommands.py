# -*- coding: utf-8 -*-

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

from taskcoachlib import patterns
from taskcoachlib.i18n import _
from taskcoachlib.domain import attachment
import base, noteCommands


class NewAttachmentCommand(base.NewItemCommand):
    singular_name = _('New attachment')
    
    def __init__(self, *args, **kwargs):
        subject = kwargs.pop('subject', _('New attachment'))
        description = kwargs.pop('description', '')
        location = kwargs.pop('location', '')
        super(NewAttachmentCommand, self).__init__(*args, **kwargs)
        self.items = self.attachments = self.createNewAttachments(subject=subject,
                          description=description, location=location)

    def createNewAttachments(self, **kwargs):
        return [attachment.FileAttachment(**kwargs)]


class DeleteAttachmentCommand(base.DeleteCommand):
    plural_name = _('Delete attachments')
    singular_name = _('Delete attachment "%s"')


class AddAttachmentNoteCommand(noteCommands.AddNoteCommand):
    plural_name = _('Add note to attachments')
    
    
class EditAttachmentLocationCommand(base.BaseCommand):
    plural_name = _('Edit location of attachments')
    singular_name = _('Edit attachment "%s" location')

    def __init__(self, *args, **kwargs):
        self.__newLocation = kwargs.pop('location')
        super(EditAttachmentLocationCommand, self).__init__(*args, **kwargs)
        self.__oldLocations = [item.location() for item in self.items]
    
    @patterns.eventSource
    def do_command(self, event=None):
        for item in self.items:
            item.setLocation(self.__newLocation, event=event)
            
    @patterns.eventSource
    def undo_command(self, event=None):
        for item, oldLocation in zip(self.items, self.__oldLocations):
            item.setLocation(oldLocation, event=event)
            
    def redo_command(self):
        self.do_command()


class AddAttachmentCommand(base.BaseCommand):
    plural_name = _('Add attachment')
    singular_name = _('Add attachment to "%s"')
    
    def __init__(self, *args, **kwargs):
        self.__attachments = kwargs.get('attachments', 
                                        [attachment.FileAttachment('', subject=_('New attachment'))])
        super(AddAttachmentCommand, self).__init__(*args, **kwargs)
        self.owners = self.items
        self.items = self.__attachments
        
    @patterns.eventSource
    def addAttachments(self, event=None):
        kwargs = dict(event=event)
        for owner in self.owners:
            owner.addAttachments(*self.__attachments, **kwargs) # pylint: disable-msg=W0142

    @patterns.eventSource
    def removeAttachments(self, event=None):
        kwargs = dict(event=event)
        for owner in self.owners:
            owner.removeAttachments(*self.__attachments, **kwargs) # pylint: disable-msg=W0142
                         
    def do_command(self):
        self.addAttachments()
        
    def undo_command(self):
        self.removeAttachments()

    def redo_command(self):
        self.addAttachments()


class RemoveAttachmentCommand(base.BaseCommand):
    plural_name = _('Remove attachment')
    singular_name = _('Remove attachment to "%s"')
    
    def __init__(self, *args, **kwargs):
        self.__attachments = kwargs.pop('attachments')
        super(RemoveAttachmentCommand, self).__init__(*args, **kwargs)

    @patterns.eventSource
    def addAttachments(self, event=None):
        kwargs = dict(event=event)
        for item in self.items:
            item.addAttachments(*self.__attachments, **kwargs) # pylint: disable-msg=W0142
        
    @patterns.eventSource
    def removeAttachments(self, event=None):
        kwargs = dict(event=event)
        for item in self.items:
            item.removeAttachments(*self.__attachments, **kwargs) # pylint: disable-msg=W0142
                
    def do_command(self):
        self.removeAttachments()
        
    def undo_command(self):
        self.addAttachments()

    def redo_command(self):
        self.removeAttachments()