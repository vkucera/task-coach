class TaskWriter:
    def __init__(self, fd, versionnr=4):
        import csv
        self.writer = csv.writer(fd)
        self.versionnr = versionnr
        self.version = '.tsk format version %d'%versionnr

    def taskAttributes(self, task):
        childrenIds = [child.id() for child in task.children()]
        attributes = [task.subject()]
        if self.versionnr > 1:
            attributes.append(task.description())
        attributes.extend([task.id(), task.dueDate(), task.startDate(), \
            task.completionDate(), childrenIds])
        return attributes

    def effortAttributes(self, effort):
        return [effort.task().id(), effort.getStart().timetuple(), 
            effort.getStop().timetuple()]
        
    def write(self, taskList, effortList=None):
        self.writer.writerow([self.version])
        for task in taskList:
            self.writer.writerow(self.taskAttributes(task))
        if effortList:
            self.writer.writerow(['effort:'])
            for effort in effortList:
                self.writer.writerow(self.effortAttributes(effort))
                
import xml.dom
class XMLWriter:
    def __init__(self, fd, versionnr=5):
        self.fd = fd
        self.version = '.tsk format version %d'%versionnr
        
    def write(self, taskList, effortList):
        domImplementation = xml.dom.getDOMImplementation()
        self.document = domImplementation.createDocument(None, "tasks", None)
        for task in taskList.rootTasks():
            self.document.documentElement.appendChild(self.taskNode(task))
        self.document.writexml(self.fd, addindent=' ', newl='\n')
            
    def taskNode(self, task):
        node = self.document.createElement("task")
        node.setAttribute("subject", task.subject())
        node.setAttribute("description", task.description())
        node.setAttribute("startdate", str(task.startDate()))
        node.setAttribute("duedate", str(task.dueDate()))
        node.setAttribute("completiondate", str(task.completionDate()))
        if task.children():
            childrenList = self.document.createElement("tasks")
            node.appendChild(childrenList)
            for child in task.children():
                childrenList.appendChild(self.taskNode(child))
        return node
        
