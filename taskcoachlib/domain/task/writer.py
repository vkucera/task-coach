import xml.dom, meta


class XMLWriter:
    def __init__(self, fd, versionnr=12):
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
        node.setAttribute('id', task.id())
        node.setAttribute('startdate', str(task.startDate()))
        node.setAttribute('duedate', str(task.dueDate()))
        node.setAttribute('completiondate', str(task.completionDate()))
        node.setAttribute('budget', self.budgetAsAttribute(task.budget()))
        node.setAttribute('priority', str(task.priority()))
        node.setAttribute('lastModificationTime', str(task.lastModificationTime()))
        node.setAttribute('hourlyFee', str(task.hourlyFee()))
        node.setAttribute('fixedFee', str(task.fixedFee()))
        node.setAttribute('reminder', str(task.reminder()))
        node.appendChild(self.textNode('description', task.description()))
        for category in task.categories():
            node.appendChild(self.textNode('category', category))
        for child in task.children():
            node.appendChild(self.taskNode(child))
        for effort in task.efforts():
            node.appendChild(self.effortNode(effort))
        return node
        
    def effortNode(self, effort):
        node = self.document.createElement('effort')
        node.setAttribute('start', str(effort.getStart()))
        node.setAttribute('stop', str(effort.getStop()))
        node.appendChild(self.textNode('description', effort.getDescription()))
        return node
        
    def budgetAsAttribute(self, budget):
        return '%d:%02d:%02d'%budget.hoursMinutesSeconds()
                
    def textNode(self, tagName, text):
        node = self.document.createElement(tagName)
        textNode = self.document.createTextNode(text)
        node.appendChild(textNode)
        return node
