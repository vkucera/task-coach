import time, xml.dom.minidom, re
import domain.date as date
import domain.effort as effort
import task

class XMLReader:
    def __init__(self, fd):
        self.__fd = fd

    def read(self):
        domDocument = xml.dom.minidom.parse(self.__fd)
        self.__tskversion = self.__parseTskVersionNumber(domDocument)
        return self.__parseTaskNodes(domDocument.documentElement.childNodes)

    def __parseTskVersionNumber(self, domDocument):
        processingInstruction = domDocument.firstChild.data
        matchObject = re.search('tskversion="(\d+)"', processingInstruction)
        return int(matchObject.group(1))
        
    def __parseTaskNodes(self, nodes):
        return [self.__parseTaskNode(node) for node in nodes if node.nodeName == 'task']

    def __parseTaskNode(self, taskNode):
        subject = taskNode.getAttribute('subject')
        id = taskNode.getAttribute('id')
        description = self.__parseDescription(taskNode)
        startDate = date.parseDate(taskNode.getAttribute('startdate'))
        dueDate = date.parseDate(taskNode.getAttribute('duedate'))
        completionDate = date.parseDate(taskNode.getAttribute('completiondate'))
        budget = date.parseTimeDelta(taskNode.getAttribute('budget'))
        priority = self.__parseInteger(taskNode.getAttribute('priority'))
        lastModificationTime = self.__parseDateTime(taskNode.getAttribute('lastModificationTime'))
        hourlyFee = self.__parseFloat(taskNode.getAttribute('hourlyFee'))
        fixedFee = self.__parseFloat(taskNode.getAttribute('fixedFee'))
        reminder = self.__parseDateTime(taskNode.getAttribute('reminder'))
        shouldMarkCompletedWhenAllChildrenCompleted = self.__parseBoolean(taskNode.getAttribute('shouldMarkCompletedWhenAllChildrenCompleted'))
        parent = task.Task(subject, description, id_=id, startdate=startDate, duedate=dueDate, 
            completiondate=completionDate, budget=budget, priority=priority, 
            lastModificationTime=lastModificationTime, hourlyFee=hourlyFee,
            fixedFee=fixedFee, reminder=reminder, 
            shouldMarkCompletedWhenAllChildrenCompleted=shouldMarkCompletedWhenAllChildrenCompleted)
        for category in self.__parseCategoryNodes(taskNode.childNodes):
            parent.addCategory(category)
        for child in self.__parseTaskNodes(taskNode.childNodes):
            parent.addChild(child) 
        for effort in self.__parseEffortNodes(parent, taskNode.childNodes):
            parent.addEffort(effort)
        return parent        
        
    def __parseCategoryNodes(self, nodes):
        return [self.__parseCategoryNode(node) for node in nodes if node.nodeName == 'category']
        
    def __parseCategoryNode(self, node):
        return node.firstChild.data
    
    def __parseEffortNodes(self, task, nodes):
        return [self.__parseEffortNode(task, node) for node in nodes if node.nodeName == 'effort']
        
    def __parseEffortNode(self, task, effortNode):
        start = effortNode.getAttribute('start')
        stop = effortNode.getAttribute('stop')
        description = self.__parseDescription(effortNode)
        return effort.Effort(task, date.parseDateTime(start), 
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
    
    def __parseInteger(self, integerText):
        return self.__parse(integerText, int, 0)

    def __parseFloat(self, floatText):
        return self.__parse(floatText, float, 0.0)
                    
    def __parseDateTime(self, dateTimeText):
        return self.__parse(dateTimeText, date.parseDateTime, None)
    
    def __parseBoolean(self, booleanText):
        def textToBoolean(text):
            if text in ['True', 'False']:
                return text == 'True'
            else:
                raise ValueError, "Expected 'True' or 'False'"
        return self.__parse(booleanText, textToBoolean, None)
        
    def __parse(self, text, parseFunction, defaultValue):
        try:
            return parseFunction(text)
        except ValueError:
            return defaultValue
