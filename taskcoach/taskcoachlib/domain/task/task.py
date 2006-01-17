import patterns, time, copy, sets
import domain.date as date


class TaskProperty(property):
    pass

class Task(patterns.Observable):
    def __init__(self, subject='', description='', duedate=None, 
            startdate=None, completiondate=None, parent=None, budget=None, 
            priority=0, id_=None, lastModificationTime=None, hourlyFee=0,
            fixedFee=0, reminder=None, *args, **kwargs):
        super(Task, self).__init__(*args, **kwargs)
        self._subject        = subject
        self._description    = description 
        self._duedate        = duedate or date.Date()
        self._startdate      = startdate or date.Today()
        self._completiondate = completiondate or date.Date()
        self._budget         = budget or date.TimeDelta()
        self._id             = id_ or '%s:%s'%(id(self), time.time()) # FIXME: Npt a valid XML id
        self._children       = []
        self._parent         = parent # adding the parent->child link is
                                      # the creator's responsibility
        self._efforts        = []
        self._categories     = sets.Set()
        self._priority       = priority
        self._hourlyFee      = hourlyFee
        self._fixedFee       = fixedFee
        self._reminder       = None
        self.setReminder(reminder)
        self.setLastModificationTime(lastModificationTime)
            
    def onNotify(self, notification, *args, **kwargs):
        notification = patterns.observer.Notification(self,  
            itemsChanged=[notification.source], effortsChanged=notification.effortsChanged)
        self.notifyObservers(notification, *args, **kwargs)       
    
    def notifyObservers(self, notification, *args, **kwargs):
        if notification.changeNeedsSave:
            self.setLastModificationTime()
        super(Task, self).notifyObservers(notification, *args, **kwargs)

    def __setstate__(self, state):
        for attribute, newValue in state.items():
            self.__setAttributeAndNotifyObservers(attribute, newValue)
            
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
            completionDateChanged = attribute == '_completiondate'
            dueDateChanged = attribute == '_duedate'
            startDateChanged = attribute == '_startdate'
            notification = patterns.Notification(self, dueDateChanged=dueDateChanged, 
                completionDateChanged=completionDateChanged, startDateChanged=startDateChanged,
                changeNeedsSave=True)
            self.notifyObservers(notification)

    def id(self):
        return self._id

    def children(self, recursive=False):
        if recursive:
            return self.allChildren()
        else:
            return self._children
        
    def __getDescription(self):
        return self.__description
    
    def __setDescription(self, description):
        self.__description = description
        
    _description = TaskProperty(__getDescription, __setDescription)

    def description(self):
        return self._description

    def setDescription(self, description):
        self.__setAttributeAndNotifyObservers('_description', description)
    
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
            startdate=max(date.Today(), self.startDate()), parent=self)

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
            child.registerObserver(self.onNotify)
            self.notifyObservers(patterns.Notification(self, changeNeedsSave=True, childAdded=child))

    def removeChild(self, child):
        self._children.remove(child)
        child.removeObserver(self.onNotify)
        self.notifyObservers(patterns.Notification(self, changeNeedsSave=True, childRemoved=child))

    def setParent(self, parent):
        self._parent = parent

    def parent(self):
        return self._parent

    def subject(self, recursive=False):
        ''' The recursive flag is allowed, but ignored. This makes 
            task.sorter.Sorter.__createRegularSortKey easier. '''
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

    def timeLeft(self, recursive=False):
        return self.dueDate(recursive) - date.Today()
        
    def completionDate(self, recursive=False):
        if recursive:
            childrenCompletionDates = [child.completionDate(recursive=True) for child in self.children() if child.completed()]
            return max(childrenCompletionDates+[self._completiondate])
        else:
            return self._completiondate

    def setCompletionDate(self, completionDate=None):
        completionDate = completionDate or date.Today()
        self.__setAttributeAndNotifyObservers('_completiondate', completionDate)
        
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
    
   # effort related methods:

    def efforts(self, recursive=False):
        childEfforts = []
        if recursive:
            for child in self.children():
                childEfforts.extend(child.efforts(recursive=True))
        return self._efforts + childEfforts
        
    def addEffort(self, effort):
        if effort not in self._efforts:
            self._efforts.append(effort)
            effort.registerObserver(self.notifyEffortChanged)
            self.notifyObservers(patterns.Notification(self, changeNeedsSave=True, effortsAdded=[effort]))
        
    def removeEffort(self, effort):
        self._efforts.remove(effort)
        effort.removeObserver(self.notifyEffortChanged)
        self.notifyObservers(patterns.Notification(self, changeNeedsSave=True, effortsRemoved=[effort]))
        
    def notifyEffortChanged(self, notification, *args, **kwargs):
        if notification.source.task() != self:
            self.removeEffort(notification.source)
        else:
            notification['effortsChanged'] = [notification.source]
            notification['source'] = self
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
        self.notifyObservers(patterns.observer.Notification(self, changeNeedsSave=True, categoriesAdded=[category]))
        
    def removeCategory(self, category):
        self._categories.discard(category)
        self.notifyObservers(patterns.observer.Notification(self, changeNeedsSave=True, categoriesRemoved=[category]))

    # priority
    
    def priority(self, recursive=False):
        if recursive:
            childPriorities = [child.priority(recursive=True) for child in self.children()]
            return max(childPriorities + [self._priority])
        else:
            return self._priority
        
    def setPriority(self, priority):
        self.__setAttributeAndNotifyObservers('_priority', priority)
        
    # modifications
    
    def lastModificationTime(self, recursive=False):
        if recursive:
            childModificationTimes = [child.lastModificationTime(recursive=True) for child in self.children()]
            return max(childModificationTimes + [self._lastModificationTime])
        else:
            return self._lastModificationTime

    def setLastModificationTime(self, time=None):
        self._lastModificationTime = time or date.DateTime.now()

    # revenue
    
    def hourlyFee(self, recursive=False):
        return self._hourlyFee
    
    def setHourlyFee(self, hourlyFee):
        self.__setAttributeAndNotifyObservers('_hourlyFee', hourlyFee)
        
    def revenue(self, recursive=False):
        if recursive:
            childRevenues = sum(child.revenue(recursive) for child in self.children())
        else:
            childRevenues = 0
        return self.timeSpent().hours() * self.hourlyFee() + self.fixedFee() + childRevenues
    
    def fixedFee(self, recursive=False):
        if recursive:
            childFixedFees = sum(child.fixedFee(recursive) for child in self.children())
        else:
            childFixedFees = 0
        return self._fixedFee + childFixedFees
    
    def setFixedFee(self, fixedFee):
        self.__setAttributeAndNotifyObservers('_fixedFee', fixedFee)
        
    # reminder
    
    def reminder(self):
        return self._reminder

    def setReminder(self, reminderDateTime=None):
        clock = date.Clock()
        if self._reminder:
            clock.removeObserver(self.onReminder)
        self.__setAttributeAndNotifyObservers('_reminder', reminderDateTime)
        if self._reminder:
            clock.registerObserver(self.onReminder, self._reminder)
        
    def onReminder(self, *args, **kwargs):
        self.notifyObservers(patterns.Notification(self), 'reminder')