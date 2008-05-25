
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

from taskcoachlib.domain.task import Task
from taskcoachlib.domain.base import Object
from taskcoachlib.domain.date import date

# Utility functions

def parseDate(dt):
    dt, tm = dt.split('T')
    return date.Date(int(dt[:4]), int(dt[4:6]), int(dt[6:8]))

def fmtDate(dt):
    if dt == date.Date():
        return '00000000T000000' # FIXME
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
        for line in lines:
            if line.startswith('BEGIN:'):
                try:
                    self.setState(self.stateMap[line[6:]])
                except KeyError:
                    raise TypeError, 'Unrecognized vcal type: %s' % line[6:]
            elif line.startswith('END:'):
                if line[4:] == 'VCALENDAR':
                    break
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

    def onFinish(self):
        raise NotImplementedError

    def acceptItem(self, name, value):
        self.kwargs[name.lower()] = value


class VTodoParser(VCalendarParser):
    def onFinish(self):
        self.kwargs['status'] = Object.STATUS_NONE
        self.tasks.append(Task(**self.kwargs))

    def acceptItem(self, name, value):
        if name == 'DTSTART':
            self.kwargs['startDate'] = parseDate(value)
        elif name == 'DUE':
            self.kwargs['dueDate'] = parseDate(value)
        elif name == 'PRIORITY':
            self.kwargs['priority'] = int(value)
        elif name == 'SUMMARY':
            self.kwargs['subject'] = value
        elif name == 'CATEGORIES':
            pass # TODO!!!
        else:
            super(VTodoParser, self).acceptItem(name, value)


#==============================================================================
#

def VCalFromTask(task):
    r = """BEGIN:VCALENDAR
VERSION:1.0
BEGIN:VTODO"""
    if task.startDate() != date.Date():
        r += """
DTSTART:%(startDate)s"""
    if task.dueDate() != date.Date():
        r += """
DUE:%(dueDate)s"""
    r += """
DESCRIPTION;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:%(description)s
PRIORITY:%(priority)d
SUMMARY;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:%(subject)s
END:VTODO
END:VCALENDAR"""

    return r % { 'startDate': fmtDate(task.startDate()),
                 'dueDate':   fmtDate(task.dueDate()),
                 'description': task.description().encode('UTF-8').encode('quoted-printable'),
                 'subject': task.subject().encode('UTF-8').encode('quoted-printable'),
                 'priority': task.priority() }
