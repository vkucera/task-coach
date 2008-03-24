'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>
Copyright (C) 2007-2008 Jerome Laheurte <fraca7@free.fr>

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
from patterns import Observer, Observable, Event
from i18n import _

import os, shutil, tempfile

def getRelativePath(path, base=os.getcwd()):
    """Tries to guess the relative version of 'path' from 'base'. If
    not possible, return absolute 'path'. Both 'path' and 'base' must
    be absolute."""

    path = os.path.realpath(os.path.normpath(path))
    base = os.path.realpath(os.path.normpath(base))

    drv1, pth1 = os.path.splitdrive(path)
    drv2, pth2 = os.path.splitdrive(base)

    # No relative path is possible if the two are on different drives.
    if drv1 != drv2:
        return path

    if pth1.startswith(pth2):
        if pth1 == pth2:
            return ''
        return pth1[len(pth2) + 1:]

    pth1 = pth1.split(os.path.sep)
    pth2 = pth2.split(os.path.sep)

    while pth1 and pth2 and pth1[0] == pth2[0]:
        pth1.pop(0)
        pth2.pop(0)

    while pth2:
        pth1.insert(0, '..')
        pth2.pop(0)

    return os.path.join(*pth1)


class Attachment(Observer, Observable):
    type_ = None

    def __init__(self, *args, **kwargs):
        super(Attachment, self).__init__(*args, **kwargs)

    def open(self, workingDir=None):
        raise NotImplementedError

    def data(self):
        raise NotImplementedError

    def setDescription(self, descr):
        raise NotImplementedError

class FileAttachment(Attachment):
    type_ = 'file'

    def __init__(self, filename, description=None, **kwargs):
        super(FileAttachment, self).__init__(**kwargs)

        self.filename = filename

        self.registerObserver(self.onBaseChange, 'before.file.attachmentbase')

    def onBaseChange(self, evt):
        if os.path.isabs(self.filename):
            oldpath = self.filename
        else:
            oldpath = os.path.join(evt.source().get('file', 'attachmentbase'),
                                   self.filename)

        if os.path.exists(oldpath):
            if evt.value():
                self.filename = getRelativePath(oldpath, evt.value())
            else:
                self.filename = oldpath

            self.notifyObservers(Event(self, 'attachment.changed'))

    def open(self, workingDir=None):
        if workingDir is not None and not os.path.isabs(self.filename):
            path = os.path.join(workingDir, self.filename)
        else:
            path = self.filename

        desktop.open(os.path.normpath(path))

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

    def __init__(self, uri, description=None, **kwargs):
        super(URIAttachment, self).__init__(**kwargs)

        self.uri = uri

    def open(self, workingDir=None):
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

    def __init__(self, filename, description=None, **kwargs):
        super(MailAttachment, self).__init__(**kwargs)

        if os.path.isabs(filename):
            self.filename = os.path.normpath(filename)
        else:
            self.filename = os.path.normpath(os.path.join(self.attdir, filename))

        if description is None:
            self.description, unused = readMail(self.filename)
        else:
            self.description = description

    def open(self, workingDir=None):
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
