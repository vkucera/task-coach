import wx, os, re, tempfile
from i18n import _

def readMail(filename, readContent=True):
    subject = None
    content = ''
    encoding = None
    s = 0
    rx = re.compile('charset=([-0-9a-zA-Z]+)')

    for line in file(filename, 'r'):
        if s == 0:
            if line.lower().startswith('subject: '):
                subject = line[9:].strip()
            if line.strip() == '':
                if not readContent:
                    break
                s = 1
            mt = rx.search(line)
            if mt:
                encoding = mt.group(1)
        elif s == 1:
            content += line

    if encoding is None:
        encoding = wx.Locale_GetSystemEncodingName()
	if not encoding:
	    encoding = 'ISO-8859-1'

    if subject is None:
        subject = _('Untitled e-mail')
    else:
        subject = subject.decode(encoding)

    content = content.decode(encoding)

    return subject, content
