'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>
Copyright (C) 2007 Jerome Laheurte <fraca7@free.fr>

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

import time, xml.dom.minidom, re, os, sys
from taskcoachlib.domain import date, effort, task, category, note, attachment


class XMLReader:
    def __init__(self, fd):
        self.__fd = fd

    def read(self):
        # Determine where are attachments.
        path, name = os.path.split(os.path.abspath(self.__fd.name))
        name, ext = os.path.splitext(name)
        attdir = os.path.normpath(os.path.join(path, name + '_attachments'))
        attachment.MailAttachment.attdir = attdir

        domDocument = xml.dom.minidom.parse(self.__fd)
        self.__tskversion = self.__parseTskVersionNumber(domDocument)
        tasks = self.__parseTaskNodes(domDocument.documentElement.childNodes)
        categorizables = tasks[:]
        for task in tasks:
            categorizables.extend(task.children(recursive=True))
        if self.__tskversion <= 15:
            notes = []
        else:
            notes = self.__parseNoteNodes(domDocument.documentElement.childNodes)
        categorizables.extend(notes)
        for note in notes:
            categorizables.extend(note.children(recursive=True))
        categorizablesById = dict([(categorizable.id(), categorizable) for \
                                   categorizable in categorizables])
        if self.__tskversion <= 13:
            categories = self.__parseCategoryNodesFromTaskNodes(domDocument, 
                                                                categorizablesById)
        else:
            categories = self.__parseCategoryNodes( \
                domDocument.documentElement.childNodes, categorizablesById)

        return tasks, categories, notes

    def __parseTskVersionNumber(self, domDocument):
        processingInstruction = domDocument.firstChild.data
        matchObject = re.search('tskversion="(\d+)"', processingInstruction)
        return int(matchObject.group(1))
        
    def __parseTaskNodes(self, nodes):
        return [self.__parseTaskNode(node) for node in nodes \
                if node.nodeName == 'task']
                
    def __parseCategoryNodes(self, nodes, categorizablesById):
        return [self.__parseCategoryNode(node, categorizablesById) for node in nodes \
                if node.nodeName == 'category']
        
    def __parseNoteNodes(self, nodes):
        return [self.__parseNoteNode(node) for node in nodes \
                if node.nodeName == 'note']

    def __parseCategoryNode(self, categoryNode, categorizablesById):
        kwargs = self.__parseBaseAttributes(categoryNode, 
            self.__parseCategoryNodes, categorizablesById)
        kwargs.update(dict(\
            notes=self.__parseNoteNodes(categoryNode.childNodes),
            filtered=self.__parseBoolean(categoryNode.getAttribute('filtered'), 
                                         False)))
        if self.__tskversion < 19:
            categorizableIds = categoryNode.getAttribute('tasks')
        else:
            categorizableIds = categoryNode.getAttribute('categorizables')
        if categorizableIds:
            # The category tasks attribute might contain id's that refer to tasks that
            # have been deleted (a bug in release 0.61.5), be prepared:
            categorizables = [categorizablesById[id] for id in \
                              categorizableIds.split(' ') \
                              if id in categorizablesById]
        else:
            categorizables = []
        kwargs['categorizables'] = categorizables
        return category.Category(**kwargs)
                      
    def __parseCategoryNodesFromTaskNodes(self, document, tasks):
        ''' In tskversion <=13 category nodes were subnodes of task nodes. '''
        taskNodes = document.getElementsByTagName('task')
        categoryMapping = self.__parseCategoryNodesWithinTaskNodes(taskNodes, tasks)
        subjectCategoryMapping = {}
        for taskId, categories in categoryMapping.items():
            for subject in categories:
                if subject in subjectCategoryMapping:
                    cat = subjectCategoryMapping[subject]
                else:
                    cat = category.Category(subject)
                    subjectCategoryMapping[subject] = cat
                cat.addCategorizable(tasks[taskId])
        return subjectCategoryMapping.values()
    
    def __parseCategoryNodesWithinTaskNodes(self, taskNodes, tasks):
        ''' In tskversion <=13 category nodes were subnodes of task nodes. '''
        categoryMapping = {}
        for node in taskNodes:
            taskId = node.getAttribute('id')
            categories = [self.__parseTextNode(node) for node in node.childNodes \
                          if node.nodeName == 'category']
            categoryMapping.setdefault(taskId, []).extend(categories)
        return categoryMapping
        
    def __parseTaskNode(self, taskNode):
        kwargs = self.__parseBaseAttributes(taskNode, self.__parseTaskNodes)
        kwargs.update(dict(
            startDate=date.parseDate(taskNode.getAttribute('startdate')),
            dueDate=date.parseDate(taskNode.getAttribute('duedate')),
            completionDate=date.parseDate(taskNode.getAttribute('completiondate')),
            budget=date.parseTimeDelta(taskNode.getAttribute('budget')),
            priority=self.__parseInteger(taskNode.getAttribute('priority')),
            hourlyFee=self.__parseFloat(taskNode.getAttribute('hourlyFee')),
            fixedFee=self.__parseFloat(taskNode.getAttribute('fixedFee')),
            reminder=self.__parseDateTime(taskNode.getAttribute('reminder')),
            shouldMarkCompletedWhenAllChildrenCompleted= \
                self.__parseBoolean(taskNode.getAttribute('shouldMarkCompletedWhenAllChildrenCompleted')),
            efforts=self.__parseEffortNodes(taskNode.childNodes),
            notes=self.__parseNoteNodes(taskNode.childNodes),
            recurrence=self.__parseRecurrence(taskNode)))
        if self.__tskversion <= 13:
            kwargs['categories'] = self.__parseCategoryNodesWithinTaskNode(taskNode.childNodes)
        else:
            kwargs['categories'] = []
        return task.Task(**kwargs)
        
    def __parseRecurrence(self, taskNode):
        if self.__tskversion <= 19:
            parseKwargs = self.__parseRecurrenceAttributesFromTaskNode
        else:
            parseKwargs = self.__parseRecurrenceNode
        return date.Recurrence(**parseKwargs(taskNode))
    
    def __parseRecurrenceNode(self, taskNode):
        ''' Since tskversion >= 20, recurrence information is stored in a 
            separate node. '''
        kwargs = dict(unit='', amount=1, count=0, max=0, sameWeekday=False)
        for node in self.__getNodes(taskNode, 'recurrence'):
            kwargs = dict(unit=node.getAttribute('unit'),
                amount=self.__parseInteger(node.getAttribute('amount'), 1),
                count=self.__parseInteger(node.getAttribute('count')),
                max=self.__parseInteger(node.getAttribute('max')),
                sameWeekday=self.__parseBoolean(node.getAttribute('sameWeekday'), False))
            break
        return kwargs
                               
    def __parseRecurrenceAttributesFromTaskNode(self, taskNode):
        ''' In tskversion <=19 recurrence information was stored as attributes
            of task nodes. '''
        return dict(unit=taskNode.getAttribute('recurrence'),
            count=self.__parseInteger(taskNode.getAttribute('recurrenceCount')),
            amount=self.__parseInteger(taskNode.getAttribute('recurrenceFrequency'), default=1),
            max=self.__parseInteger(taskNode.getAttribute('maxRecurrenceCount')))
    
    def __parseNoteNode(self, noteNode):
        ''' Parse the attributes and child notes from the noteNode. '''
        kwargs = self.__parseBaseAttributes(noteNode, self.__parseNoteNodes)
        return note.Note(**kwargs)
    
    def __parseBaseAttributes(self, node, parseChildren, *parseChildrenArgs):
        ''' Parse the attributes all composite domain objects share, such as
            id, subject, description, and children and return them as a 
            keyword arguments dictionary that can be passed to the domain 
            object constructor. '''
        return dict(id=node.getAttribute('id'),
            subject=node.getAttribute('subject'),
            description=self.__parseDescription(node),
            attachments=self.__parseAttachments(node),
            expandedContexts=self.__parseTuple(\
                node.getAttribute('expandedContexts'), []),
            color=self.__parseTuple(node.getAttribute('color'), None),
            children=parseChildren(node.childNodes, *parseChildrenArgs))
        
    def __parseCategoryNodesWithinTaskNode(self, nodes):
        ''' In tskversion <= 13, categories of tasks were stored as text 
            nodes. '''
        return [self.__parseTextNode(node) for node in nodes \
                if node.nodeName == 'category']

    def __parseAttachments(self, parent):
        attachments = []
        for node in self.__getNodes(parent, 'attachment'):
            if self.__tskversion <= 16:
                args = (self.__parseTextNode(node),)
            else:
                args = (self.__parseTextNode(node.getElementsByTagName('data')[0]),
                        self.__parseTextNode(node.getElementsByTagName('description')[0]),
                        node.getAttribute('type'))
            attachments.append(attachment.AttachmentFactory(*args))
        return attachments

    def __parseEffortNodes(self, nodes):
        return [self.__parseEffortNode(node) for node in nodes \
                if node.nodeName == 'effort']
        
    def __parseEffortNode(self, effortNode):
        start = effortNode.getAttribute('start')
        stop = effortNode.getAttribute('stop')
        description = self.__parseDescription(effortNode)
        return effort.Effort(task=None, start=date.parseDateTime(start), 
            stop=date.parseDateTime(stop), description=description)
        
    def __parseDescription(self, node):
        if self.__tskversion <= 6:
            description = node.getAttribute('description')
        else:
            descriptionNode = self.__getNode(node, 'description')
            if descriptionNode and descriptionNode.firstChild:
                description = descriptionNode.firstChild.data
            else:
                description = ''
        return description

    def __getNode(self, parent, tagName):
        ''' Get the child node of parent with tagName. Returns None if no child 
            node with tagName can be found. '''
        for child in parent.childNodes:
            if child.nodeName == tagName:
                return child
        return None
        
    def __getNodes(self, parent, tagName):
        ''' Get all child nodes of parent with tagName. Returns an empty list 
            if no child node with tagName can be found. '''
        nodes = []
        for child in parent.childNodes:
            if child.nodeName == tagName:
                nodes.append(child)
        return nodes
        
    def __parseTextNode(self, node):
        return node.firstChild.data
    
    def __parseInteger(self, integerText, default=0):
        return self.__parse(integerText, int, default)

    def __parseFloat(self, floatText, default=0.0):
        return self.__parse(floatText, float, default)
                    
    def __parseDateTime(self, dateTimeText):
        return self.__parse(dateTimeText, date.parseDateTime, None)
    
    def __parseBoolean(self, booleanText, defaultValue=None):
        def textToBoolean(text):
            if text in ['True', 'False']:
                return text == 'True'
            else:
                raise ValueError, "Expected 'True' or 'False', got '%s'"%booleanText
        return self.__parse(booleanText, textToBoolean, defaultValue)
        
    def __parseTuple(self, tupleText, defaultValue=None):
        if tupleText.startswith('(') and tupleText.endswith(')'):
            return self.__parse(tupleText, eval, defaultValue)
        else:
            return defaultValue
    
    def __parse(self, text, parseFunction, defaultValue):
        try:
            return parseFunction(text)
        except ValueError:
            return defaultValue
