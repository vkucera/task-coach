import patterns, time, copy
import domain.date as date


class TaskProperty(property):
    pass

class Task(object):
    def __init__(self, subject='', description='', dueDate=None, 
            startDate=None, completionDate=None, parent=None, budget=None, 
            priority=0, id_=None, lastModificationTime=None, hourlyFee=0,
            fixedFee=0, reminder=None, attachments=None, categories=None,
            children=None, efforts=None,
            shouldMarkCompletedWhenAllChildrenCompleted=None, *args, **kwargs):
        super(Task, self).__init__(*args, **kwargs)
        self._subject        = subject
        self._description    = description 
        self._dueDate        = dueDate or date.Date()
        self._startDate      = startDate or date.Today()
        self._completionDate = completionDate or date.Date()
        self._budget         = budget or date.TimeDelta()
        self._id             = id_ or '%s:%s'%(id(self), time.time()) # FIXME: Not a valid XML id
        self._children       = children or []
        for child in self._children:
            child.setParent(self)
        self._parent         = parent # adding the parent->child link is
                                      # the creator's responsibility
        self._efforts        = efforts or []
        for effort in self._efforts:
            effort.setTask(self)
        self._categories     = set(categories or [])
        self._priority       = priority
        self._hourlyFee      = hourlyFee
        self._fixedFee       = fixedFee
        self._reminder       = reminder
        self._attachments    = attachments or []
        self._shouldMarkCompletedWhenAllChildrenCompleted = \
            shouldMarkCompletedWhenAllChildrenCompleted
        self.setLastModificationTime(lastModificationTime)
            
    def __setstate__(self, state):
        self.setSubject(state['subject'])
        self.setDescription(state['description'])
        self.setId(state['id'])
        self.setStartDate(state['startDate'])
        self.setDueDate(state['dueDate'])
        self.setCompletionDate(state['completionDate'])
        self.setChildren(state['children'])
        self.setParent(state['parent'])
        self.setEfforts(state['efforts'])
        self.setBudget(state['budget'])
        self.setCategories(state['categories'])
        self.setPriority(state['priority'])
        self.setAttachments(state['attachments'])
        self.setHourlyFee(state['hourlyFee'])
        self.setFixedFee(state['fixedFee'])
        self.shouldMarkCompletedWhenAllChildrenCompleted = \
            state['shouldMarkCompletedWhenAllChildrenCompleted']
            
    def __getstate__(self):
        return dict(subject=self._subject, description=self._description, 
            id=self._id, dueDate=self._dueDate, startDate=self._startDate, 
            completionDate=self._completionDate, children=self._children, 
            parent=self._parent, efforts=self._efforts, budget=self._budget, 
            categories=set(self._categories), priority=self._priority, 
            attachments=self._attachments[:], hourlyFee=self._hourlyFee, 
            fixedFee=self._fixedFee, 
            shouldMarkCompletedWhenAllChildrenCompleted=\
                self._shouldMarkCompletedWhenAllChildrenCompleted)
        
    def __repr__(self):
        return self._subject
        
    def id(self):
        return self._id

    def setId(self, id):
        self._id = id
    
    def __notifyObservers(self, event):
        patterns.Publisher().notifyObservers(event)

    def children(self, recursive=False):
        if recursive:
            return self.children() + [descendent for child in self.children() 
                for descendent in child.children(recursive=True)]
        else:
            return self._children
    
    # I want to use properties more, but I still need to make all the changes.
    # So, only description is a property right now.
        
    def __getDescription(self):
        return self.__description
    
    def __setDescription(self, description):
        self.__description = description
        
    _description = TaskProperty(__getDescription, __setDescription)

    def description(self):
        return self._description

    def setDescription(self, description):
        if description != self._description:
            self._description = description
            self.setLastModificationTime()
            self.__notifyObservers(patterns.Event(self, 'task.description', 
                description))
    
    def allChildrenCompleted(self):
        if not self.children():
            return False
        for child in self.children():
            if not child.completed():
                return False
        return True

    def copy(self):
        ''' Copy constructor '''
        return self.__class__(self.subject(), self.description(), 
            self.dueDate(), self.startDate(), self.completionDate(),
            parent=self.parent(), 
            budget=self.budget(), priority=self.priority(), 
            categories=set(self.categories()), fixedFee=self.fixedFee(),
            hourlyFee=self.hourlyFee(), attachments=self.attachments()[:],
            reminder=self.reminder(), 
            shouldMarkCompletedWhenAllChildrenCompleted=\
                self.shouldMarkCompletedWhenAllChildrenCompleted,
            children=[child.copy() for child in self.children()])
    
    def newSubTask(self, subject='New subtask'):
        ''' Subtask constructor '''
        return self.__class__(subject, dueDate=self.dueDate(),
            startDate=max(date.Today(), self.startDate()), parent=self)

    def ancestors(self):
        myParent = self.parent()
        if myParent is None:
            return []
        else:
            return myParent.ancestors() + [myParent]

    def family(self):
        return self.ancestors() + [self] + self.children(recursive=True)

    def setChildren(self, children):
        self._children = children # FIXME: no notification?
        
    def addChild(self, child):
        if child in self._children:
            return
        oldTotalBudgetLeft = self.budgetLeft(recursive=True)
        oldTotalPriority = self.priority(recursive=True)
        self._children.append(child)
        child.setParent(self)
        self.setLastModificationTime()
        self.__notifyObservers(patterns.Event(self, 'task.child.add', child))
        newTotalBudgetLeft = self.budgetLeft(recursive=True)
        if child.budget(recursive=True):
            self.notifyObserversOfTotalBudgetChange()
        if newTotalBudgetLeft != oldTotalBudgetLeft:
            self.notifyObserversOfTotalBudgetLeftChange()
        if child.timeSpent(recursive=True):
            self.notifyObserversOfTotalTimeSpentChange()
        if child.priority(recursive=True) > oldTotalPriority:
            self.notifyObserversOfTotalPriorityChange()
        if child.revenue(recursive=True):
            self.notifyObserversOfTotalRevenueChange()
        if child.isBeingTracked(recursive=True):
            self.notifyObserversOfStartTracking(*child.activeEfforts(recursive=True))

    def removeChild(self, child):
        if child not in self._children:
            return
        oldTotalBudgetLeft = self.budgetLeft(recursive=True)
        oldTotalPriority = self.priority(recursive=True)
        self._children.remove(child)
        self.setLastModificationTime()
        self.__notifyObservers(patterns.Event(self, 'task.child.remove', child))
        newTotalBudgetLeft = self.budgetLeft(recursive=True)
        if child.budget(recursive=True):
            self.notifyObserversOfTotalBudgetChange()
        if newTotalBudgetLeft != oldTotalBudgetLeft:
            self.notifyObserversOfTotalBudgetLeftChange()
        if child.timeSpent(recursive=True):
            self.notifyObserversOfTotalTimeSpentChange()
        if child.priority(recursive=True) == oldTotalPriority:
            self.notifyObserversOfTotalPriorityChange()
        if child.revenue(recursive=True):
            self.notifyObserversOfTotalRevenueChange()
        if child.isBeingTracked(recursive=True) and not \
            self.isBeingTracked(recursive=True):
            self.notifyObserversOfStopTracking(*child.activeEfforts(recursive=True))

    def setParent(self, parent):
        self._parent = parent

    def parent(self):
        return self._parent

    def subject(self, recursive=False):
        ''' The recursive flag is allowed, but ignored. This makes 
            task.sorter.Sorter.__createRegularSortKey easier. '''
        return self._subject

    def setSubject(self, subject):
        if subject != self._subject:
            self._subject = subject
            self.setLastModificationTime()
            self.__notifyObservers(patterns.Event(self, 'task.subject', subject))

    def dueDate(self, recursive=False):
        if recursive:
            childrenDueDates = [child.dueDate(recursive=True) for child in self.children() if not child.completed()]
            return min(childrenDueDates + [self._dueDate])
        else:
            return self._dueDate

    def setDueDate(self, dueDate):
        if dueDate != self._dueDate:
            self._dueDate = dueDate
            self.setLastModificationTime()
            self.__notifyObservers(patterns.Event(self, 'task.dueDate', dueDate))

    def startDate(self, recursive=False):
        if recursive:
            childrenStartDates = [child.startDate(recursive=True) for child in self.children() if not child.completed()]
            return min(childrenStartDates+[self._startDate])
        else:
            return self._startDate

    def setStartDate(self, startDate):
        if startDate != self._startDate:
            self._startDate = startDate
            self.setLastModificationTime()
            self.__notifyObservers(patterns.Event(self, 'task.startDate', 
                startDate))

    def timeLeft(self, recursive=False):
        return self.dueDate(recursive) - date.Today()
        
    def completionDate(self, recursive=False):
        if recursive:
            childrenCompletionDates = [child.completionDate(recursive=True) \
                for child in self.children() if child.completed()]
            return max(childrenCompletionDates+[self._completionDate])
        else:
            return self._completionDate

    def setCompletionDate(self, completionDate=None):
        completionDate = completionDate or date.Today()
        if completionDate != self._completionDate:
            self._completionDate = completionDate
            self.setLastModificationTime()
            self.__notifyObservers(patterns.Event(self, 'task.completionDate', 
                completionDate))
        
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

    def activeEfforts(self, recursive=False):
        return [effort for effort in self.efforts(recursive) \
            if effort.isBeingTracked()]

    def nrActiveEfforts(self):
        return len(self.activeEfforts())

    def isBeingTracked(self, recursive=False):
        return self.activeEfforts(recursive)
        
    def addEffort(self, effort):
        wasTracking = self.isBeingTracked()
        if effort not in self._efforts:
            self._efforts.append(effort)
            self.setLastModificationTime()
            self.__notifyObservers(patterns.Event(self, 'task.effort.add', 
                effort))
            if effort.isBeingTracked() and not wasTracking:
                self.notifyObserversOfStartTracking(effort)
            self.notifyObserversOfTimeSpentChange()
        
    def removeEffort(self, effort):
        if effort in self._efforts:
            self._efforts.remove(effort)
            self.setLastModificationTime()
            self.__notifyObservers(patterns.Event(self, 'task.effort.remove', 
                effort))
            if effort.isBeingTracked() and not self.isBeingTracked():
                self.notifyObserversOfStopTracking(effort)
            self.notifyObserversOfTimeSpentChange()

    def setEfforts(self, efforts):
        self._efforts = efforts # FIXME: no notification?

    def timeSpent(self, recursive=False):
        if recursive:
            return self._myTimeSpent() + self._childrenTimeSpent()
        else:
            return self._myTimeSpent()
    
    def stopTracking(self):
        stoppedEfforts = []
        for effort in self.activeEfforts():
            effort.setStop()
            stoppedEfforts.append(effort)
        if stoppedEfforts:
            self.setLastModificationTime()
        return stoppedEfforts
                
    def budget(self, recursive=False):
        result = self._budget
        if recursive:
            for task in self.children():
                result += task.budget(recursive)
        return result
        
    def setBudget(self, budget):
        if budget != self._budget:
            self._budget = budget
            self.setLastModificationTime()
            self.notifyObserversOfBudgetChange()
            self.notifyObserversOfBudgetLeftChange()
        
    def budgetLeft(self, recursive=False):
        budget = self.budget(recursive)
        if budget:
            return budget - self.timeSpent(recursive)
        else:
            return budget

    def _myTimeSpent(self):
        return sum([effort.duration() for effort in self.efforts()], 
            date.TimeDelta())
    
    def _childrenTimeSpent(self):
        return sum([child.timeSpent(recursive=True) \
            for child in self.children()], date.TimeDelta())

    def notifyObserversOfBudgetChange(self):
        self.__notifyObservers(patterns.Event(self, 'task.budget', self.budget()))
        self.notifyObserversOfTotalBudgetChange()

    def notifyObserversOfTotalBudgetChange(self):
        self.__notifyObservers(patterns.Event(self, 'task.totalBudget',
            self.budget(recursive=True)))
        parent = self.parent()
        if parent: 
            parent.notifyObserversOfTotalBudgetChange()

    def notifyObserversOfBudgetLeftChange(self):
        self.__notifyObservers(patterns.Event(self, 'task.budgetLeft',
            self.budgetLeft()))
        self.notifyObserversOfTotalBudgetLeftChange()
        
    def notifyObserversOfTotalBudgetLeftChange(self):
        self.__notifyObservers(patterns.Event(self, 'task.totalBudgetLeft', 
            self.budgetLeft(recursive=True)))
        parent = self.parent()
        if parent: 
            parent.notifyObserversOfTotalBudgetLeftChange()
        
    def notifyObserversOfTimeSpentChange(self):
        self.__notifyObservers(patterns.Event(self, 'task.timeSpent', 
            self.timeSpent()))
        self.notifyObserversOfTotalTimeSpentChange()
        if self.budget():
            self.notifyObserversOfBudgetLeftChange()
        elif self.budget(recursive=True):
            self.notifyObserversOfTotalBudgetLeftChange()
        if self.hourlyFee() > 0:
            self.notifyObserversOfRevenueChange()

    def notifyObserversOfTotalTimeSpentChange(self):
        self.__notifyObservers(patterns.Event(self, 'task.totalTimeSpent', 
            self.timeSpent(recursive=True)))
        parent = self.parent()
        if parent: 
            parent.notifyObserversOfTotalTimeSpentChange()

    def notifyObserversOfStartTracking(self, *trackedEfforts):
        self.__notifyObservers(patterns.Event(self, 'task.track.start',
            *trackedEfforts))
        parent = self.parent()
        if parent: 
            parent.notifyObserversOfStartTracking(*trackedEfforts)

    def notifyObserversOfStopTracking(self, *trackedEfforts):
        self.__notifyObservers(patterns.Event(self, 'task.track.stop',
            *trackedEfforts))
        parent = self.parent()
        if parent: 
            parent.notifyObserversOfStopTracking(*trackedEfforts)

    # categories
    
    def categories(self, recursive=False):
        result = set(self._categories)
        if recursive and self.parent() is not None:
            result |= self.parent().categories(recursive=True)
        return result
        
    def addCategory(self, category):
        if category not in self._categories:
            self._categories.add(category)
            self.setLastModificationTime()
            self.__notifyObservers(patterns.Event(self, 'task.category.add', 
                category))
        
    def removeCategory(self, category):
        if category in self._categories:
            self._categories.discard(category)
            self.setLastModificationTime()
            self.__notifyObservers(patterns.Event(self, 'task.category.remove', 
                category))

    def setCategories(self, categories):
        self._categories = categories # FIXME: no notification?

    # priority
    
    def priority(self, recursive=False):
        if recursive:
            childPriorities = [child.priority(recursive=True) \
                               for child in self.children()]
            return max(childPriorities + [self._priority])
        else:
            return self._priority
        
    def setPriority(self, priority):
        if priority != self._priority:
            self._priority = priority
            self.setLastModificationTime()
            self.notifyObserversOfPriorityChange()
        
    def notifyObserversOfPriorityChange(self):
        self.__notifyObservers(patterns.Event(self, 'task.priority', 
            self.priority()))
        self.notifyObserversOfTotalPriorityChange()

    def notifyObserversOfTotalPriorityChange(self):
        myTotalPriority = self.priority(recursive=True)
        self.__notifyObservers(patterns.Event(self, 'task.totalPriority', 
            myTotalPriority))
        parent = self.parent()
        if parent and myTotalPriority == parent.priority(recursive=True):
            parent.notifyObserversOfTotalPriorityChange()

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
        if hourlyFee != self._hourlyFee:
            self._hourlyFee = hourlyFee
            self.setLastModificationTime()
            self.__notifyObservers(patterns.Event(self, 'task.hourlyFee',
                hourlyFee))
            if self.timeSpent() > date.TimeDelta():
                self.notifyObserversOfRevenueChange()
        
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
        if fixedFee != self._fixedFee:
            self._fixedFee = fixedFee
            self.setLastModificationTime()
            self.__notifyObservers(patterns.Event(self, 'task.fixedFee',
                fixedFee))
            self.notifyObserversOfRevenueChange()

    def notifyObserversOfRevenueChange(self):
        self.__notifyObservers(patterns.Event(self, 'task.revenue', 
            self.revenue()))
        self.notifyObserversOfTotalRevenueChange()
        
    def notifyObserversOfTotalRevenueChange(self):
        self.__notifyObservers(patterns.Event(self, 'task.totalRevenue', 
            self.revenue(recursive=True)))
        parent = self.parent()
        if parent:
            parent.notifyObserversOfTotalRevenueChange()
        
    # reminder
    
    def reminder(self):
        return self._reminder

    def setReminder(self, reminderDateTime=None):
        if reminderDateTime == date.DateTime.max:
            reminderDateTime = None
        if reminderDateTime != self._reminder:
            self._reminder = reminderDateTime
            self.setLastModificationTime()
            self.__notifyObservers(patterns.Event(self, 'task.reminder', 
                self._reminder))
        
    # attachments
    
    def attachments(self):
        return self._attachments
    
    def addAttachments(self, *attachments):
        if attachments:
            self._attachments.extend(attachments)
            self.setLastModificationTime()
            self.__notifyObservers(patterns.Event(self, 'task.attachment.add', 
                *attachments))
        
    def removeAttachments(self, *attachments):
        attachmentsRemoved = []
        for attachment in attachments:
            if attachment in self._attachments:
                self._attachments.remove(attachment)
                attachmentsRemoved.append(attachment)
        if attachmentsRemoved:
            self.setLastModificationTime()
            self.__notifyObservers(patterns.Event(self, 'task.attachment.remove', 
                *attachmentsRemoved))
            
    def removeAllAttachments(self):
        self.removeAttachments(*self._attachments)
            
    def setAttachments(self, attachments):
        self._attachments = attachments # FIXME: no notification?

    # behavior
    
    # To experiment, this attribute is coded by means of a proporty, which
    # means you can set it like this: task.shouldMark... = True
    
    def __setShouldMarkCompletedWhenAllChildrenCompleted(self, newValue):
        if newValue == self._shouldMarkCompletedWhenAllChildrenCompleted:
            return
        self._shouldMarkCompletedWhenAllChildrenCompleted = newValue
        self.__notifyObservers(patterns.Event(self,
            'task.setting.shouldMarkCompletedWhenAllChildrenCompleted',
            newValue))

    def __getShouldMarkCompletedWhenAllChildrenCompleted(self):
        return self._shouldMarkCompletedWhenAllChildrenCompleted
    
    shouldMarkCompletedWhenAllChildrenCompleted = \
        property(fget=__getShouldMarkCompletedWhenAllChildrenCompleted,
                 fset=__setShouldMarkCompletedWhenAllChildrenCompleted)
