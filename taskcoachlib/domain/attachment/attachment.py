
from thirdparty import desktop
from mailer import thunderbird, outlook, readMail, setMailDescription
from i18n import _

import os, shutil, tempfile

class Attachment(object):
    def open(self):
        raise NotImplementedError

    def setDescription(self, descr):
        raise NotImplementedError

class FileAttachment(Attachment):
    def __init__(self, filename):
        self.filename = filename

    def open(self):
        desktop.open(os.path.normpath(self.filename))

    def setDescription(self, descr):
        self.filename = descr

    def __repr__(self):
        return 'FILE:%s' % self.filename

    def __unicode__(self):
        return unicode(self.filename)

    def __cmp__(self, other):
        try:
            return cmp(self.filename, other.filename)
        except AttributeError:
            return 1

class URIAttachment(Attachment):
    def __init__(self, uri):
        self.uri = uri

    def open(self):
        desktop.open(self.uri)

    def setDescription(self, descr):
        self.uri = descr

    def __repr__(self):
        return 'URI:%s' % self.uri

    def __unicode__(self):
        return self.uri

    def __cmp__(self, other):
        try:
            return cmp(self.uri, other.uri)
        except AttributeError:
            return 1

class MailAttachment(Attachment):
    attdir =  None #  This is  filled in before  saving or  reading by
                   # xml.writer and xml.reader

    def __init__(self, filename):
        if os.path.isabs(filename):
            self.filename = os.path.normpath(filename)
        else:
            self.filename = os.path.normpath(os.path.join(self.attdir, filename))

        self.subject, self.description, unused = readMail(self.filename, False)

    def open(self):
        desktop.open(self.filename)

    def setDescription(self, descr):
        setMailDescription(self.filename, descr)

    def __repr__(self):
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

        return 'MAIL:' + name

    def __unicode__(self):
        return self.description

    def __cmp__(self, other):
        try:
            return cmp(self.filename, other.filename)
        except AttributeError:
            return 1


#==============================================================================
#

def AttachmentFactory(s):
    if s.startswith('URI:'):
        return URIAttachment(s[4:])
    elif s.startswith('FILE:'):
        return FileAttachment(s[5:])
    elif s.startswith('MAIL:'):
        return MailAttachment(s[5:])

    # Assume old task file

    return FileAttachment(s)
