import date, task, datetime, time, effort

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
            taskId, start, stop = line
            task = self.taskDict[taskId]
            newEffort = effort.Effort(task, self.createDateTime(start),
                self.createDateTime(stop))
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

