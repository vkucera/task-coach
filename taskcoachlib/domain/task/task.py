import patterns, time, copy, sets
import domain.date as date


class TaskProperty(property):
    pass

class Task(patterns.Observable):
    def __init__(self, subject='', description='', dueDate=None, 
            startDate=None, completionDate=None, parent=None, budget=None, 
            priority=0, id_=None, lastModificationTime=None, hourlyFee=0,
            fixedFee=0, reminder=None, attachments=None,
            shouldMarkCompletedWhenAllChildrenCompleted=None, *args, **kwargs):
        super(Task, self).__init__(*args, **kwargs)
        self._subject        = subject
        self._description    = description 
        self._dueDate        = dueDate or date.Date()
        self._startDate      = startDate or date.Today()
        self._completionDate = completionDate or date.Date()
        self._budget         = budget or date.TimeDelta()
        self._id             = id_ or '%s:%s'%(id(self), time.time()) # FIXME: Not a valid XML id
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
        self._attachments    = attachments or []
        self._shouldMarkCompletedWhenAllChildrenCompleted = shouldMarkCompletedWhenAllChildrenCompleted
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
            categories=sets.Set(self._categories), priority=self._priority, 
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

    def children(self, recursive=False):
        if recursive:
            return self.allChildren()
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
            self.notifyObservers(patterns.Event(self, 'task.description', 
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
        return self.__class__(subject, dueDate=self.dueDate(),
            startDate=max(date.Today(), self.startDate()), parent=self)

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

    def setChildren(self, children):
        self._children = children # FIXME: no notification?
        
    def addChild(self, child):
        if child not in self._children:
            self._children.append(child)
            child.setParent(self)
            self.setLastModificationTime()
            self.notifyObservers(patterns.Event(self, 'task.child.add', child))

    def removeChild(self, child):
        if child in self._children:
            self._children.remove(child)
            self.setLastModificationTime()
            self.notifyObservers(patterns.Event(self, 'task.child.remove', 
                child))

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
            self.notifyObservers(patterns.Event(self, 'task.subject', subject))

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
            self.notifyObservers(patterns.Event(self, 'task.dueDate', dueDate))

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
            self.notifyObservers(patterns.Event(self, 'task.startDate', 
                startDate))

    def timeLeft(self, recursive=False):
        return self.dueDate(recursive) - date.Today()
        
    def completionDate(self, recursive=False):
        if recursive:
            childrenCompletionDates = [child.completionDate(recursive=True) for child in self.children() if child.completed()]
            return max(childrenCompletionDates+[self._completionDate])
        else:
            return self._completionDate

    def setCompletionDate(self, completionDate=None):
        completionDate = completionDate or date.Today()
        if completionDate != self._completionDate:
            self._completionDate = completionDate
            self.setLastModificationTime()
            self.notifyObservers(patterns.Event(self, 'task.completionDate', 
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

    def nrActiveEfforts(self):
        return len([effort for effort in self.efforts() if \
                    effort.getStop() == None])
        
    def addEffort(self, effort):
        wasTracking = self.isBeingTracked()
        if effort not in self._efforts:
            self._efforts.append(effort)
            effort.registerObserver(self.onEffortDurationChanged,
                'effort.start', 'effort.stop')
            effort.registerObserver(self.onEffortStartTracking,
                'effort.track.start')
            effort.registerObserver(self.onEffortStopTracking,
                'effort.track.stop')
            self.setLastModificationTime()
            self.notifyObservers(patterns.Event(self, 'task.effort.add', 
                effort))
            if effort.getStop() == None and not wasTracking:
                self.notifyObservers(patterns.Event(self, 'task.track.start'))
            self.onEffortDurationChanged()
        
    def removeEffort(self, effort):
        if effort in self._efforts:
            self._efforts.remove(effort)
            effort.removeObservers(self.onEffortDurationChanged,
                self.onEffortStartTracking, self.onEffortStopTracking)
            self.setLastModificationTime()
            self.notifyObservers(patterns.Event(self, 'task.effort.remove', 
                effort))
            if effort.getStop() == None and not self.isBeingTracked():
                self.notifyObservers(patterns.Event(self, 'task.track.stop'))
            self.onEffortDurationChanged()

    def setEfforts(self, efforts):
        self._efforts = efforts # FIXME: no notification?

    def onEffortDurationChanged(self, event=None):
        self.notifyObservers( \
            patterns.Event(self, 'task.timeSpent', self.timeSpent()), 
            patterns.Event(self, 'task.budgetLeft', self.budgetLeft()))

    def onEffortStartTracking(self, event):
        if self.nrActiveEfforts() == 1:
            self.notifyObservers(patterns.Event(self, 'task.track.start'))
        
    def onEffortStopTracking(self, event):
        if self.nrActiveEfforts() == 0:
            self.notifyObservers(patterns.Event(self, 'task.track.stop'))

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
                self.setLastModificationTime()
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
        if budget != self._budget:
            self._budget = budget
            self.setLastModificationTime()
            self.notifyObservers(patterns.Event(self, 'task.budget', budget),
                patterns.Event(self, 'task.budgetLeft', self.budgetLeft()))
        
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
        
    # categories
    
    def categories(self, recursive=False):
        result = sets.Set(self._categories)
        if recursive and self.parent() is not None:
            result |= self.parent().categories(recursive=True)
        return result
        
    def addCategory(self, category):
        if category not in self._categories:
            self._categories.add(category)
            self.setLastModificationTime()
            self.notifyObservers(patterns.Event(self, 'task.category.add', 
                category))
        
    def removeCategory(self, category):
        if category in self._categories:
            self._categories.discard(category)
            self.setLastModificationTime()
            self.notifyObservers(patterns.Event(self, 'task.category.remove', 
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
            self.notifyObservers(patterns.Event(self, 'task.priority', 
                priority))
        
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
            self.notifyObservers(patterns.Event(self, 'task.hourlyFee',
                hourlyFee))
        
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
            self.notifyObservers(patterns.Event(self, 'task.fixedFee',
                fixedFee))
        
    # reminder
    
    def reminder(self):
        return self._reminder

    def setReminder(self, reminderDateTime=None):
        if reminderDateTime == date.DateTime.max:
            reminderDateTime = None
        if reminderDateTime != self._reminder:
            self._reminder = reminderDateTime
            self.setLastModificationTime()
            self.notifyObservers(patterns.Event(self, 'task.reminder', 
                self._reminder))
        
    # attachments
    
    def attachments(self):
        return self._attachments
    
    def addAttachments(self, *attachments):
        if attachments:
            self._attachments.extend(attachments)
            self.setLastModificationTime()
            self.notifyObservers(patterns.Event(self, 'task.attachment.add', 
                *attachments))
        
    def removeAttachments(self, *attachments):
        attachmentsRemoved = []
        for attachment in attachments:
            if attachment in self._attachments:
                self._attachments.remove(attachment)
                attachmentsRemoved.append(attachment)
        if attachmentsRemoved:
            self.setLastModificationTime()
            self.notifyObservers(patterns.Event(self, 'task.attachment.remove', 
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
        self.notifyObservers(patterns.Event(self,
            'task.setting.shouldMarkCompletedWhenAllChildrenCompleted',
            newValue))

    def __getShouldMarkCompletedWhenAllChildrenCompleted(self):
        return self._shouldMarkCompletedWhenAllChildrenCompleted
    
    shouldMarkCompletedWhenAllChildrenCompleted = \
        property(fget=__getShouldMarkCompletedWhenAllChildrenCompleted,
                 fset=__setShouldMarkCompletedWhenAllChildrenCompleted)
