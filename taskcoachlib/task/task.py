from taskcoachlib import patterns, date
import time, copy


class Task(patterns.Observable):
    sep = '|'
   
    def __init__(self, subject='', description='', duedate=None, 
            startdate=None, parent=None, budget=None, *args, **kwargs):
        super(Task, self).__init__(*args, **kwargs)
        self._subject        = subject
        self._description    = description 
        self._duedate        = duedate or date.Date()
        self._startdate      = startdate or date.Today()
        self._completiondate = date.Date()
        self._budget         = budget or date.TimeDelta()
        self._id             = '%s:%s'%(id(self), time.time())
        self._children       = []
        self._parent         = parent # adding the parent->child link is
                                      # the creator's responsibility
        self._efforts        = []

    def onNotify(self, notification, *args, **kwargs):
        notification = patterns.observer.Notification(self,  
            itemsChanged=[notification.source])
        self.notifyObservers(notification, *args, **kwargs)       
        
    def __setstate__(self, state):
        self.__dict__.update(state)
        self.notifyObservers(patterns.observer.Notification(self))

    def __getstate__(self):
        return { '_subject' : self._subject, 
            '_description' : self._description, '_id' : self._id, 
            '_duedate' : self._duedate, '_startdate' : self._startdate, 
            '_completiondate' : self._completiondate,
            '_children' : self._children, '_parent' : self._parent,
            '_efforts' : self._efforts, '_budget' : self._budget }
        
    def __repr__(self):
        return self._subject

    def id(self):
        return self._id

    def children(self):
        return self._children

    def description(self):
        return self._description

    def setDescription(self, description):
        self._description = description

    def allChildrenCompleted(self):
        if not self.children():
            return False
        for child in self.children():
            if not child.completed():
                return False
        return True

    def copy(self):
        ''' Copy constructor '''
        copy = self.__class__(self.subject(), self.description(), 
            self.dueDate(), self.startDate(), parent=self.parent())
        copy.setCompletionDate(self.completionDate())
        for child in self.children():
            childCopy = child.copy()
            copy.addChild(childCopy)
        return copy
    
    def newSubTask(self, subject='New subtask'):
        ''' Subtask constructor '''
        return self.__class__(subject, duedate=self.dueDate(),
            startdate=self.startDate(), parent=self)

    def allChildren(self):
        return self.children() + [descendent for child in self.children() 
                                  for descendent in child.allChildren()]

    def ancestors(self):
        myParent = self.parent()
        if myParent is None:
            return []
        else:
            return myParent.ancestors() + [myParent]

    def family(self):
        return self.ancestors() + [self] + self.allChildren()
        
    def addChild(self, child):
        if child not in self._children:
            self._children.append(child)
            child.setParent(self)
            self._updateCompletionState(child.completionDate())
            child.registerObserver(self.onNotify)
            self.notifyObservers(patterns.observer.Notification(self, childrenAdded=[child]))

    def removeChild(self, child):
        self._children.remove(child)
        if self._children:
            self._updateCompletionState(date.Today())
        child.removeObserver(self.onNotify)
        self.notifyObservers(patterns.observer.Notification(self, childrenRemoved=[child]))

    def setParent(self, parent):
        self._parent = parent

    def parent(self):
        return self._parent

    def subject(self):
        return self._subject

    def setSubject(self, subject):
        if subject != self._subject:
            self._subject = subject
            self.notifyObservers(patterns.observer.Notification(self))

    def dueDate(self):
        if self.children():
            if self.allChildrenCompleted():
                children = self.children()
            else:
                children = [child for child in self.children()
                            if not child.completed()]
            return max([child.dueDate() for child in children])
        else:
            return self._duedate

    def setDueDate(self, duedate):
        if duedate != self._duedate:
            self._duedate = duedate
            self.notifyObservers(patterns.observer.Notification(self))

    def startDate(self):
        if self.children():
            if self.allChildrenCompleted():
                children = self.children()
            else:
                children = [child for child in self.children()
                            if not child.completed()]
            return min([child.startDate() for child in children])
        else:
            return self._startdate

    def setStartDate(self, startdate):
        if startdate != self._startdate:
            self._startdate = startdate
            self.notifyObservers(patterns.observer.Notification(self))

    def timeLeft(self):
        return self._duedate - date.Today()
        
    def completionDate(self):
        return self._completiondate

    def setCompletionDate(self, completionDate=None):
        completionDate = completionDate or date.Today()
        if completionDate == self._completiondate:
            return
        if completionDate != date.Date():
            self.stopTracking()
        self._completiondate = completionDate
        [child.setCompletionDate(completionDate) for child in self.children() 
            if not child.completed()]
        parent = self.parent()
        if parent:
            parent._updateCompletionState(completionDate)
        self.notifyObservers(patterns.observer.Notification(self))

    def _updateCompletionState(self, completionDate):
        if not self.completed() and self.allChildrenCompleted():
            self.setCompletionDate(completionDate)
        elif self.completed() and not self.allChildrenCompleted():
            self.setCompletionDate(date.Date())

    def completed(self):
        return self.completionDate() != date.Date()

    def overdue(self):
        return self.dueDate() < date.Today() and not self.completed()

    def inactive(self):
        return (self.startDate() > date.Today()) and not self.completed()

    def dueToday(self):
        return (self.dueDate() == date.Today() and not self.completed())

    def dueTomorrow(self):
        return (self.dueDate() == date.Tomorrow() and not self.completed())

    
    # comparison related methods:
        
    def _compare(self, other):
        for method in ['completed', 'inactive', 'dueDate', 'startDate',
                       'subject', 'id']:
            result = cmp(getattr(self, method)(), getattr(other, method)())
            if result != 0:
                return result
        return result

    def __eq__(self, other):
        return self.id() == other.id()

    def __ne__(self, other):
        return self.id() != other.id()

    def __lt__(self, other):
        return self._compare(other) < 0

    def __gt__(self, other):
        return self._compare(other) > 0
    
    # effort related methods:

    def efforts(self, recursive=False):
        childEfforts = []
        if recursive:
            for child in self.children():
                childEfforts.extend(child.efforts(recursive=True))
        return self._efforts + childEfforts
        
    def addEffort(self, effort):
        self._efforts.append(effort)
        effort.registerObserver(self.notifyEffortChanged)
        self.notifyObservers(patterns.observer.Notification(self, effortsAdded=[effort]))
        
    def removeEffort(self, effort):
        self._efforts.remove(effort)
        effort.removeObserver(self.notifyEffortChanged)
        self.notifyObservers(patterns.observer.Notification(self, effortsRemoved=[effort]))
        
    def notifyEffortChanged(self, notification, *args, **kwargs):
        notification = patterns.observer.Notification(self, effortsChanged=[notification.source])
        self.notifyObservers(notification)
        
    def duration(self, recursive=False):
        if recursive:
            return self._myDuration() + self._childrenDuration()
        else:
            return self._myDuration()
    
    def stopTracking(self):
        stoppedEfforts = []
        for effort in self.efforts():
            if effort.getStop() is None:
                effort.setStop()
                stoppedEfforts.append(effort)
        return stoppedEfforts
                
    def isBeingTracked(self):
        for effort in self.efforts():
            if effort.getStop() is None:
                return True
        return False
        
    def budget(self, recursive=False):
        result = self._budget
        if recursive:
            for task in self.children():
                result += task.budget(recursive)
        return result
        
    def setBudget(self, budget):
        self._budget = budget
        self.notifyObservers(patterns.observer.Notification(self))
        
    def budgetLeft(self, recursive=False):
        budget = self.budget(recursive)
        if budget:
            return budget - self.duration(recursive)
        else:
            return budget

    def _myDuration(self):
        return sum([effort.duration() for effort in self.efforts()], date.TimeDelta())
    
    def _childrenDuration(self):
        return sum([child.duration(recursive=True) for child in self.children()], date.TimeDelta())
        