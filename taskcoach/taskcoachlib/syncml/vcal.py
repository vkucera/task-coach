
"""
BEGIN:VCALENDAR
VERSION:1.0
BEGIN:VTODO
CATEGORIES:Personal
DTSTART:20080523T000000
DTSTART:20080523T000000
DUE:20080524T000000
DESCRIPTION;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:Test description=0A=0A=3D multiline=0A=0AAccentu=C3=A9=0A=0AModif bidon=0A
LAST-MODIFIED:20080525T094406Z
PERCENT-COMPLETE:0
PRIORITY:2
STATUS:NEEDS ACTION
SUMMARY;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:Test todo
END:VTODO
END:VCALENDAR
"""

from taskcoachlib.domain.base import Object
from taskcoachlib.domain.date import date

# Utility functions

def parseDate(dt):
    dt, tm = dt.split('T')
    return date.Date(int(dt[:4]), int(dt[4:6]), int(dt[6:8]))

def fmtDate(dt):
    return '%04d%02d%02dT000000' % (dt.year, dt.month, dt.day)

class VCalendarParser(object):
    def __init__(self, *args, **kwargs):
        super(VCalendarParser, self).__init__(*args, **kwargs)

        self.stateMap = { 'VCALENDAR': VCalendarParser,
                          'VTODO':     VTodoParser }

        self.tasks = []

        self.init()

    def init(self):
        self.kwargs = {}

    def setState(self, state):
        self.__class__ = state
        self.init()

    def parse(self, lines):
        currentLine = lines[0]

        for line in lines[1:]:
            if line.startswith(' ') or line.startswith('\t'):
                currentLine += line[1:]
            else:
                if self.handleLine(currentLine):
                    return
                currentLine = line

        self.handleLine(currentLine)

    def handleLine(self, line):
        if line.startswith('BEGIN:'):
            try:
                self.setState(self.stateMap[line[6:]])
            except KeyError:
                raise TypeError, 'Unrecognized vcal type: %s' % line[6:]
        elif line.startswith('END:'):
            if line[4:] == 'VCALENDAR':
                return True
            else:
                self.onFinish()
                self.setState(VCalendarParser)
        else:
            try:
                idx = line.index(':')
            except ValueError:
                raise RuntimeError, 'Malformed vcal line: %s' % line

            details, value = line[:idx].split(';'), line[idx + 1:]
            name, specs = details[0], details[1:]
            specs = dict([tuple(v.split('=')) for v in specs])

            if specs.has_key('ENCODING'):
                value = value.decode(specs['ENCODING'].lower())
            if specs.has_key('CHARSET'):
                value = value.decode(specs['CHARSET'].lower())

            self.acceptItem(name, value)

        return False

    def onFinish(self):
        raise NotImplementedError

    def acceptItem(self, name, value):
        self.kwargs[name.lower()] = value


class VTodoParser(VCalendarParser):
    def onFinish(self):
        if not self.kwargs.has_key('startDate'):
            # This means no start  date, but the task constructor will
            # take today, so force.
            self.kwargs['startDate'] = date.Date()

        self.kwargs['status'] = Object.STATUS_NONE
        self.tasks.append(self.kwargs)

    def acceptItem(self, name, value):
        if name == 'DTSTART':
            self.kwargs['startDate'] = parseDate(value)
        elif name == 'DUE':
            self.kwargs['dueDate'] = parseDate(value)
        elif name == 'UID':
            self.kwargs['id'] = value.decode('UTF-8')
        elif name == 'PRIORITY':
            # On ScheduleWorld,  priority may be 1  (high), 2 (medium)
            # or  3 (low).  Other  values are  ignored. In  TaskCoach,
            # priority  is  any  positive  or  nul  number,  and  it's
            # positively correlated with the actual task priority...
            self.kwargs['priority'] = max(0, 3 - int(value))
        elif name == 'SUMMARY':
            self.kwargs['subject'] = value
        elif name == 'CATEGORIES':
            self.kwargs['categories'] = value.split(',')
        else:
            super(VTodoParser, self).acceptItem(name, value)


#==============================================================================
#

def quoteString(s):
    # 'quoted-printable' codec  doesn't encode  \n, but tries  to fold
    # lines with \n instead of  CRLF and generally does strange things
    # that ScheduleWorld does not understand. Same thing with \r.

    s = s.encode('UTF-8').encode('quoted-printable')
    s = s.replace('=\r', '')
    s = s.replace('=\n', '')
    s = s.replace('\r', '=0D')
    s = s.replace('\n', '=0A')

    return s

def VCalFromTask(task):
    components = []

    values = { 'description': quoteString(task.description()),
               'subject': quoteString(task.subject()),
               'priority': max(1, 3 - task.priority()),
               'categories': ','.join(map(quoteString, [unicode(c).encode('UTF-8') for c in task.categories()])) }

    components.append('BEGIN:VCALENDAR')
    components.append('VERSION: 1.0')
    components.append('BEGIN:VTODO')
    components.append('UID:%s' % task.id().encode('UTF-8'))

    if task.startDate() != date.Date():
        components.append('DTSTART:%(startDate)s')
        values['startDate'] = fmtDate(task.startDate())

    if task.dueDate() != date.Date():
        components.append('DUE:%(dueDate)s')
        values['dueDate'] = fmtDate(task.dueDate())

    if task.categories():
        components.append('CATEGORIES;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:%(categories)s')

    components.append('DESCRIPTION;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:%(description)s')
    components.append('PRIORITY:%(priority)d')
    components.append('SUMMARY;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:%(subject)s')
    components.append('END:VTODO')
    components.append('END:VCALENDAR')

    text = ''

    for component in components:
        line = component % values

        if len(line) < 75:
            text += line + '\r\n'
        else:
            text += line[:75] + '\r\n'
            line = line[75:]

            while True:
                if len(line) < 75:
                    text += ' ' + line + '\r\n'
                    break
                else:
                    text += ' ' + line[:75] + '\r\n'
                    line = line[75:]

    return text
