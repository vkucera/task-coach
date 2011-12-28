'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2011 Task Coach developers <developers@taskcoach.org>

Task Coach is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Task Coach is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from taskcoachlib import patterns
from taskcoachlib.domain import base, date
import task


class ViewFilter(base.Filter):
    def __init__(self, *args, **kwargs):
        self.__dueDateTimeFilter = self.__stringToDueDateTimeFilter(kwargs.pop('dueDateTimeFilter', 
                                                                               'Never'))
        self.__completionDateTimeFilter = self.__stringToCompletionDateTimeFilter(kwargs.pop('completionDateTimeFilter',
                                                                                             'Never'))
        self.__plannedStartDateTimeFilterString = kwargs.pop('plannedStartDateTimeFilter', 
                                                      'Never')
        self.__plannedStartDateTimeFilter = self.__stringToPlannedStartDateTimeFilter(self.__plannedStartDateTimeFilterString)
        self.__hideActiveTasks = kwargs.pop('hideActiveTasks', False)
        self.__hideCompositeTasks = kwargs.pop('hideCompositeTasks', False)
        self.registerObservers()
        super(ViewFilter, self).__init__(*args, **kwargs)
        
    def registerObservers(self):
        registerObserver = patterns.Publisher().registerObserver
        for eventType in (task.Task.dueDateTimeChangedEventType(),
                          task.Task.plannedStartDateTimeChangedEventType(),
                          task.Task.completionDateTimeChangedEventType(),
                          'task.prerequisites',
                          task.Task.appearanceChangedEventType(), # Proxy for status changes
                          task.Task.addChildEventType(),
                          task.Task.removeChildEventType(),
                          'clock.day'):
            registerObserver(self.onTaskStatusChange, eventType=eventType)

    def onTaskStatusChange(self, event): # pylint: disable-msg=W0613
        self.reset()
        
    def setFilteredByDueDateTime(self, dueDateTimeString):
        self.__dueDateTimeFilter = self.__stringToDueDateTimeFilter(dueDateTimeString)
        self.reset()
        
    def setFilteredByCompletionDateTime(self, completionDateTimeString):
        self.__completionDateTimeFilter = self.__stringToCompletionDateTimeFilter(completionDateTimeString)
        self.reset()

    def setFilteredByPlannedStartDateTime(self, plannedStartDateTimeString):
        self.__plannedStartDateTimeFilterString = plannedStartDateTimeString
        self.__plannedStartDateTimeFilter = self.__stringToPlannedStartDateTimeFilter(plannedStartDateTimeString)
        self.reset()
        
    def hideActiveTasks(self, hide=True):
        self.__hideActiveTasks = hide
        self.reset()
        
    def hideCompositeTasks(self, hide=True):
        self.__hideCompositeTasks = hide
        self.reset()
        
    def filter(self, tasks):
        return [task for task in tasks if self.filterTask(task)] # pylint: disable-msg=W0621
    
    def filterTask(self, task): # pylint: disable-msg=W0621
        result = True
        if self.__hideActiveTasks and task.active():
            result = False # Hide active task
        elif self.__hideCompositeTasks and not self.treeMode() and task.children():
            result = False # Hide composite task
        elif self.__taskDueLaterThanDueDateTimeFilter(task):
            result = False # Hide due task
        elif self.__taskCompletedEarlierThanCompletionDateTimeFilter(task):
            result = False # Hide completed task
        elif self.__plannedStartDateTimeFilterString == 'Always' and task.inactive():
            result = False # Hide prerequisite task no matter what planned start date
        elif self.__taskStartsLaterThanPlannedStartDateTimeFilter(task):
            result = False # Hide future task 
        return result
    
    # pylint: disable-msg=W0621
    
    def __taskDueLaterThanDueDateTimeFilter(self, task):
        if self.__dueDateTimeFilter:
            return task.dueDateTime(recursive=self.treeMode()) > self.__dueDateTimeFilter()
        else:
            return False
        
    def __taskCompletedEarlierThanCompletionDateTimeFilter(self, task):
        if self.__completionDateTimeFilter:
            return task.completionDateTime(recursive=self.treeMode()) < self.__completionDateTimeFilter()
        else:
            return False
        
    def __taskStartsLaterThanPlannedStartDateTimeFilter(self, task):
        if self.__plannedStartDateTimeFilter:
            return task.plannedStartDateTime(recursive=self.treeMode()) > self.__plannedStartDateTimeFilter()
        else:
            return False

    # pylint: disable-msg=W0108
    
    endOfPeriodFilterFactory = dict(Today=lambda: date.Now().endOfDay(), 
                                    Tomorrow=lambda: date.Now().endOfTomorrow(),
                                    Workweek=lambda: date.Now().endOfWorkWeek(), 
                                    Week=lambda: date.Now().endOfWeek(),
                                    Days7=lambda: (date.Now()+date.TimeDelta(days=7)).endOfDay(), 
                                    Days14=lambda: (date.Now()+date.TimeDelta(days=14)).endOfDay(), 
                                    Month=lambda: date.Now().endOfMonth(), 
                                    Days30=lambda: (date.Now()+date.TimeDelta(days=30)).endOfDay(),
                                    Year=lambda: date.Now().endOfYear(),
                                    Always=lambda: date.Now(), 
                                    Never=None)

    startOfPeriodFilterFactory = dict(Today=lambda: date.Now().startOfDay(),
                                      Yesterday=lambda: date.Now().startOfDay()-date.oneDay,
                                      Workweek=lambda: date.Now().startOfWorkWeek(), 
                                      Week=lambda: date.Now().startOfWeek(),
                                      Days7=lambda: (date.Now()-date.TimeDelta(days=7)).startOfDay(),
                                      Days14=lambda: (date.Now()-date.TimeDelta(days=14)).startOfDay(),
                                      Month=lambda: date.Now().startOfMonth(),
                                      Days30=lambda: (date.Now()-date.TimeDelta(days=30)).startOfDay(),
                                      Year=lambda: date.Now().startOfYear(), 
                                      Always=lambda: date.DateTime(),
                                      Never=None)
                
    @classmethod
    def __stringToDueDateTimeFilter(class_, filterString):
        return class_.__stringToFilter(class_.endOfPeriodFilterFactory, 
                                       filterString)

    @classmethod
    def __stringToCompletionDateTimeFilter(class_, filterString):
        return class_.__stringToFilter(class_.startOfPeriodFilterFactory, 
                                       filterString)
    
    @classmethod
    def __stringToPlannedStartDateTimeFilter(class_, filterString):
        return class_.__stringToFilter(class_.endOfPeriodFilterFactory, 
                                       filterString)
    
    @staticmethod
    def __stringToFilter(filterFactory, filterString, default='Never'):
        try:
            return filterFactory[filterString]
        except KeyError:
            return filterFactory[default]
        
