# -*- coding: utf-8 -*-

'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2012 Task Coach developers <developers@taskcoach.org>

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

from .. import sessiontempfile  # pylint: disable-msg=F0401
from taskcoachlib import meta
from taskcoachlib.domain import date, effort, task, category, note, attachment
from taskcoachlib.i18n import translate
from taskcoachlib.syncml.config import SyncMLConfigNode, createDefaultSyncConfig
from taskcoachlib.thirdparty.deltaTime import nlTimeExpression
from taskcoachlib.thirdparty.guid import generate
import StringIO
import os
import re
import stat
import wx
import xml.etree.ElementTree as ET


class PIParser(ET.XMLTreeBuilder):
    """See http://effbot.org/zone/element-pi.htm"""
    def __init__(self):
        ET.XMLTreeBuilder.__init__(self)
        self._parser.ProcessingInstructionHandler = self.handle_pi
        self.tskversion = meta.data.tskversion

    def handle_pi(self, target, data):
        if target == 'taskcoach':
            matchObject = re.search('tskversion="(\d+)"', data)
            self.tskversion = int(matchObject.group(1))


class XMLReaderTooNewException(Exception):
    pass


class XMLReader(object):
    defaultStartTime = (0, 0, 0, 0)
    defaultEndTime = (23, 59, 59, 999999)

    def __init__(self, fd):
        self.__fd = fd
        self.__defaultFontSize = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT).GetPointSize()

    def tskversion(self):
        return self.__tskversion

    def read(self):
        if self._hasBrokenLines():
            self._fixBrokenLines()
        parser = PIParser()
        tree = ET.parse(self.__fd, parser)
        root = tree.getroot()
        self.__tskversion = parser.tskversion  # pylint: disable-msg=W0201
        if self.__tskversion > meta.data.tskversion:
            raise XMLReaderTooNewException  # Version number of task file is too high
        tasks = self._parseTaskNodes(root)
        self._resolvePrerequisitesAndDependencies(tasks)
        categorizables = tasks[:]
        for eachTask in tasks:
            categorizables.extend(eachTask.children(recursive=True))
        for eachTask in tasks:
            categorizables.extend(eachTask.notes(recursive=True))
        notes = self._parseNoteNodes(root)
        categorizables.extend(notes)
        for eachNote in notes:
            categorizables.extend(eachNote.children(recursive=True))
        categorizablesById = dict([(categorizable.id(), categorizable) for \
                                   categorizable in categorizables])
        if self.__tskversion <= 13:
            categories = self._parseCategoryNodesFromTaskNodes(root, 
                                                               categorizablesById)
        else:
            categories = self._parseCategoryNodes(root, categorizablesById)

        guid = self.__parseGUIDNode(root.find('guid'))
        syncMLConfig = self._parseSyncMLNode(root, guid)

        return tasks, categories, notes, syncMLConfig, guid
    
    def _hasBrokenLines(self):
        ''' tskversion 24 may contain newlines in element tags. '''
        hasBrokenLines = '><spds><sources><TaskCoach-\n' in self.__fd.read()
        self.__fd.seek(0)
        return hasBrokenLines
    
    def _fixBrokenLines(self):
        ''' Remove spurious newlines from element tags. '''
        self.__origFd = self.__fd  # pylint: disable-msg=W0201
        self.__fd = StringIO.StringIO()
        lines = self.__origFd.readlines()
        for index in xrange(len(lines)):
            if lines[index].endswith('<TaskCoach-\n') or lines[index].endswith('</TaskCoach-\n'):
                lines[index] = lines[index][:-1]  # Remove newline
                lines[index + 1] = lines[index + 1][:-1]  # Remove newline
        self.__fd.write(''.join(lines))
        self.__fd.seek(0)

    def _parseTaskNodes(self, node):
        return [self._parseTaskNode(child) for child in node.findall('task')]
                
    def _resolvePrerequisitesAndDependencies(self, tasks):
        tasksById = dict()
        
        def collectIds(tasks):
            for each_task in tasks:
                tasksById[each_task.id()] = each_task
                collectIds(each_task.children())
        
        def addPrerequisitesAndDependencies(tasks):
            for each_task in tasks:
                if each_task.isDeleted():
                    # Don't restore prerequisites and dependencies for deleted
                    # tasks
                    for deletedTask in [each_task] + each_task.children(recursive=True):
                        deletedTask.setPrerequisites([])
                    continue
                dummyPrerequisites = each_task.prerequisites()
                prerequisites = set()
                for dummyPrerequisite in dummyPrerequisites:
                    try:
                        prerequisites.add(tasksById[dummyPrerequisite.id])
                    except KeyError:
                        # Release 1.2.11 and older have a bug where tasks can
                        # have prerequisites listed that don't exist anymore
                        pass
                each_task.setPrerequisites(prerequisites)
                for prerequisite in prerequisites:
                    prerequisite.addDependencies([each_task])
                addPrerequisitesAndDependencies(each_task.children())
                
        collectIds(tasks)
        addPrerequisitesAndDependencies(tasks)
                
    def _parseCategoryNodes(self, node, categorizablesById):
        return [self._parseCategoryNode(child, categorizablesById) \
                for child in node.findall('category')]
        
    def _parseNoteNodes(self, node):
        return [self._parseNoteNode(child) for child in node.findall('note')]

    def _parseCategoryNode(self, categoryNode, categorizablesById):
        kwargs = self._parseBaseCompositeAttributes(categoryNode, 
            self._parseCategoryNodes, categorizablesById)
        kwargs.update(dict(\
            notes=self._parseNoteNodes(categoryNode),
            filtered=self._parseBoolean(categoryNode.attrib.get('filtered', 'False')),
            exclusiveSubcategories=self._parseBoolean(categoryNode.attrib.get('exclusiveSubcategories', 'False'))))
        if self.__tskversion < 19:
            categorizableIds = categoryNode.attrib.get('tasks', '')
        else:
            categorizableIds = categoryNode.attrib.get('categorizables', '')
        if categorizableIds:
            # The category tasks attribute might contain id's that refer to tasks that
            # have been deleted (a bug in release 0.61.5), be prepared:
            categorizables = [categorizablesById[categorizableId] for categorizableId in \
                              categorizableIds.split(' ') \
                              if categorizableId in categorizablesById]
        else:
            categorizables = []
        kwargs['categorizables'] = categorizables
        if self.__tskversion > 20:
            kwargs['attachments'] = self._parseAttachmentNodes(categoryNode)
        return category.Category(**kwargs)  # pylint: disable-msg=W0142
                      
    def _parseCategoryNodesFromTaskNodes(self, root, tasks):
        ''' In tskversion <=13 category nodes were subnodes of task nodes. '''
        taskNodes = root.findall('.//task')
        categoryMapping = self._parseCategoryNodesWithinTaskNodes(taskNodes)
        subjectCategoryMapping = {}
        for taskId, categories in categoryMapping.items():
            for subject in categories:
                if subject in subjectCategoryMapping:
                    cat = subjectCategoryMapping[subject]
                else:
                    cat = category.Category(subject)
                    subjectCategoryMapping[subject] = cat
                theTask = tasks[taskId]
                cat.addCategorizable(theTask)
                theTask.addCategory(cat)
        return subjectCategoryMapping.values()
    
    def _parseCategoryNodesWithinTaskNodes(self, taskNodes):
        ''' In tskversion <=13 category nodes were subnodes of task nodes. '''
        categoryMapping = {}
        for node in taskNodes:
            taskId = node.attrib['id']
            categories = [child.text for child in node.findall('category')]
            categoryMapping.setdefault(taskId, []).extend(categories)
        return categoryMapping
        
    def _parseTaskNode(self, taskNode):
        class DummyPrerequisite(object):
            def __init__(self, prerequisite_id):
                self.id = prerequisite_id
                
            def __getattr__(self, attr):
                ''' Ignore all method calls. '''
                return lambda *args, **kwargs: None
            
        plannedStartDateTimeAttributeName = 'startdate' if self.tskversion() <= 33 else 'plannedstartdate'
        kwargs = self._parseBaseCompositeAttributes(taskNode, self._parseTaskNodes)
        kwargs.update(dict(
            plannedStartDateTime=date.parseDateTime(taskNode.attrib.get(plannedStartDateTimeAttributeName, ''), 
                                                    *self.defaultStartTime),
            dueDateTime=date.parseDateTime(taskNode.attrib.get('duedate', ''), 
                                           *self.defaultEndTime),
            actualStartDateTime=date.parseDateTime(taskNode.attrib.get('actualstartdate', ''),
                                                   *self.defaultStartTime),
            completionDateTime=date.parseDateTime(taskNode.attrib.get('completiondate', ''), 
                                                  *self.defaultEndTime),
            percentageComplete=self._parseIntAttribute(taskNode, 'percentageComplete'),
            budget=date.parseTimeDelta(taskNode.attrib.get('budget', '')),
            priority=self._parseIntAttribute(taskNode, 'priority'),
            hourlyFee=float(taskNode.attrib.get('hourlyFee', '0')),
            fixedFee=float(taskNode.attrib.get('fixedFee', '0')),
            reminder=self._parseDateTime(taskNode.attrib.get('reminder', '')),
            reminderBeforeSnooze=self._parseDateTime(taskNode.attrib.get('reminderBeforeSnooze', '')),
            # Here we just add the ids, they will be converted to object references later on:
            prerequisites=[DummyPrerequisite(prerequisite_id) for prerequisite_id in taskNode.attrib.get('prerequisites', '').split(' ') if prerequisite_id], 
            shouldMarkCompletedWhenAllChildrenCompleted= \
                self._parseBoolean(taskNode.attrib.get('shouldMarkCompletedWhenAllChildrenCompleted', '')),
            efforts=self._parseEffortNodes(taskNode),
            notes=self._parseNoteNodes(taskNode),
            recurrence=self._parseRecurrence(taskNode)))
        if self.__tskversion > 20:
            kwargs['attachments'] = self._parseAttachmentNodes(taskNode)
        return task.Task(**kwargs)  # pylint: disable-msg=W0142
        
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
        node = taskNode.find('recurrence')
        if node is not None:
            kwargs = dict(unit=node.attrib.get('unit', ''),
                amount=int(node.attrib.get('amount', '1')),
                count=int(node.attrib.get('count', '0')),
                max=int(node.attrib.get('max', '0')),
                sameWeekday=self._parseBoolean(node.attrib.get('sameWeekday', 'False')),
                recurBasedOnCompletion=self._parseBoolean(node.attrib.get('recurBasedOnCompletion', 'False')))
        return kwargs
                               
    def _parseRecurrenceAttributesFromTaskNode(self, taskNode):
        ''' In tskversion <=19 recurrence information was stored as attributes
            of task nodes. '''
        return dict(unit=taskNode.attrib.get('recurrence', ''),
            count=int(taskNode.attrib.get('recurrenceCount', '0')),
            amount=int(taskNode.attrib.get('recurrenceFrequency', '1')),
            max=int(taskNode.attrib.get('maxRecurrenceCount', '0')))
    
    def _parseNoteNode(self, noteNode):
        ''' Parse the attributes and child notes from the noteNode. '''
        kwargs = self._parseBaseCompositeAttributes(noteNode, self._parseNoteNodes)
        if self.__tskversion > 20:
            kwargs['attachments'] = self._parseAttachmentNodes(noteNode)
        return note.Note(**kwargs) # pylint: disable-msg=W0142
    
    def _parseBaseAttributes(self, node):
        ''' Parse the attributes all composite domain objects share, such as
            id, subject, description, and return them as a 
            keyword arguments dictionary that can be passed to the domain 
            object constructor. '''
        bgColorAttribute = 'color' if self.__tskversion <= 27 else 'bgColor'
        attributes = dict(id=node.attrib.get('id', ''),
            subject=node.attrib.get('subject', ''),
            description=self._parseDescription(node),
            fgColor=self._parseTuple(node.attrib.get('fgColor', ''), None),
            bgColor=self._parseTuple(node.attrib.get(bgColorAttribute, ''), None),
            font=self._parseFontDesc(node.attrib.get('font', '')),
            icon=self._parseIcon(node.attrib.get('icon', '')),
            selectedIcon=self._parseIcon(node.attrib.get('selectedIcon', '')))

        if self.__tskversion <= 20:
            attributes['attachments'] = self._parseAttachmentsBeforeVersion21(node)
        if self.__tskversion >= 22:
            attributes['status'] = int(node.attrib.get('status', '1'))

        return attributes
    
    def _parseBaseCompositeAttributes(self, node, parseChildren, *parseChildrenArgs):
        """Same as _parseBaseAttributes, but also parse children and expandedContexts."""
        kwargs = self._parseBaseAttributes(node)
        kwargs['children'] = parseChildren(node, *parseChildrenArgs)
        kwargs['expandedContexts'] = self._parseTuple(node.attrib.get('expandedContexts', ''), [])
        return kwargs

    def _parseAttachmentsBeforeVersion21(self, parent):
        path, name = os.path.split(os.path.abspath(self.__fd.name)) # pylint: disable-msg=E1103
        name = os.path.splitext(name)[0]
        attdir = os.path.normpath(os.path.join(path, name + '_attachments'))

        attachments = []
        for node in parent.findall('attachment'):
            if self.__tskversion <= 16:
                args = (node.text,)
                kwargs = dict()
            else:
                args = (os.path.join(attdir, node.find('data').text), node.attrib['type'])
                description = self._parseDescription(node)
                kwargs = dict(subject=description,
                              description=description)
            try:
                attachments.append(attachment.AttachmentFactory(*args, **kwargs)) # pylint: disable-msg=W0142
            except IOError:
                # Mail attachment, file doesn't exist. Ignore this.
                pass
        return attachments

    def _parseEffortNodes(self, parent):
        return [self._parseEffortNode(node) for node in parent.findall('effort')]

    def _parseEffortNode(self, effortNode):
        kwargs = {}
        if self.__tskversion >= 22:
            kwargs['status'] = int(effortNode.attrib['status'])
        if self.__tskversion >= 29:
            kwargs['id'] = effortNode.attrib['id']
        start = effortNode.attrib.get('start', '')
        stop = effortNode.attrib.get('stop', '')
        description = self._parseDescription(effortNode)
        # task=None because it is set when the effort is actually added to the
        # task by the task itself. This way no events are sent for changing the
        # effort owner, which is good.
        # pylint: disable-msg=W0142 
        return effort.Effort(task=None, start=date.parseDateTime(start),
            stop=date.parseDateTime(stop), description=description, **kwargs)

    def _parseSyncMLNode(self, nodes, guid):
        syncML = createDefaultSyncConfig(guid)

        nodeName = 'syncmlconfig'
        if self.__tskversion < 25:
            nodeName = 'syncml'

        for node in nodes.findall(nodeName):
            self._parseSyncMLNodes(node, syncML)

        return syncML

    def _parseSyncMLNodes(self, parent, cfgNode):
        for node in parent:
            if node.tag == 'property':
                cfgNode.set(node.attrib['name'], self._parseText(node))
            else:
                for childCfgNode in cfgNode.children():
                    if childCfgNode.name == node.tag:
                        break
                else:
                    tag = node.tag
                    childCfgNode = SyncMLConfigNode(tag)
                    cfgNode.addChild(childCfgNode)
                self._parseSyncMLNodes(node, childCfgNode) # pylint: disable-msg=W0631

    def __parseGUIDNode(self, node):
        guid = self._parseText(node).strip()
        return guid if guid else generate()
        
    def _parseAttachmentNodes(self, parent):
        result = []
        for node in parent.findall('attachment'):
            try:
                result.append(self._parseAttachmentNode(node))
            except IOError:
                pass
        return result

    def _parseAttachmentNode(self, attachmentNode):
        kwargs = self._parseBaseAttributes(attachmentNode)
        kwargs['notes'] = self._parseNoteNodes(attachmentNode)

        if self.__tskversion <= 22:
            path, name = os.path.split(os.path.abspath(self.__fd.name)) # pylint: disable-msg=E1103
            name, ext = os.path.splitext(name)
            attdir = os.path.normpath(os.path.join(path, name + '_attachments'))
            location = os.path.join(attdir, attachmentNode.attrib['location'])
        else:
            if attachmentNode.attrib.has_key('location'):
                location = attachmentNode.attrib['location']
            else:
                dataNode = attachmentNode.find('data')

                if dataNode is None:
                    raise ValueError, 'Neither location or data are defined for this attachment.'

                data = self._parseText(dataNode)
                ext = dataNode.attrib['extension']

                location = sessiontempfile.get_temp_file(suffix=ext)
                file(location, 'wb').write(data.decode('base64'))

                if os.name == 'nt':
                    os.chmod(location, stat.S_IREAD)

        return attachment.AttachmentFactory(location,  # pylint: disable-msg=W0142
                                            attachmentNode.attrib['type'],
                                            **kwargs)

    def _parseDescription(self, node):
        if self.__tskversion <= 6:
            description = node.attrib.get('description', '')
        else:
            description = self._parseText(node.find('description'))
        return description
    
    def _parseText(self, textNode):
        text = u'' if textNode is None else textNode.text or u''
        if self.__tskversion >= 24:
            # Strip newlines
            if text.startswith('\n'):
                text = text[1:]
            if text.endswith('\n'):
                text = text[:-1]
        return text
                    
    def _parseIntAttribute(self, node, attributeName):
        try:
            return int(node.attrib.get(attributeName, '0'))
        except ValueError:
            return 0
        
    def _parseDateTime(self, dateTimeText, *timeDefaults):
        return self._parse(dateTimeText, date.parseDateTime, None, *timeDefaults)
    
    def _parseFontDesc(self, fontDesc, defaultValue=None):
        if fontDesc:
            font = wx.FontFromNativeInfoString(fontDesc)
            if font and font.IsOk():
                if font.GetPointSize() < 4:
                    font.SetPointSize(self.__defaultFontSize)
                return font
        return defaultValue
    
    def _parseIcon(self, icon):
        # Parse is a big word, we just need to fix one particular icon
        return 'clock_alarm_icon' if icon == 'clock_alarm' else icon
    
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
    
    def _parse(self, text, parseFunction, defaultValue, *parseArgs):
        try:
            return parseFunction(text, *parseArgs) if parseArgs else parseFunction(text) 
        except ValueError:
            return defaultValue


class TemplateXMLReader(XMLReader):
    def read(self):
        return super(TemplateXMLReader, self).read()[0][0]

    def _parseTaskNode(self, taskNode):
        attrs = dict()
        attributeRenames = dict(startdate='plannedstartdate')
        for name in ['startdate', 'plannedstartdate', 'duedate', 'completiondate', 'reminder']:
            newName = attributeRenames.get(name, name)
            if taskNode.attrib.has_key(name + 'tmpl'):
                if self.tskversion() < 32:
                    value = TemplateXMLReader.convertOldFormat(taskNode.attrib[name + 'tmpl'])
                else:
                    value = taskNode.attrib[name + 'tmpl']
                attrs[newName] = value
                taskNode.attrib[newName] = str(nlTimeExpression.parseString(value).calculatedTime)
            else:
                attrs[newName] = None
        if taskNode.attrib.has_key('subject'):
            taskNode.attrib['subject'] = translate(taskNode.attrib['subject'])
        parsed_task = super(TemplateXMLReader, self)._parseTaskNode(taskNode)
        for name, value in attrs.items():
            setattr(parsed_task, name + 'tmpl', value)
        return parsed_task

    @staticmethod
    def convertOldFormat(expr, now=date.Now):
        # Built-in templates
        if expr == 'Now()':
            return 'now'
        if expr == 'Now().endOfDay()':
            return '11:59 PM today'
        if expr == 'Now().endOfDay() + oneDay':
            return '11:59 PM tomorrow'
        if expr == 'Today()':
            return '00:00 AM today'
        if expr == 'Tomorrow()':
            return '11:59 PM tomorrow'
        newDateTime = eval(expr, date.__dict__)
        if isinstance(newDateTime, date.date.RealDate):
            newDateTime = date.DateTime(newDateTime.year, newDateTime.month, newDateTime.day)
        delta = newDateTime - now()
        minutes = delta.minutes()
        if minutes < 0:
            return '%d minutes ago' % (-minutes)
        else:
            return '%d minutes from now' % minutes
