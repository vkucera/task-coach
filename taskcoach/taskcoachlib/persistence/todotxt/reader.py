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
from taskcoachlib import patterns


class TodoTxtReader(object):
    def __init__(self, taskList, categoryList):
        self.__taskList = taskList
        self.__tasksBySubject = self.__createSubjectCache(taskList)
        self.__categoryList = categoryList
        self.__categoriesBySubject = self.__createSubjectCache(categoryList)

    def read(self, filename):
        with file(filename, 'r') as fp:
            self.readFile(fp)
    
    @patterns.eventSource    
    def readFile(self, fp, now=date.Now, event=None):
        todoTxtRE = self.compileTodoTxtRE()
        for line in fp:
            line = line.strip()
            if line:
                self.processLine(line, todoTxtRE, now, event)
            
    def processLine(self, line, todoTxtRE, now, event):
        match = todoTxtRE.match(line)
        priority = self.priority(match)    
        completionDateTime = self.completionDateTime(match, now)
        startDateTime = self.startDateTime(match)
        categories = self.categories(match, event)
       
        recursiveSubject = match.group('subject')
        subjects = recursiveSubject.split('->')
        newTask = None
        for subject in subjects:
            newTask = self.findOrCreateTask(subject.strip(), newTask, event)
        
        newTask.setPriority(priority, event=event)
        newTask.setStartDateTime(startDateTime, event=event)
        newTask.setCompletionDateTime(completionDateTime, event=event)
        for eachCategory in categories:
            newTask.addCategory(eachCategory, event=event)
            eachCategory.addCategorizable(newTask, event=event)
                
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
            return date.DateTime()
        
    @classmethod
    def startDateTime(cls, match):
        startDateText = match.group('startDate')
        return cls.dateTime(startDateText) if startDateText else date.DateTime()

    @staticmethod
    def dateTime(dateText):
        year, month, day = dateText.split('-')
        return date.DateTime(int(year), int(month), int(day), 0, 0, 0)
      
    def categories(self, match, event):
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
                    categoryForTask = self.findOrCreateCategory(subject, categoryForTask, event)
                categories.append(categoryForTask)
        return categories
        
    def findOrCreateCategory(self, subject, parent, event):
        if subject in self.__categoriesBySubject:
            categories = self.__categoriesBySubject[subject]
            for categoryWithSubjectWeAreLookingFor in categories:
                if categoryWithSubjectWeAreLookingFor.parent() == parent:
                    return categoryWithSubjectWeAreLookingFor
        newCategory = category.Category(subject=subject)
        if parent:
            newCategory.setParent(parent)
            parent.addChild(newCategory, event=event)
        self.__categoryList.append(newCategory, event=event)
        self.__categoriesBySubject.setdefault(subject, []).append(newCategory)
        return newCategory
        
    def findOrCreateTask(self, subject, parent, event):
        if subject in self.__tasksBySubject:
            tasks = self.__tasksBySubject[subject]
            for taskWithSubjectWeAreLookingFor in tasks:
                if taskWithSubjectWeAreLookingFor.parent() == parent:
                    return taskWithSubjectWeAreLookingFor
        newTask = task.Task(subject=subject)
        if parent:
            newTask.setParent(parent)
            parent.addChild(newTask, event=event)
        self.__taskList.append(newTask, event=event)
        self.__tasksBySubject.setdefault(subject, []).append(newTask)
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
        
    @staticmethod
    def __createSubjectCache(itemContainer):
        cache = dict()
        for item in itemContainer:
            cache.setdefault(item.subject(), []).append(item)
        return cache

        