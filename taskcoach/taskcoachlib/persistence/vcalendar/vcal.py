
"""

This module defines classes and functions to handle the VCalendar
format.

"""

from taskcoachlib.domain.base import Object
from taskcoachlib.domain.date import date

import time, calendar

#{ Utility functions

def parseDate(fulldate):
    """Parses a date as seen in vcalendar files into a
    L{taskcoachlib.domain.date.Date} object."""

    dt, tm = fulldate.split('T')
    year, month, day = int(dt[:4]), int(dt[4:6]), int(dt[6:8])
    hour, minute, second = int(tm[:2]), int(tm[2:4]), int(tm[4:6])

    if fulldate.endswith('Z'):
        # GMT. Convert this to local time.
        localTime = time.localtime(calendar.timegm((year, month, day, hour, minute, second, 0, 0, -1)))
        year, month, day = localTime[:3]

    return date.Date(year, month, day)

def fmtDate(dt):
    """Formats a L{taskcoachlib.domain.date.Date} object to a string
    suitable for inclusion in a vcalendar file."""
    return '%04d%02d%02dT000000' % (dt.year, dt.month, dt.day)

def quoteString(s):
    """The 'quoted-printable' codec doesn't encode \n, but tries to
    fold lines with \n instead of CRLF and generally does strange
    things that ScheduleWorld does not understand (me neither, to an
    extent). Same thing with \r. This function works around this."""

    s = s.encode('UTF-8').encode('quoted-printable')
    s = s.replace('=\r', '')
    s = s.replace('=\n', '')
    s = s.replace('\r', '=0D')
    s = s.replace('\n', '=0A')

    return s

#}

#{ Parsing VCalendar files

class VCalendarParser(object):
    """Base parser class for vcalendar files. This uses the State
    pattern (in its Python incarnation, replacing the class of an
    object at runtime) in order to parse different objects in the
    VCALENDAR. Other states are

     - VTodoParser: parses VTODO objects.

    @ivar kwargs: While parsing, the keyword arguments for the
        domain object creation for the current (parsed) object.
    @ivar tasks: A list of dictionnaries suitable to use as
        keyword arguments for task creation, representing all
        VTODO object in the parsed file."""

    def __init__(self, *args, **kwargs):
        super(VCalendarParser, self).__init__(*args, **kwargs)

        self.stateMap = { 'VCALENDAR': VCalendarParser,
                          'VTODO':     VTodoParser }

        self.tasks = []

        self.init()

    def init(self):
        """Called after a state change."""
        self.kwargs = {}

    def setState(self, state):
        """Sets the state (class) of the parser object."""
        self.__class__ = state
        self.init()

    def parse(self, lines):
        """Actually parses the file.
        @param lines: A list of lines."""

        # TODO: avoid using indexes here, just iterate. This way the
        # method can accept a file object as argument.

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
        """Called by L{parse} for each line to parse. L{parse} is
        supposed to have handled the unfolding."""

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
            else:
                # Some  servers only  specify CHARSET  when  there are
                # non-ASCII characters :)
                value = value.decode('ascii')

            self.acceptItem(name, value)

        return False

    def onFinish(self):
        """This method is called when the current object ends."""
        raise NotImplementedError

    def acceptItem(self, name, value):
        """Called on each new 'item', i.e. key/value pair. Default
        behaviour is to store the pair in the 'kwargs' instance
        variable (which is emptied in L{init})."""
        self.kwargs[name.lower()] = value


class VTodoParser(VCalendarParser):
    """This is the state responsible for parsing VTODO objects."""

    def onFinish(self):
        if not self.kwargs.has_key('startDate'):
            # This means no start  date, but the task constructor will
            # take today, so force.
            self.kwargs['startDate'] = date.Date()

        if self.kwargs.has_key('vcardStatus'):
            if self.kwargs['vcardStatus'] == 'COMPLETED' and \
                   not self.kwargs.has_key('completionDate'):
                # Some servers only give the status, and not the date (SW)
                if self.kwargs.has_key('last-modified'):
                    self.kwargs['completionDate'] = parseDate(self.kwargs['last-modified'])
                else:
                    self.kwargs['completionDate'] = date.Today()

        self.kwargs['status'] = Object.STATUS_NONE
        self.tasks.append(self.kwargs)

    def acceptItem(self, name, value):
        if name == 'DTSTART':
            self.kwargs['startDate'] = parseDate(value)
        elif name == 'DUE':
            self.kwargs['dueDate'] = parseDate(value)
        elif name == 'COMPLETED':
            self.kwargs['completionDate'] = parseDate(value)
        elif name == 'UID':
            self.kwargs['id'] = value.decode('UTF-8')
        elif name == 'PRIORITY':
            # Okay. Seems that in vcal,  the priority ranges from 1 to
            # 3, but what it means depends on the other client...

            self.kwargs['priority'] = int(value) - 1
        elif name == 'SUMMARY':
            self.kwargs['subject'] = value
        elif name == 'CATEGORIES':
            self.kwargs['categories'] = value.split(',')
        elif name == 'STATUS':
            self.kwargs['vcardStatus'] = value
        else:
            super(VTodoParser, self).acceptItem(name, value)

#}


#==============================================================================
#{ Generating VCalendar files.

def VCalFromTask(task):
    """This function returns a string representing the task in
    vcalendar format."""

    components = []

    values = { 'description': quoteString(task.description()),
               'subject': quoteString(task.subject()),
               'priority': min(3, task.priority() + 1),
               'categories': ','.join(map(quoteString, [unicode(c) for c in task.categories(True)])) }

    components.append('BEGIN:VTODO')
    components.append('UID:%s' % task.id().encode('UTF-8'))

    if task.startDate() != date.Date():
        components.append('DTSTART:%(startDate)s')
        values['startDate'] = fmtDate(task.startDate())

    if task.dueDate() != date.Date():
        components.append('DUE:%(dueDate)s')
        values['dueDate'] = fmtDate(task.dueDate())

    if task.completionDate() != date.Date():
        components.append('COMPLETED:%(completionDate)s')
        values['completionDate'] = fmtDate(task.completionDate())

    if task.categories(True):
        components.append('CATEGORIES;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:%(categories)s')

    if task.completed():
        components.append('STATUS:COMPLETED')
    elif task.active():
        components.append('STATUS:NEEDS-ACTION')
    else:
        components.append('STATUS:CANCELLED') # Hum...

    components.append('DESCRIPTION;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:%(description)s')
    components.append('PRIORITY:%(priority)d')
    components.append('SUMMARY;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:%(subject)s')
    components.append('END:VTODO')

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

#}
