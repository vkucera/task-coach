class Category(object):
    def __init__(self, subject, tasks=None, children=None):
        self.__subject = subject
        self.__parent = None
        self.__tasks = tasks or []
        self.__children = children or []
        for child in self.__children:
            child.setParent(self)
            
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
    
    def tasks(self):
        return self.__tasks
    
    def addTask(self, task):
        self.__tasks.append(task)
    
    def setParent(self, parent):
        self.__parent = parent
        
    def parent(self):
        return self.__parent
            
    def addChild(self, category):
        self.__children.append(category)
        category.setParent(self)
        
    def children(self):
        return self.__children