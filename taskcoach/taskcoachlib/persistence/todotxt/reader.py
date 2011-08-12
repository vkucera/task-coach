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
from taskcoachlib.domain import task, category, date


class TodoTxtReader(object):
    def __init__(self, taskList, categoryList):
        self.taskList = taskList
        self.categoryList = categoryList

    def read(self, filename):
        with file(filename, 'r') as fp:
            self.readFile(fp)
        
    def readFile(self, fp, now=date.Now):
        todoTxtRE = self.compileTodoTxtRE()
        for line in fp:
            match = todoTxtRE.match(line.strip())
            priority = self.priority(match)    
            completionDateTime = self.completionDateTime(match, now)
            startDateTime = self.startDateTime(match)
            categories = self.categories(match)
           
            recursiveSubject = match.group('subject')
            parentForTask = None
            subjects = recursiveSubject.split('->')
            for subject in subjects[:-1]:
                parentForTask = self.findOrCreateTask(subject.strip(), parentForTask)
                
            newTask = task.Task(subject=subjects[-1].strip(), 
                                priority=priority, 
                                startDateTime=startDateTime,
                                completionDateTime=completionDateTime,
                                categories=categories)
            if parentForTask:
                newTask.setParent(parentForTask)
                parentForTask.addChild(newTask)
            self.taskList.append(newTask)
            

    @staticmethod
    def priority(match):
        priorityText = match.group('priority')
        return ord(priorityText) + 1 - ord('A') if priorityText else 0
    
    @classmethod
    def completionDateTime(cls, match, now):
        if match.group('completed'):
            completionDateText = match.group('completionDate')
            return cls.dateTime(completionDateText) if completionDateText else now()
        else:
            return None
        
    @classmethod
    def startDateTime(cls, match):
        startDateText = match.group('startDate')
        return cls.dateTime(startDateText) if startDateText else None

    @staticmethod
    def dateTime(dateText):
        year, month, day = dateText.split('-')
        return date.DateTime(int(year), int(month), int(day), 0, 0, 0)
      
    def categories(self, match):
        ''' Transform both projects and contexts into categories. Since Todo.txt
            allows multiple projects for one task, but Task Coach does not allow
            for tasks to have more than one parent task, we cannot transform 
            projects into parent tasks. '''
        categories = []
        contextsAndProjects = match.group('contexts_and_projects_pre') + \
                              match.group('contexts_and_projects_post')
        contextsAndProjects = contextsAndProjects.strip()
        if contextsAndProjects:        
            for contextOrProject in contextsAndProjects.split(' '):
                recursiveSubject = contextOrProject.strip('+@')
                categoryForTask = None
                for subject in recursiveSubject.split('->'):
                    categoryForTask = self.findOrCreateCategory(subject, categoryForTask)
                categories.append(categoryForTask)
        return categories
        
    def findOrCreateCategory(self, subject, parent=None):
        categoriesToSearch = parent.children() if parent else self.categoryList.rootItems()
        for existingCategory in categoriesToSearch:
            if existingCategory.subject() == subject:
                return existingCategory
        newCategory = category.Category(subject=subject)
        if parent:
            newCategory.setParent(parent)
            parent.addChild(newCategory)
        self.categoryList.append(newCategory)
        return newCategory
    
    def findOrCreateTask(self, subject, parent=None):
        tasksToSearch = parent.children() if parent else self.taskList.rootItems()
        for existingTask in tasksToSearch:
            if existingTask.subject() == subject:
                return existingTask
        newTask = task.Task(subject=subject)
        if parent:
            newTask.setParent(parent)
            parent.addChild(newTask)
        self.taskList.append(newTask)
        return newTask
    
    @staticmethod
    def compileTodoTxtRE():
        priorityRE = r'(?:\((?P<priority>[A-Z])\) )?'
        completedRe = r'(?P<completed>[Xx] )?'
        completionDateRE = r'(?:(?<=[xX] )(?P<completionDate>\d{4}-\d{2}-\d{2}) )?'
        startDateRE = r'(?:(?P<startDate>\d{4}-\d{2}-\d{2}) )?' 
        contextsAndProjectsPreRE = r'(?P<contexts_and_projects_pre>(?:(?:^| )[@+][^\s]+)*)'
        subjectRE = r'(?P<subject>.*?)'
        contextsAndProjectsPostRE = r'(?P<contexts_and_projects_post>(?: [@+][^\s]+)*)'
        return re.compile('^' + priorityRE + completedRe + completionDateRE + \
                          startDateRE + contextsAndProjectsPreRE + subjectRE + \
                          contextsAndProjectsPostRE + '$')
        