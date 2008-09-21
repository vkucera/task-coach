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

import time, xml.dom.minidom, re, os, sys, datetime
from taskcoachlib.domain import date, effort, task, category, note, attachment
from taskcoachlib.syncml.config import SyncMLConfigNode, createDefaultSyncConfig
from taskcoachlib.thirdparty.guid import generate
from taskcoachlib.thirdparty.desktop import get_temp_file


class XMLReader(object):
    def __init__(self, fd):
        self.__fd = fd

    def read(self):
        domDocument = xml.dom.minidom.parse(self.__fd)
        self.__tskversion = self._parseTskVersionNumber(domDocument)
        tasks = self._parseTaskNodes(domDocument.documentElement.childNodes)
        categorizables = tasks[:]
        for task in tasks:
            categorizables.extend(task.children(recursive=True))
        if self.__tskversion <= 15:
            notes = []
        else:
            notes = self._parseNoteNodes(domDocument.documentElement.childNodes)
        categorizables.extend(notes)
        for note in notes:
            categorizables.extend(note.children(recursive=True))
        categorizablesById = dict([(categorizable.id(), categorizable) for \
                                   categorizable in categorizables])
        if self.__tskversion <= 13:
            categories = self._parseCategoryNodesFromTaskNodes(domDocument, 
                                                                categorizablesById)
        else:
            categories = self._parseCategoryNodes( \
                domDocument.documentElement.childNodes, categorizablesById)

        guid = self.__findGUIDNode(domDocument.documentElement.childNodes)
        syncMLConfig = self._parseSyncMLNode(domDocument.documentElement.childNodes, guid)

        return tasks, categories, notes, syncMLConfig, guid

    def _parseTskVersionNumber(self, domDocument):
        processingInstruction = domDocument.firstChild.data
        matchObject = re.search('tskversion="(\d+)"', processingInstruction)
        return int(matchObject.group(1))
        
    def _parseTaskNodes(self, nodes):
        return [self._parseTaskNode(node) for node in nodes \
                if node.nodeName == 'task']
                
    def _parseCategoryNodes(self, nodes, categorizablesById):
        return [self._parseCategoryNode(node, categorizablesById) for node in nodes \
                if node.nodeName == 'category']
        
    def _parseNoteNodes(self, nodes):
        return [self._parseNoteNode(node) for node in nodes \
                if node.nodeName == 'note']

    def _parseCategoryNode(self, categoryNode, categorizablesById):
        kwargs = self._parseBaseCompositeAttributes(categoryNode, 
            self._parseCategoryNodes, categorizablesById)
        kwargs.update(dict(\
            notes=self._parseNoteNodes(categoryNode.childNodes),
            filtered=self._parseBoolean(categoryNode.getAttribute('filtered'), 
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
        if self.__tskversion > 20:
            kwargs['attachments'] = self._parseAttachmentNodes(categoryNode.childNodes)
        return category.Category(**kwargs)
                      
    def _parseCategoryNodesFromTaskNodes(self, document, tasks):
        ''' In tskversion <=13 category nodes were subnodes of task nodes. '''
        taskNodes = document.getElementsByTagName('task')
        categoryMapping = self._parseCategoryNodesWithinTaskNodes(taskNodes, tasks)
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
    
    def _parseCategoryNodesWithinTaskNodes(self, taskNodes, tasks):
        ''' In tskversion <=13 category nodes were subnodes of task nodes. '''
        categoryMapping = {}
        for node in taskNodes:
            taskId = node.getAttribute('id')
            categories = [self._parseTextNode(node) for node in node.childNodes \
                          if node.nodeName == 'category']
            categoryMapping.setdefault(taskId, []).extend(categories)
        return categoryMapping
        
    def _parseTaskNode(self, taskNode):
        kwargs = self._parseBaseCompositeAttributes(taskNode, self._parseTaskNodes)
        kwargs.update(dict(
            startDate=date.parseDate(taskNode.getAttribute('startdate')),
            dueDate=date.parseDate(taskNode.getAttribute('duedate')),
            completionDate=date.parseDate(taskNode.getAttribute('completiondate')),
            budget=date.parseTimeDelta(taskNode.getAttribute('budget')),
            priority=self._parseInteger(taskNode.getAttribute('priority')),
            hourlyFee=self._parseFloat(taskNode.getAttribute('hourlyFee')),
            fixedFee=self._parseFloat(taskNode.getAttribute('fixedFee')),
            reminder=self._parseDateTime(taskNode.getAttribute('reminder')),
            shouldMarkCompletedWhenAllChildrenCompleted= \
                self._parseBoolean(taskNode.getAttribute('shouldMarkCompletedWhenAllChildrenCompleted')),
            efforts=self._parseEffortNodes(taskNode.childNodes),
            notes=self._parseNoteNodes(taskNode.childNodes),
            recurrence=self._parseRecurrence(taskNode)))
        if self.__tskversion <= 13:
            kwargs['categories'] = self._parseCategoryNodesWithinTaskNode(taskNode.childNodes)
        else:
            kwargs['categories'] = []

        if self.__tskversion > 20:
            kwargs['attachments'] = self._parseAttachmentNodes(taskNode.childNodes)

        return task.Task(**kwargs)
        
    def _parseRecurrence(self, taskNode):
        if self.__tskversion <= 19:
            parseKwargs = self._parseRecurrenceAttributesFromTaskNode
        else:
            parseKwargs = self._parseRecurrenceNode
        return date.Recurrence(**parseKwargs(taskNode))
    
    def _parseRecurrenceNode(self, taskNode):
        ''' Since tskversion >= 20, recurrence information is stored in a 
            separate node. '''
        kwargs = dict(unit='', amount=1, count=0, max=0, sameWeekday=False)
        for node in self.__getNodes(taskNode, 'recurrence'):
            kwargs = dict(unit=node.getAttribute('unit'),
                amount=self._parseInteger(node.getAttribute('amount'), 1),
                count=self._parseInteger(node.getAttribute('count')),
                max=self._parseInteger(node.getAttribute('max')),
                sameWeekday=self._parseBoolean(node.getAttribute('sameWeekday'), False))
            break
        return kwargs
                               
    def _parseRecurrenceAttributesFromTaskNode(self, taskNode):
        ''' In tskversion <=19 recurrence information was stored as attributes
            of task nodes. '''
        return dict(unit=taskNode.getAttribute('recurrence'),
            count=self._parseInteger(taskNode.getAttribute('recurrenceCount')),
            amount=self._parseInteger(taskNode.getAttribute('recurrenceFrequency'), default=1),
            max=self._parseInteger(taskNode.getAttribute('maxRecurrenceCount')))
    
    def _parseNoteNode(self, noteNode):
        ''' Parse the attributes and child notes from the noteNode. '''
        kwargs = self._parseBaseCompositeAttributes(noteNode, self._parseNoteNodes)
        if self.__tskversion > 20:
            kwargs['attachments'] = self._parseAttachmentNodes(noteNode.childNodes)
        return note.Note(**kwargs)
    
    def _parseBaseAttributes(self, node):
        ''' Parse the attributes all composite domain objects share, such as
            id, subject, description, and return them as a 
            keyword arguments dictionary that can be passed to the domain 
            object constructor. '''
        attributes = dict(id=node.getAttribute('id'),
            subject=node.getAttribute('subject'),
            description=self._parseDescription(node),
            color=self._parseTuple(node.getAttribute('color'), None))

        if self.__tskversion <= 20:
            attributes['attachments'] = self._parseAttachmentsBeforeVersion21(node)
        if self.__tskversion >= 22:
            attributes['status'] = int(node.getAttribute('status'))

        return attributes

    def _parseBaseCompositeAttributes(self, node, parseChildren, *parseChildrenArgs):
        """Same as _parseBaseAttributes, but also parse children and expandedContexts."""
        kwargs = self._parseBaseAttributes(node)
        kwargs['children'] = parseChildren(node.childNodes, *parseChildrenArgs)
        kwargs['expandedContexts'] = self._parseTuple(node.getAttribute('expandedContexts'), [])
        return kwargs

    def _parseCategoryNodesWithinTaskNode(self, nodes):
        ''' In tskversion <= 13, categories of tasks were stored as text 
            nodes. '''
        return [self._parseTextNode(node) for node in nodes \
                if node.nodeName == 'category']

    def _parseAttachmentsBeforeVersion21(self, parent):
        attachments = []
        for node in self.__getNodes(parent, 'attachment'):
            if self.__tskversion <= 16:
                args = (self._parseTextNode(node),)
                kwargs = dict()
            else:
                args = (self._parseTextNode(node.getElementsByTagName('data')[0]),
                        node.getAttribute('type'))
                description = self._parseTextNode(node.getElementsByTagName('description')[0])
                kwargs = dict(subject=description,
                              description=description)

            attachments.append(attachment.AttachmentFactory(*args, **kwargs))
        return attachments

    def _parseEffortNodes(self, nodes):
        return [self._parseEffortNode(node) for node in nodes \
                if node.nodeName == 'effort']

    def _parseEffortNode(self, effortNode):
        kwargs = {}
        if self.__tskversion >= 22:
            kwargs['status'] = int(effortNode.getAttribute('status'))
        start = effortNode.getAttribute('start')
        stop = effortNode.getAttribute('stop')
        description = self._parseDescription(effortNode)
        return effort.Effort(task=None, start=date.parseDateTime(start), 
            stop=date.parseDateTime(stop), description=description, **kwargs)

    def _parseSyncMLNode(self, nodes, guid):
        syncML = createDefaultSyncConfig(guid)

        for node in nodes:
            if node.nodeName == 'syncml':
                self._parseSyncMLNodes(node.childNodes, syncML)

        return syncML

    def _parseSyncMLNodes(self, nodes, cfgNode):
        for node in nodes:
            if node.nodeName == 'property':
                cfgNode.set(node.getAttribute('name'), self._parseTextNodeOrEmpty(node))
            else:
                for childCfgNode in cfgNode.children():
                    if childCfgNode.name == node.nodeName:
                        break
                else:
                    childCfgNode = SyncMLConfigNode(node.nodeName)
                    cfgNode.addChild(childCfgNode)
                self._parseSyncMLNodes(node.childNodes, childCfgNode)

    def __findGUIDNode(self, nodes):
        for node in nodes:
            if node.nodeName == 'guid':
                return self._parseTextNode(node)
        return generate()
        
    def _parseAttachmentNodes(self, nodes):
        return [self._parseAttachmentNode(node) for node in nodes \
                if node.nodeName == 'attachment']

    def _parseAttachmentNode(self, attachmentNode):
        kwargs = self._parseBaseAttributes(attachmentNode)
        kwargs['notes'] = self._parseNoteNodes(attachmentNode.childNodes)

        if self.__tskversion <= 22:
            path, name = os.path.split(os.path.abspath(self.__fd.name))
            name, ext = os.path.splitext(name)
            attdir = os.path.normpath(os.path.join(path, name + '_attachments'))
            location = os.path.join(attdir, attachmentNode.getAttribute('location'))
        else:
            if attachmentNode.hasAttribute('location'):
                location = attachmentNode.getAttribute('location')
            else:
                for node in attachmentNode.childNodes:
                    if node.nodeName == 'data':
                        data = node.firstChild.data
                        ext = node.getAttribute('extension')
                        break
                else:
                    raise ValueError, 'Neither location or data are defined for this attachment.'

                location = get_temp_file(suffix=ext)
                file(location, 'wb').write(data.decode('base64'))

        return attachment.AttachmentFactory(location,
                                            attachmentNode.getAttribute('type'),
                                            **kwargs)

    def _parseDescription(self, node):
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
        
    def _parseTextNode(self, node):
        return node.firstChild.data
    
    def _parseInteger(self, integerText, default=0):
        return self._parse(integerText, int, default)

    def _parseTextNodeOrEmpty(self, node):
        if node.firstChild:
            return node.firstChild.data
        return u''

    def _parseFloat(self, floatText, default=0.0):
        return self._parse(floatText, float, default)
                    
    def _parseDateTime(self, dateTimeText):
        return self._parse(dateTimeText, date.parseDateTime, None)
    
    def _parseBoolean(self, booleanText, defaultValue=None):
        def textToBoolean(text):
            if text in ['True', 'False']:
                return text == 'True'
            else:
                raise ValueError, "Expected 'True' or 'False', got '%s'"%booleanText
        return self._parse(booleanText, textToBoolean, defaultValue)
        
    def _parseTuple(self, tupleText, defaultValue=None):
        if tupleText.startswith('(') and tupleText.endswith(')'):
            return self._parse(tupleText, eval, defaultValue)
        else:
            return defaultValue
    
    def _parse(self, text, parseFunction, defaultValue):
        try:
            return parseFunction(text)
        except ValueError:
            return defaultValue


class TemplateXMLReader(XMLReader):
    def __init__(self, *args, **kwargs):
        super(TemplateXMLReader, self).__init__(*args, **kwargs)

        self.__context = dict()
        self.__context.update(date.__dict__)
        self.__context.update(datetime.__dict__)

    def read(self):
        return super(TemplateXMLReader, self).read()[0][0]

    def _parseTaskNode(self, taskNode):
        for name in ['startdate', 'duedate', 'completiondate']:
            if taskNode.hasAttribute(name + 'tmpl'):
                taskNode.setAttribute(name, str(eval(taskNode.getAttribute(name + 'tmpl'), self.__context)))
        return super(TemplateXMLReader, self)._parseTaskNode(taskNode)
