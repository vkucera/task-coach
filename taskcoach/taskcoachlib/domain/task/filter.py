'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2012 Task Coach developers <developers@taskcoach.org>

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
from taskcoachlib.domain import base
import task


class ViewFilter(base.Filter):
    def __init__(self, *args, **kwargs):
        self.__hideInactiveTasks = kwargs.pop('hideInactiveTasks', False)
        self.__hideLateTasks = kwargs.pop('hideLateTasks', False)
        self.__hideActiveTasks = kwargs.pop('hideActiveTasks', False)
        self.__hideDueSoonTasks = kwargs.pop('hideDueSoonTasks', False)
        self.__hideOverDueTasks = kwargs.pop('hideOverDueTasks', False)
        self.__hideCompletedTasks = kwargs.pop('hideCompletedTasks', False)
        self.__hideCompositeTasks = kwargs.pop('hideCompositeTasks', False)
        self.registerObservers()
        super(ViewFilter, self).__init__(*args, **kwargs)
        
    def registerObservers(self):
        registerObserver = patterns.Publisher().registerObserver
        for eventType in ('task.actualStartDateTime', 'task.plannedStartDateTime',
                          'task.dueDateTime', 'task.completionDateTime', 
                          'task.prerequisites',
                          task.Task.appearanceChangedEventType(), # Proxy for status changes
                          task.Task.addChildEventType(),
                          task.Task.removeChildEventType(),
                          'clock.day'):
            registerObserver(self.onTaskStatusChange, eventType=eventType)

    def onTaskStatusChange(self, event): # pylint: disable-msg=W0613
        self.reset()
        
    def hideInactiveTasks(self, hide=True):
        self.__hideInactiveTasks = hide
        self.reset()
        
    def hideLateTasks(self, hide=True):
        self.__hideLateTasks = hide
        self.reset()
        
    def hideActiveTasks(self, hide=True):
        self.__hideActiveTasks = hide
        self.reset()
        
    def hideDueSoonTasks(self, hide=True):
        self.__hideDueSoonTasks = hide
        self.reset()
        
    def hideOverDueTasks(self, hide=True):
        self.__hideOverDueTasks = hide
        self.reset()

    def hideCompletedTasks(self, hide=True):
        self.__hideCompletedTasks = hide
        self.reset()
        
    def hideCompositeTasks(self, hide=True):
        self.__hideCompositeTasks = hide
        self.reset()
        
    def filter(self, tasks):
        return [task for task in tasks if self.filterTask(task)] # pylint: disable-msg=W0621
    
    def filterTask(self, task): # pylint: disable-msg=W0621
        result = True
        if self.__hideInactiveTasks and task.inactive():
            result = False # Hide inactive task
        elif self.__hideLateTasks and task.late():
            result = False # Hide late task
        elif self.__hideActiveTasks and task.active():
            result = False # Hide active task
        elif self.__hideDueSoonTasks and task.dueSoon():
            result = False # Hide due soon task
        elif self.__hideOverDueTasks and task.overdue():
            result = False # Hide over due task
        elif self.__hideCompletedTasks and task.completed():
            result = False # Hide completed task
        elif self.__hideCompositeTasks and not self.treeMode() and task.children():
            result = False # Hide composite task
        return result
