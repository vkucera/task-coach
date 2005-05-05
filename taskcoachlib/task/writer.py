import xml.dom, meta


class XMLWriter:
    def __init__(self, fd, versionnr=7):
        self.__fd = fd
        self.__versionnr = versionnr
        
    def write(self, taskList):
        domImplementation = xml.dom.getDOMImplementation()
        self.document = domImplementation.createDocument(None, 'tasks', None)
        pi = self.document.createProcessingInstruction('taskcoach', 
            'release="%s" tskversion="%d"'%(meta.data.version, self.__versionnr))
        self.document.insertBefore(pi, self.document.documentElement)
        for task in taskList.rootTasks():
            self.document.documentElement.appendChild(self.taskNode(task))
        self.document.writexml(self.__fd)
            
    def taskNode(self, task):
        node = self.document.createElement('task')
        node.setAttribute('subject', task.subject())
        node.setAttribute('startdate', str(task.startDate()))
        node.setAttribute('duedate', str(task.dueDate()))
        node.setAttribute('completiondate', str(task.completionDate()))
        node.setAttribute('budget', self.budgetAsAttribute(task.budget()))
        node.appendChild(self.descriptionNode(task.description()))
        for child in task.children():
            node.appendChild(self.taskNode(child))
        for effort in task.efforts():
            node.appendChild(self.effortNode(effort))
        return node
        
    def effortNode(self, effort):
        node = self.document.createElement('effort')
        node.setAttribute('start', str(effort.getStart()))
        node.setAttribute('stop', str(effort.getStop()))
        node.appendChild(self.descriptionNode(effort.getDescription()))
        return node
        
    def budgetAsAttribute(self, budget):
        return '%d:%02d:%02d'%budget.hoursMinutesSeconds()
        
    def descriptionNode(self, description):
        node = self.document.createElement('description')
        text = self.document.createTextNode(description)
        node.appendChild(text)
        return node