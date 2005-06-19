import patterns, date, time, copy, sets


class Task(patterns.Observable):
    def __init__(self, subject='', description='', duedate=None, 
            startdate=None, completiondate=None, parent=None, budget=None, 
            priority=None, *args, **kwargs):
        super(Task, self).__init__(*args, **kwargs)
        self._subject        = subject
        self._description    = description 
        self._duedate        = duedate or date.Date()
        self._startdate      = startdate or date.Today()
        self._completiondate = completiondate or date.Date()
        self._budget         = budget or date.TimeDelta()
        self._id             = '%s:%s'%(id(self), time.time())
        self._children       = []
        self._parent         = parent # adding the parent->child link is
                                      # the creator's responsibility
        self._efforts        = []
        self._categories     = sets.Set()
        self._priority       = priority

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
            '_efforts' : self._efforts, '_budget' : self._budget, 
            '_categories': sets.Set(self._categories),
            '_priority': self._priority }
        
    def __repr__(self):
        return self._subject
        
    def __setAttributeAndNotifyObservers(self, attribute, newValue):
        currentValue = getattr(self, attribute)
        if newValue != currentValue:
            setattr(self, attribute, newValue)
            self.notifyObservers(patterns.observer.Notification(self))

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
            self.dueDate(), self.startDate(), parent=self.parent(), 
            budget=self.budget(), priority=self.priority())
        for category in self.categories():
            copy.addCategory(category)
        copy.setCompletionDate(self.completionDate())
        for child in self.children():
            childCopy = child.copy()
            copy.addChild(childCopy)
        return copy
    
    def newSubTask(self, subject='New subtask'):
        ''' Subtask constructor '''
        return self.__class__(subject, duedate=self.dueDate(),
            parent=self)

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
        self.__setAttributeAndNotifyObservers('_subject', subject)

    def dueDate(self, recursive=False):
        if recursive:
            childrenDueDates = [child.dueDate(recursive=True) for child in self.children() if not child.completed()]
            return min(childrenDueDates + [self._duedate])
        else:
            return self._duedate

    def setDueDate(self, duedate):
        self.__setAttributeAndNotifyObservers('_duedate', duedate)

    def startDate(self, recursive=False):
        if recursive:
            childrenStartDates = [child.startDate(recursive=True) for child in self.children() if not child.completed()]
            return min(childrenStartDates+[self._startdate])
        else:
            return self._startdate

    def setStartDate(self, startdate):
        self.__setAttributeAndNotifyObservers('_startdate', startdate)

    def timeLeft(self):
        return self._duedate - date.Today()
        
    def completionDate(self, recursive=False):
        if recursive:
            childrenCompletionDates = [child.completionDate(recursive=True) for child in self.children() if child.completed()]
            return max(childrenCompletionDates+[self._completiondate])
        else:
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
        
    def active(self):
        return not self.inactive() and not self.completed()

    def dueToday(self):
        return (self.dueDate() == date.Today() and not self.completed())

    def dueTomorrow(self):
        return (self.dueDate() == date.Tomorrow() and not self.completed())
    
    # comparison related methods:
        
    def __eq__(self, other):
        return self.id() == other.id()

    def __ne__(self, other):
        return self.id() != other.id()
            
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
        
    def timeSpent(self, recursive=False):
        if recursive:
            return self._myTimeSpent() + self._childrenTimeSpent()
        else:
            return self._myTimeSpent()
    
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
        self.__setAttributeAndNotifyObservers('_budget', budget)
        
    def budgetLeft(self, recursive=False):
        budget = self.budget(recursive)
        if budget:
            return budget - self.timeSpent(recursive)
        else:
            return budget

    def _myTimeSpent(self):
        return sum([effort.duration() for effort in self.efforts()], date.TimeDelta())
    
    def _childrenTimeSpent(self):
        return sum([child.timeSpent(recursive=True) for child in self.children()], date.TimeDelta())
        
    # categories
    
    def categories(self, recursive=False):
        result = sets.Set(self._categories)
        if recursive and self.parent() is not None:
            result |= self.parent().categories(recursive=True)
        return result
        
    def addCategory(self, category):
        self._categories.add(category)
        
    def removeCategory(self, category):
        self._categories.discard(category)
        
    # priority
    
    def priority(self, recursive=False):
        if recursive:
            childPriorities = [child.priority(recursive=True) for child in self.children()]
            priorities = [priority for priority in childPriorities + [self._priority] if priority is not None]
            if priorities:
                return min(priorities)
            else:
                return None
        else:
            return self._priority
        
    def setPriority(self, priority):
        self.__setAttributeAndNotifyObservers('_priority', priority)
