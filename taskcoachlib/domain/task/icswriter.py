import meta
import time

class ICSWriter:
    ''' Write effort out in vCalendar format. See http://www.imc.org/pdi/ 
        and more specifically http://www.ietf.org/rfc/rfc2445.txt.
        Initial version provided by Gissehel. '''

    def __init__(self, fd):
        self.__fd = fd

    def __iadd__(self, line):
        self.__fd.write(line+'\n')
        self.__fd.flush()
        return self

    def write(self, taskList):
        self += 'BEGIN:VCALENDAR'
        self += 'VERSION:2.0'
        domain = meta.url[len('http://'):-1]
        self += 'PRODID:-//%s//NONSGML %s V%s//EN'%(domain, meta.name, meta.version)

        for task in taskList.rootTasks():
            self.writeTask(task)

        self += 'END:VCALENDAR'

    def writeTask(self, task, parentName=None):
        if parentName == None :
            name = task.subject()
        else :
            name = parentName + ' -> ' + task.subject() # don't use magic constant

        for child in task.children():
            self.writeTask(child, name)

        for effort in task.efforts():
            self.writeEffort(task, effort, name)

    def writeEffort(self, task, effort, name):
        self += 'BEGIN:VEVENT'

        self += 'SUMMARY:%s'%name

        description = ''
        if task.description() != '' :
            description = task.description()
        if effort.getDescription() != '' :
            if description != '' :
                description += '\n----\n'
            description += effort.getDescription()
        if description != '' :
            self += 'DESCRIPTION:%s'%description.replace('\n','\\n')

        start = effort.getStart().strftime('%Y%m%dT%H%M%SZ')
        stop = effort.getStop().strftime('%Y%m%dT%H%M%SZ')
        istart = int(time.mktime(effort.getStart().utctimetuple()))
        istop = int(time.mktime(effort.getStop().utctimetuple()))

        self += 'CREATED:%s' % start
        self += 'LAST-MODIFIED:%s' % stop
        self += 'DTSTAMP:%s' % start
        self += 'CLASS:PUBLIC'
        self += 'PRIORITY:0'
        self += 'UID:uuid:%d-%d' % (istart, istop)
        self += 'DTSTART:%s' % start
        self += 'DTEND:%s' % stop

        self += 'END:VEVENT'

