'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2011 Task Coach developers <developers@taskcoach.org>

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

import re
from taskcoachlib.domain import date


class TodoTxtWriter(object):
    def __init__(self, fd, filename):
        self.__fd = fd
        self.__filename = filename
        self.__maxDateTime = date.DateTime()
        
    def write(self, viewer, settings, selectionOnly, **kwargs):
        count = 0
        for task in viewer.visibleItems():
            if selectionOnly and not viewer.isselected(task):
                continue
            count += 1
            self.__fd.write(self.priority(task.priority()) + \
                            self.completionDate(task.completionDateTime()) + \
                            self.startDate(task.startDateTime()) + \
                            task.subject(recursive=True) + \
                            self.contexts(task) + \
                            self.dueDate(task.dueDateTime()) + '\n')
        return count
                
    @staticmethod
    def priority(priorityNumber):
        return '(%s) '%chr(ord('A') + priorityNumber - 1) if 1 <= priorityNumber <= 26 else ''

    @classmethod
    def startDate(cls, startDateTime):
        return '%s '%cls.dateTime(startDateTime) if cls.isActualDateTime(startDateTime) else ''
    
    @classmethod
    def dueDate(cls, dueDateTime):
        return ' due:%s'%cls.dateTime(dueDateTime) if cls.isActualDateTime(dueDateTime) else ''
        
    @classmethod
    def completionDate(cls, completionDateTime):
        return 'X ' + '%s '%cls.dateTime(completionDateTime) if cls.isActualDateTime(completionDateTime) else ''
        
    @staticmethod
    def dateTime(dateTime):
        ''' Todo.txt doesn't support time, just dates, so ignore the time part. '''
        return dateTime.date().strftime('%Y-%m-%d')

    @staticmethod
    def isActualDateTime(dateTime, maxDateTime=date.DateTime()):
        return dateTime != maxDateTime

    @classmethod
    def contexts(cls, task):
        contexts = ' '.join(sorted([cls.context(category) for category in task.categories()]))
        return ' ' + contexts if contexts else ''

    @staticmethod
    def context(category):
        subject = category.subject(recursive=True).strip()
        subject = re.sub(r' -> ', '->', subject)
        context = re.sub(r'\s+', '_', subject)
        return context if context.startswith('@') else '@' + context
