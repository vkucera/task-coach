import wx, os, re, tempfile
from i18n import _

def readMail(filename, readContent=True):
    subject = None
    description = None
    content = ''
    encoding = None
    s = 0
    rx = re.compile('charset=([-0-9a-zA-Z]+)')

    for line in file(filename, 'r'):
        if s == 0:
            if line.lower().startswith('subject: '):
                subject = line[9:].strip()
            if line.lower().startswith('x-taskcoach-description: '):
                description = line[25:].strip()
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

    if description is None:
        description = subject
    else:
        description = description.decode(encoding)

    return subject, description, content

def setMailDescription(filename, descr):
    # First find out encoding

    rx = re.compile('charset=([-0-9a-zA-Z]+)')
    encoding = None

    for line in file(filename, 'r'):
        if line.strip() == '':
            break

        mt = rx.search(line)
        if mt:
            encoding = mt.group(1)
            break

    if encoding is None:
        encoding = wx.Locale_GetSystemEncodingName()

    # Next rewrite the file

    dstname = tempfile.mktemp('.eml')
    dst = file(dstname, 'w')
    s = 0

    for line in file(filename, 'r'):
        if s == 0:
            if line.lower().startswith('x-taskcoach-description: '):
                dst.write('X-Taskcoach-Description: %s\n' % descr.encode(encoding))
                s = 1
            elif line.strip() == '':
                dst.write('X-Taskcoach-Description: %s\n' % descr.encode(encoding))
                s = 1
            else:
                dst.write(line)
        else:
            dst.write(line)

    dst.close()
    os.remove(filename)
    os.rename(dstname, filename)
