import patterns

class Category(patterns.ObservableComposite):
    def __init__(self, subject, tasks=None, children=None, filtered=False):
        super(Category, self).__init__(children=children or [])
        self.__subject = subject
        self.__tasks = tasks or []
        self.__filtered = filtered
        
    def __repr__(self):
        return self.__subject
            
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.subject(recursive=True) == other.subject(recursive=True)
    
    def subject(self, recursive=False):
        if recursive and self.parent():
            return '%s -> %s'%(self.parent().subject(recursive=True), 
                               self.__subject)
        else:
            return self.__subject
    
    def tasks(self, recursive=False):
        result = []
        if recursive:
            for child in self.children():
                result.extend(child.tasks(recursive))
        result.extend(self.__tasks)
        return result
    
    def addTask(self, task):
        self.__tasks.append(task)
        
    def isFiltered(self):
        return self.__filtered
    
    def setFiltered(self, filtered=True):
        self.__filtered = filtered
        for child in self.children():
            child.setFiltered(filtered)
