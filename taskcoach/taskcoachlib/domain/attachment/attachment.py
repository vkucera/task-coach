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

import os, shutil, tempfile
from taskcoachlib.thirdparty import desktop
from taskcoachlib.mailer import readMail, openMail
from taskcoachlib.i18n import _


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

        if pth2 == os.path.sep:
            return pth1[1:]

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


class Attachment(object):
    ''' Abstract base class for attachments. '''
    type_ = None

    attdir =  None # This is filled in before saving or reading by
                   # xml.writer and xml.reader
        
    def open(self, workingDir=None):
        raise NotImplementedError

    def data(self):
        raise NotImplementedError

    def setDescription(self, descr):
        raise NotImplementedError

    def copy(self):
        return self.__class__(**self.__getcopystate__())

    def __getcopystate__(self):
        return dict(location=self.data())


class FileAttachment(Attachment):
    type_ = 'file'

    def __init__(self, location='', description=None, **kwargs):
        super(FileAttachment, self).__init__(**kwargs)
        # FIXME: description is ignored
        self.filename = location

    def open(self, workingDir=None, openAttachment=desktop.open):
        if workingDir is not None and not os.path.isabs(self.filename):
            path = os.path.join(workingDir, self.filename)
        else:
            path = self.filename

        openAttachment(os.path.normpath(path))

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

    def __init__(self, location='', description=None, **kwargs):
        super(URIAttachment, self).__init__(**kwargs)
        # FIXME: description is ignored
        self.uri = location

    def open(self, workingDir=None):
        desktop.open(self.uri)

    def setDescription(self, description):
        self.uri = description

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

    def __init__(self, location='', description=None, **kwargs):
        super(MailAttachment, self).__init__(**kwargs)

        if os.path.isabs(location):
            self.filename = os.path.normpath(location)
        else:
            self.filename = os.path.normpath(os.path.join(self.attdir, location))

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


def AttachmentFactory(location, description=None, type_=None):
    if type_ is None:
        if location.startswith('URI:'):
            return URIAttachment(location[4:])
        elif location.startswith('FILE:'):
            return FileAttachment(location[5:])
        elif location.startswith('MAIL:'):
            return MailAttachment(location[5:])

        return FileAttachment(location)

    try:
        return { 'file': FileAttachment,
                 'uri': URIAttachment,
                 'mail': MailAttachment }[type_](location, description)
    except KeyError:
        raise TypeError, 'Unknown attachment type: %s' % type_
