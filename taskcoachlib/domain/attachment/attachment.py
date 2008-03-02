'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>
Copyright (C) 2007 Jerome Laheurte <fraca7@free.fr>

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

from thirdparty import desktop
from mailer import readMail, openMail
from i18n import _

import os, shutil, tempfile

class Attachment(object):
    type_ = None

    def open(self):
        raise NotImplementedError

    def data(self):
        raise NotImplementedError

    def setDescription(self, descr):
        raise NotImplementedError

class FileAttachment(Attachment):
    type_ = 'file'

    def __init__(self, filename, description=None):
        self.filename = filename

    def open(self):
        desktop.open(os.path.normpath(self.filename))

    def setDescription(self, descr):
        self.filename = descr

    def data(self):
        return self.filename

    def __unicode__(self):
        return unicode(self.filename)

    def __cmp__(self, other):
        try:
            return cmp(self.filename, other.filename)
        except AttributeError:
            return 1

class URIAttachment(Attachment):
    type_ = 'uri'

    def __init__(self, uri, description=None):
        self.uri = uri

    def open(self):
        desktop.open(self.uri)

    def setDescription(self, descr):
        self.uri = descr

    def data(self):
        return self.uri

    def __unicode__(self):
        return self.uri

    def __cmp__(self, other):
        try:
            return cmp(self.uri, other.uri)
        except AttributeError:
            return 1

class MailAttachment(Attachment):
    type_ = 'mail'

    attdir =  None #  This is  filled in before  saving or  reading by
                   # xml.writer and xml.reader

    def __init__(self, filename, description=None):
        if os.path.isabs(filename):
            self.filename = os.path.normpath(filename)
        else:
            self.filename = os.path.normpath(os.path.join(self.attdir, filename))

        if description is None:
            self.description, unused = readMail(self.filename)
        else:
            self.description = description

    def open(self):
        openMail(self.filename)

    def setDescription(self, description):
        self.description = description

    def data(self):
        path, name = os.path.split(self.filename)

        if self.attdir is not None:
            if path != self.attdir:
                try:
                    os.makedirs(self.attdir)
                except OSError:
                    pass

                fd, filename = tempfile.mkstemp(suffix='.eml', dir=self.attdir)
                os.close(fd)
                shutil.move(self.filename, filename)
                self.filename = os.path.normpath(filename)
                path, name = os.path.split(self.filename)

        return name

    def __unicode__(self):
        return self.description

    def __cmp__(self, other):
        try:
            return cmp(self.filename, other.filename)
        except AttributeError:
            return 1


#==============================================================================
#

def AttachmentFactory(data, description=None, type_=None):
    if type_ is None:
        if data.startswith('URI:'):
            return URIAttachment(data[4:])
        elif data.startswith('FILE:'):
            return FileAttachment(data[5:])
        elif data.startswith('MAIL:'):
            return MailAttachment(data[5:])

        return FileAttachment(data)

    try:
        return { 'file': FileAttachment,
                 'uri': URIAttachment,
                 'mail': MailAttachment }[type_](data, description)
    except KeyError:
        raise TypeError, 'Unknown attachment type: %s' % type_
