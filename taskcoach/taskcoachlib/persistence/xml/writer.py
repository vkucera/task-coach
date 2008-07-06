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

import xml.dom, os
from taskcoachlib import meta
from taskcoachlib.domain import date, attachment


class XMLWriter:    
    def __init__(self, fd, versionnr=21):
        self.__fd = fd
        self.__versionnr = versionnr

        # Determine where to save attachments.
        path, name = os.path.split(os.path.abspath(self.__fd.name))
        name, ext = os.path.splitext(name)
        attdir = os.path.normpath(os.path.join(path, name + '_attachments'))
        attachment.MailAttachment.attdir = attdir

    def write(self, taskList, categoryContainer, noteContainer):
        domImplementation = xml.dom.getDOMImplementation()
        self.document = domImplementation.createDocument(None, 'tasks', None)
        pi = self.document.createProcessingInstruction('taskcoach', 
            'release="%s" tskversion="%d"'%(meta.data.version, 
            self.__versionnr))
        self.document.insertBefore(pi, self.document.documentElement)
        for task in taskList.rootItems():
            self.document.documentElement.appendChild(self.taskNode(task))
        for category in categoryContainer.rootItems():
            self.document.documentElement.appendChild(self.categoryNode(category, taskList, noteContainer))
        for note in noteContainer.rootItems():
            self.document.documentElement.appendChild(self.noteNode(note))
        self.document.writexml(self.__fd)

    def taskNode(self, task):
        node = self.document.createElement('task')
        node.setAttribute('subject', task.subject())
        node.setAttribute('id', task.id())
        node.setAttribute('status', str(task.getStatus()))
        if task.startDate() != date.Date():
            node.setAttribute('startdate', str(task.startDate()))
        if task.dueDate() != date.Date():
            node.setAttribute('duedate', str(task.dueDate()))
        if task.completionDate() != date.Date():
            node.setAttribute('completiondate', str(task.completionDate()))
        if task.recurrence():
            node.setAttribute('recurrence', task.recurrence()) 
        if task.recurrenceCount():
            node.setAttribute('recurrenceCount', str(task.recurrenceCount()))
        if task.maxRecurrenceCount():
            node.setAttribute('maxRecurrenceCount', str(task.maxRecurrenceCount()))
        if task.budget() != date.TimeDelta():
            node.setAttribute('budget', self.budgetAsAttribute(task.budget()))
        if task.priority() != 0:
            node.setAttribute('priority', str(task.priority()))
        if task.hourlyFee() != 0:
            node.setAttribute('hourlyFee', str(task.hourlyFee()))
        if task.fixedFee() != 0:
            node.setAttribute('fixedFee', str(task.fixedFee()))
        if task.reminder() != None:
            node.setAttribute('reminder', str(task.reminder()))
        if task.shouldMarkCompletedWhenAllChildrenCompleted != None:
            node.setAttribute('shouldMarkCompletedWhenAllChildrenCompleted', 
                              str(task.shouldMarkCompletedWhenAllChildrenCompleted))
        if task.description():
            node.appendChild(self.textNode('description', task.description()))
        for attachment in task.attachments():
            node.appendChild(self.attachmentNode(attachment))
        for child in task.children():
            node.appendChild(self.taskNode(child))
        for effort in task.efforts():
            node.appendChild(self.effortNode(effort))
        return node

    def attachmentNode(self, att):
        node = self.document.createElement('attachment')
        node.setAttribute('type', att.type_)
        node.appendChild(self.textNode('description', unicode(att)))
        node.appendChild(self.textNode('data', att.data()))
        return node

    def effortNode(self, effort):
        node = self.document.createElement('effort')
        formattedStart = self.formatDateTime(effort.getStart())
        node.setAttribute('status', str(effort.getStatus()))
        node.setAttribute('start', formattedStart)
        stop = effort.getStop()
        if stop != None:
            formattedStop = self.formatDateTime(stop)
            if formattedStop == formattedStart:
                # Make sure the effort duration is at least one second
                formattedStop = self.formatDateTime(stop + date.TimeDelta(seconds=1))
            node.setAttribute('stop', formattedStop)
        if effort.getDescription():
            node.appendChild(self.textNode('description', effort.getDescription()))
        return node
    
    def categoryNode(self, category, *categorizableContainers):
        def inCategorizableContainer(categorizable):
            for container in categorizableContainers:
                if categorizable in container:
                    return True
            return False
        node = self.document.createElement('category')
        node.setAttribute('subject', category.subject())
        node.setAttribute('id', category.id())
        if category.description():
            node.appendChild(self.textNode('description', category.description()))
        if category.isFiltered():
            node.setAttribute('filtered', str(category.isFiltered()))
        if category.color():
            node.setAttribute('color', str(category.color()))
        # Make sure the categorizables referenced are actually in the 
        # categorizableContainer, i.e. they are not deleted
        categorizableIds = ' '.join([categorizable.id() for categorizable in \
            category.categorizables() if inCategorizableContainer(categorizable)])
        if categorizableIds:            
            node.setAttribute('categorizables', categorizableIds)
        for child in category.children():
            node.appendChild(self.categoryNode(child, *categorizableContainers))
        return node
    
    def noteNode(self, note):
        node = self.document.createElement('note')
        node.setAttribute('id', note.id())
        node.setAttribute('status', str(note.getStatus()))
        if note.subject():
            node.setAttribute('subject', note.subject())
        if note.description():
            node.appendChild(self.textNode('description', note.description()))
        for child in note.children():
            node.appendChild(self.noteNode(child))
        return node
        
    def budgetAsAttribute(self, budget):
        return '%d:%02d:%02d'%budget.hoursMinutesSeconds()
                
    def textNode(self, tagName, text):
        node = self.document.createElement(tagName)
        textNode = self.document.createTextNode(text)
        node.appendChild(textNode)
        return node

    def formatDateTime(self, dateTime):
        return dateTime.strftime('%Y-%m-%d %H:%M:%S')
