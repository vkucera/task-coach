import time, xml.dom.minidom, re, os
from domain import date, effort, task, category, note, attachment


class XMLReader:
    def __init__(self, fd):
        self.__fd = fd

        # Determine where are attachments.
        path, name = os.path.split(os.path.abspath(self.__fd.name))
        name, ext = os.path.splitext(name)
        attdir = os.path.normpath(os.path.join(path, name + '_attachments'))
        attachment.MailAttachment.attdir = attdir

    def read(self):
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
                
    def __parseCategoryNodes(self, nodes, tasks):
        return [self.__parseCategoryNode(node, tasks) for node in nodes \
                if node.nodeName == 'category']
        
    def __parseNoteNodes(self, nodes):
        return [self.__parseNoteNode(node) for node in nodes \
                if node.nodeName == 'note']

    def __parseCategoryNode(self, categoryNode, categorizablesById):        
        subject = categoryNode.getAttribute('subject')
        categoryId = categoryNode.getAttribute('id')
        description = self.__parseDescription(categoryNode)
        filtered = self.__parseBoolean(categoryNode.getAttribute('filtered'), 
                                       False)
        color = self.__parseTuple(categoryNode.getAttribute('color'), None)
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
        children = self.__parseCategoryNodes(categoryNode.childNodes, categorizablesById)
        return category.Category(subject, categorizables, children, filtered, 
                                 id=categoryId, description=description, color=color)
                      
    def __parseCategoryNodesFromTaskNodes(self, document, tasks):
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
        categoryMapping = {}
        for node in taskNodes:
            taskId = node.getAttribute('id')
            categories = [self.__parseTextNode(node) for node in node.childNodes \
                          if node.nodeName == 'category']
            categoryMapping.setdefault(taskId, []).extend(categories)
        return categoryMapping
        
    def __parseTaskNode(self, taskNode):
        kwargs = dict(subject=taskNode.getAttribute('subject'),
            description=self.__parseDescription(taskNode),
            id=taskNode.getAttribute('id'),
            startDate=date.parseDate(taskNode.getAttribute('startdate')),
            dueDate=date.parseDate(taskNode.getAttribute('duedate')),
            completionDate=date.parseDate(taskNode.getAttribute('completiondate')),
            recurrence=taskNode.getAttribute('recurrence'),
            recurrenceCount=self.__parseInteger(taskNode.getAttribute('recurrenceCount')),
            maxRecurrenceCount=self.__parseInteger(taskNode.getAttribute('maxRecurrenceCount')),
            budget=date.parseTimeDelta(taskNode.getAttribute('budget')),
            priority=self.__parseInteger(taskNode.getAttribute('priority')),
            hourlyFee=self.__parseFloat(taskNode.getAttribute('hourlyFee')),
            fixedFee=self.__parseFloat(taskNode.getAttribute('fixedFee')),
            reminder=self.__parseDateTime(taskNode.getAttribute('reminder')),
            attachments=self.__parseAttachmentNodes(taskNode.childNodes),
            shouldMarkCompletedWhenAllChildrenCompleted= \
                self.__parseBoolean(taskNode.getAttribute('shouldMarkCompletedWhenAllChildrenCompleted')),
            children=self.__parseTaskNodes(taskNode.childNodes),
            efforts=self.__parseEffortNodes(taskNode.childNodes))
        if self.__tskversion <= 13:
            kwargs['categories'] = self.__parseCategoryNodesWithinTaskNode(taskNode.childNodes)
        else:
            kwargs['categories'] = []
        return task.Task(**kwargs)
    
    def __parseNoteNode(self, noteNode):
        kwargs = dict(subject=noteNode.getAttribute('subject'),
            id=noteNode.getAttribute('id'),
            description=self.__parseDescription(noteNode),
            children=self.__parseNoteNodes(noteNode.childNodes))
        return note.Note(**kwargs)
        
    def __parseCategoryNodesWithinTaskNode(self, nodes):
        return [self.__parseTextNode(node) for node in nodes \
                if node.nodeName == 'category']
        
    def __parseAttachmentNodes(self, nodes):
        attachments = []
        for node in nodes:
            if node.nodeName == 'attachment':
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
        return effort.Effort(None, date.parseDateTime(start), 
            date.parseDateTime(stop), description)
        
    def __getNode(self, parent, tagName):
        for child in parent.childNodes:
            if child.nodeName == tagName:
                return child
        return None        
        
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
    
    def __parseTextNode(self, node):
        return node.firstChild.data
    
    def __parseInteger(self, integerText):
        return self.__parse(integerText, int, 0)

    def __parseFloat(self, floatText):
        return self.__parse(floatText, float, 0.0)
                    
    def __parseDateTime(self, dateTimeText):
        return self.__parse(dateTimeText, date.parseDateTime, None)
    
    def __parseBoolean(self, booleanText, defaultValue=None):
        def textToBoolean(text):
            if text in ['True', 'False']:
                return text == 'True'
            else:
                raise ValueError, "Expected 'True' or 'False'"
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
