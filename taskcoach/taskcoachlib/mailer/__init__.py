
import wx, re

def readMail(filename):
    subject = None
    description = ''
    encoding = None
    s = 0
    rx = re.compile('charset=([-0-9a-zA-Z]+)')

    for line in file(filename, 'r'):
        if s == 0:
            if line.lower().startswith('subject: '):
                subject = line[9:].strip()
            if line.strip() == '':
                s = 1
            mt = rx.search(line)
            if mt:
                encoding = mt.group(1)
        elif s == 1:
            description += line

    if encoding is None:
        encoding = wx.Locale_GetSystemEncodingName()

    if subject is None:
        subject = _('New task')
    else:
        subject = subject.decode(encoding)

    description = description.decode(encoding)

    return subject, description
