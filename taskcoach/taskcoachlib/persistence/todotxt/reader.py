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
from taskcoachlib.domain import task, date


class TodoTxtReader(object):
    def __init__(self, taskList, categoryList):
        self.taskList = taskList
        self.categoryList = categoryList

    def read(self, filename):
        with file(filename, 'r') as fp:
            self.readFile(fp)
        
    def readFile(self, fp):
        todoTxtRE = self.compileTodoTxtRE()
        for line in fp:
            match = todoTxtRE.match(line)
            priority = ord(match.group('priority')) + 1 - ord('A') if match.group('priority') else 0
            startDateTime = self.startDateTime(match.group('startDate')) if match.group('startDate') else None
            self.taskList.append(task.Task(subject=match.group('subject'), 
                                           priority=priority, 
                                           startDateTime=startDateTime))
            
    def startDateTime(self, startDateText):
        year, month, day = startDateText.split('-')
        return date.DateTime(int(year), int(month), int(day), 0, 0, 0)
            
    @staticmethod
    def compileTodoTxtRE():
        priorityRE = r'(?:\((?P<priority>[A-Z])\) )?'
        startDateRE = r'(?:(?P<startDate>\d{4}-\d{2}-\d{2}) )?' 
        subjectRE = r'(?P<subject>.*)'
        return re.compile('^' + priorityRE + startDateRE + subjectRE + '$')
        