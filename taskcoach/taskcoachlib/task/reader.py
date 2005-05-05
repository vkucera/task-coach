import date, task, datetime, time, effort, xml.dom.minidom, re

class TaskFactory:
    def __init__(self, versionnr):
        self.versionnr = versionnr

    def createTask(self, line):
        nrTimeEntries = "0"
        description = ''
        if self.versionnr > 3:
            subject, description, id, dueDate, startDate, completionDate, childrenIds = line
        elif self.versionnr > 2:
            subject, description, id, dueDate, startDate, completionDate, childrenIds, nrTimeEntries = line
        elif self.versionnr > 1:
            subject, description, id, dueDate, startDate, completionDate, childrenIds = line
        else:
            subject, id, dueDate, startDate, completionDate, childrenIds = line

        childrenIds = eval(childrenIds) # FIXME: safety issue?
        dueDate = date.parseDate(dueDate)
        startDate = date.parseDate(startDate)
        completionDate = date.parseDate(completionDate)
        newTask = task.Task(subject=subject, description=description, 
            duedate=dueDate, startdate=startDate)
        newTask.setCompletionDate(completionDate)
        newTask._id = id
        newTask.IdsOfChildrenToAdd = childrenIds
        nrTimeEntries = int(nrTimeEntries)
        return newTask, nrTimeEntries


class TaskReader:
    datetimefmt = '%Y-%m-%d %H:%M:%S'
    
    def __init__(self, fd):
        import csv
        self.reader = csv.reader(fd)

    def createTasks(self, versionnr):
        taskFactory = TaskFactory(versionnr)
        nrTimeEntriesToRead = 0
        for line in self.reader:
            if line == []:
                continue
            if line == ['effort:']:
                return
            if nrTimeEntriesToRead > 0:
                task.addEffort(self.createEffort(task, line))
                nrTimeEntriesToRead -= 1
            else:
                (task, nrTimeEntriesToRead) = taskFactory.createTask(line)
                self.taskList.append(task)
                self.taskDict[task.id()] = task

    def createEffort(self, task, line):
        start, stop = line
        start = self.createDateTime(start)
        stop = self.createDateTime(stop)
        return effort.Effort(task, start, stop)
    
    def createEfforts(self, versionnr):
        if versionnr <=3:
            return
        for line in self.reader:
            if line == []:
                continue
            if versionnr <= 4:
                taskId, start, stop = line
                description = ''
            else:
                taskId, start, stop, description = line
            task = self.taskDict[taskId]
            newEffort = effort.Effort(task, self.createDateTime(start),
                self.createDateTime(stop), description)
            task.addEffort(newEffort)
            
    def createDateTime(self, string):
        if not string:
            return None
        else:
            return date.DateTime.fromtimestamp(time.mktime(eval(string)))
                
    def createChildren(self):
        for task in self.taskList:
            for childId in task.IdsOfChildrenToAdd:
                task.addChild(self.taskDict[childId])
            del task.IdsOfChildrenToAdd
 
    def read(self):
        self.taskList = []
        self.taskDict = {}
        self.version = self.reader.next()[0]
        versionnr = int(self.version.split()[-1])
        self.createTasks(versionnr)
        self.createChildren()
        self.createEfforts(versionnr)
        tasks = [task for task in self.taskList if task.parent() is None]
        return tasks


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
        description = self.__parseDescription(taskNode)
        startDate = date.parseDate(taskNode.getAttribute('startdate'))
        dueDate = date.parseDate(taskNode.getAttribute('duedate'))
        completionDate = date.parseDate(taskNode.getAttribute('completiondate'))
        budget = date.parseTimeDelta(taskNode.getAttribute('budget'))
        parent = task.Task(subject, description, startdate=startDate, duedate=dueDate, 
            completiondate=completionDate, budget=budget)
        for child in self.__parseTaskNodes(taskNode.childNodes):
            parent.addChild(child) 
        for effort in self.__parseEffortNodes(parent, taskNode.childNodes):
            parent.addEffort(effort)
        return parent        
        
    def __parseEffortNodes(self, task, nodes):
        return [self.__parseEffortNode(task, node) for node in nodes if node.nodeName == 'effort']
        
    def __parseEffortNode(self, task, effortNode):
        start = effortNode.getAttribute('start')
        stop = effortNode.getAttribute('stop')
        description = self.__parseDescription(effortNode)
        #description = effortNode.getAttribute('description')
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
        