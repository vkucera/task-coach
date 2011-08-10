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

from taskcoachlib.domain import date


class TodoTxtWriter(object):
    def __init__(self, fd, filename):
        self.__fd = fd
        self.__filename = filename
        
    def write(self, viewer, settings, selectionOnly, **kwargs):
        count = 0
        for task in viewer.visibleItems():
            if selectionOnly and not viewer.isselected(task):
                continue
            count += 1
            self.__fd.write(self.formatPriority(task.priority()) + \
                            self.formatStartDate(task.startDateTime()) + \
                            task.subject() + '\n')
        return count
                
    def formatPriority(self, priorityNumber):
        if 1 <= priorityNumber <= 26:
            return '(%s) '%chr(ord('A') + priorityNumber - 1)
        else:
            return ''
        
    def formatStartDate(self, startDateTime):
        if startDateTime == date.DateTime():
            return ''
        else:
            return startDateTime.date().strftime('%Y-%m-%d') + ' '