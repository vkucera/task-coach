import xml.dom, meta
import domain.date as date


class XMLWriter:
    def __init__(self, fd, versionnr=14):
        self.__fd = fd
        self.__versionnr = versionnr
        
    def write(self, taskList, categoryContainer):
        domImplementation = xml.dom.getDOMImplementation()
        self.document = domImplementation.createDocument(None, 'tasks', None)
        pi = self.document.createProcessingInstruction('taskcoach', 
            'release="%s" tskversion="%d"'%(meta.data.version, 
            self.__versionnr))
        self.document.insertBefore(pi, self.document.documentElement)
        for task in taskList.rootItems():
            self.document.documentElement.appendChild(self.taskNode(task))
        for category in categoryContainer.rootItems():
            self.document.documentElement.appendChild(self.categoryNode(category, taskList))
        self.document.writexml(self.__fd)
            
    def taskNode(self, task):
        node = self.document.createElement('task')
        node.setAttribute('subject', task.subject())
        node.setAttribute('id', task.id())
        node.setAttribute('lastModificationTime', 
            str(task.lastModificationTime()))
        if task.startDate() != date.Date():
            node.setAttribute('startdate', str(task.startDate()))
        if task.dueDate() != date.Date():
            node.setAttribute('duedate', str(task.dueDate()))
        if task.completionDate() != date.Date():
            node.setAttribute('completiondate', str(task.completionDate()))
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
            node.appendChild(self.textNode('attachment', attachment))
        for child in task.children():
            node.appendChild(self.taskNode(child))
        for effort in task.efforts():
            node.appendChild(self.effortNode(effort))
        return node
        
    def effortNode(self, effort):
        node = self.document.createElement('effort')
        node.setAttribute('start', str(effort.getStart()))
        if effort.getStop() != None:
            node.setAttribute('stop', str(effort.getStop()))
        if effort.getDescription():
            node.appendChild(self.textNode('description', effort.getDescription()))
        return node
    
    def categoryNode(self, category, taskList):
        node = self.document.createElement('category')
        node.setAttribute('subject', category.subject())
        if category.isFiltered():
            node.setAttribute('filtered', str(category.isFiltered()))
        # Make sure the task referenced is actually in the tasklist
        taskIds = ' '.join([task.id() for task in category.tasks() if task in taskList])
        if taskIds:            
            node.setAttribute('tasks', taskIds)
        for child in category.children():
            node.appendChild(self.categoryNode(child, taskList))
        return node
        
    def budgetAsAttribute(self, budget):
        return '%d:%02d:%02d'%budget.hoursMinutesSeconds()
                
    def textNode(self, tagName, text):
        node = self.document.createElement(tagName)
        textNode = self.document.createTextNode(text)
        node.appendChild(textNode)
        return node
