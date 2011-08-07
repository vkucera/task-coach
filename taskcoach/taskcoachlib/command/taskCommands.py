# -*- coding: utf-8 -*-

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
from taskcoachlib.i18n import _
from taskcoachlib.domain import task, effort, date
import base, noteCommands


class SaveTaskStateMixin(base.SaveStateMixin, base.CompositeMixin):
    pass


class EffortCommand(base.BaseCommand): # pylint: disable-msg=W0223
    @patterns.eventSource
    def stopTracking(self, event=None):
        self.stoppedEfforts = [] # pylint: disable-msg=W0201
        for taskToStop in self.tasksToStopTracking():
            self.stoppedEfforts.extend(taskToStop.activeEfforts())
            taskToStop.stopTracking(event=event)

    @patterns.eventSource
    def startTracking(self, event=None):
        for stoppedEffort in self.stoppedEfforts:
            stoppedEffort.setStop(date.DateTime.max, event=event)
    
    def tasksToStopTracking(self):
        return self.list
                
    def do_command(self):
        self.stopTracking()
    
    def undo_command(self):
        self.startTracking()
        
    def redo_command(self):
        self.stopTracking()


class DragAndDropTaskCommand(base.DragAndDropCommand):
    plural_name = _('Drag and drop tasks')


class DeleteTaskCommand(base.DeleteCommand, EffortCommand):
    plural_name = _('Delete tasks')
    singular_name = _('Delete task "%s"')

    def tasksToStopTracking(self):
        return self.items

    @patterns.eventSource 
    def do_command(self, event=None):
        super(DeleteTaskCommand, self).do_command()
        self.stopTracking(event=event)
        self.__removePrerequisites(event)
    
    @patterns.eventSource
    def undo_command(self, event=None):
        super(DeleteTaskCommand, self).undo_command()
        self.startTracking(event=event)
        self.__restorePrerequisites(event)
        
    @patterns.eventSource
    def redo_command(self, event=None):
        super(DeleteTaskCommand, self).redo_command()
        self.stopTracking(event=event)
        self.__removePrerequisites(event)
    
    def __removePrerequisites(self, event):
        self.__relationsToRestore = dict() # pylint: disable-msg=W0201
        for eachTask in self.items:
            prerequisites, dependencies = eachTask.prerequisites(), eachTask.dependencies()
            self.__relationsToRestore[eachTask] = prerequisites, dependencies
            eachTask.removeTaskAsDependencyOf(prerequisites, event=event)
            eachTask.removeTaskAsPrerequisiteOf(dependencies, event=event)
            eachTask.setPrerequisites([], event=event)
            eachTask.setDependencies([], event=event)

    def __restorePrerequisites(self, event):
        for eachTask, (prerequisites, dependencies) in self.__relationsToRestore.items():
            eachTask.addTaskAsDependencyOf(prerequisites, event=event)
            eachTask.addTaskAsPrerequisiteOf(dependencies, event=event)
            eachTask.setPrerequisites(prerequisites, event=event)
            eachTask.setDependencies(dependencies, event=event)
            

class NewTaskCommand(base.NewItemCommand):
    singular_name = _('New task')
    
    def __init__(self, *args, **kwargs):
        subject = kwargs.pop('subject', _('New task'))
        super(NewTaskCommand, self).__init__(*args, **kwargs)
        self.items = [task.Task(subject=subject, **kwargs)]

    def do_command(self):
        super(NewTaskCommand, self).do_command()
        self.addDependenciesAndPrerequisites()
        
    def undo_command(self):
        super(NewTaskCommand, self).undo_command()
        self.removeDependenciesAndPrerequisites()
        
    def redo_command(self):
        super(NewTaskCommand, self).redo_command()
        self.addDependenciesAndPrerequisites()
        
    @patterns.eventSource
    def addDependenciesAndPrerequisites(self, event=None):
        for eachTask in self.items:
            for prerequisite in eachTask.prerequisites():
                prerequisite.addDependencies([eachTask], event=event)
            for dependency in eachTask.dependencies():
                dependency.addPrerequisites([eachTask], event=event)

    @patterns.eventSource
    def removeDependenciesAndPrerequisites(self, event=None):
        for eachTask in self.items:
            for prerequisite in eachTask.prerequisites():
                prerequisite.removeDependencies([eachTask], event=event)                                
            for dependency in eachTask.dependencies():
                dependency.removePrerequisites([eachTask], event=event)
                
                
class NewSubTaskCommand(base.NewSubItemCommand, SaveTaskStateMixin):
    plural_name = _('New subtasks')
    singular_name = _('New subtask of "%s"')
    # pylint: disable-msg=E1101
    
    def __init__(self, *args, **kwargs):
        super(NewSubTaskCommand, self).__init__(*args, **kwargs)
        subject = kwargs.pop('subject', _('New subtask'))
        self.items = [parent.newChild(subject=subject, **kwargs) for parent in self.items]
        self.saveStates(self.getTasksToSave())
    
    def getTasksToSave(self):
        # FIXME: can be simplified to: return self.getAncestors(self.items) ?
        parents = [item.parent() for item in self.items if item.parent()]
        return parents + self.getAncestors(parents)

    def undo_command(self):
        super(NewSubTaskCommand, self).undo_command()
        self.undoStates()

    def redo_command(self):
        super(NewSubTaskCommand, self).redo_command()
        self.redoStates()
                
                
class MarkCompletedCommand(base.SaveStateMixin, EffortCommand):
    plural_name = _('Mark tasks completed')
    singular_name = _('Mark "%s" completed')
    
    def __init__(self, *args, **kwargs):
        super(MarkCompletedCommand, self).__init__(*args, **kwargs)
        itemsToSave = set([relative for item in self.items for relative in item.family()]) 
        self.saveStates(itemsToSave)

    @patterns.eventSource
    def do_command(self, event=None):
        super(MarkCompletedCommand, self).do_command()
        for item in self.items:
            completionDateTime = date.DateTime() if item.completed() else task.Task.suggestedCompletionDateTime()
            item.setCompletionDateTime(completionDateTime, event=event)

    def undo_command(self):
        self.undoStates()
        super(MarkCompletedCommand, self).undo_command()

    def redo_command(self):
        self.redoStates()
        super(MarkCompletedCommand, self).redo_command()

    def tasksToStopTracking(self):
        return self.items                

                
class StartEffortCommand(EffortCommand):
    plural_name = _('Start tracking')
    singular_name = _('Start tracking "%s"')

    def __init__(self, *args, **kwargs):
        super(StartEffortCommand, self).__init__(*args, **kwargs)
        start = date.DateTime.now()
        self.efforts = [effort.Effort(item, start) for item in self.items]
        self.startDateTimes = [(item.startDateTime() if start < item.startDateTime() else None) for item in self.items]
        
    def do_command(self):
        super(StartEffortCommand, self).do_command()
        self.addEfforts()
        
    def undo_command(self):
        self.removeEfforts()
        super(StartEffortCommand, self).undo_command()
        
    def redo_command(self):
        super(StartEffortCommand, self).redo_command()
        self.addEfforts()

    @patterns.eventSource
    def addEfforts(self, event=None):
        for item, newEffort, currentStartDateTime in zip(self.items, self.efforts, self.startDateTimes):
            item.addEffort(newEffort, event=event)
            if currentStartDateTime:
                item.setStartDateTime(newEffort.getStart())
            
    @patterns.eventSource
    def removeEfforts(self, event=None):
        for item, newEffort, previousStartDateTime in zip(self.items, self.efforts, self.startDateTimes):
            item.removeEffort(newEffort, event=event)
            if previousStartDateTime:
                item.setStartDateTime(previousStartDateTime)
            
        
class StopEffortCommand(EffortCommand):
    plural_name = _('Stop tracking')
    singular_name = _('Stop tracking "%s"')
                  
    def canDo(self):
        return True # No selected items needed.
    
    def tasksToStopTracking(self):
        stoppable = lambda effort: effort.isBeingTracked() and not effort.isTotal()
        return set([effort.task() for effort in self.list if stoppable(effort)]) # pylint: disable-msg=W0621 


class ExtremePriorityCommand(base.BaseCommand): # pylint: disable-msg=W0223
    delta = 'Subclass responsibility'
    
    def __init__(self, *args, **kwargs):
        super(ExtremePriorityCommand, self).__init__(*args, **kwargs)
        self.oldPriorities = [item.priority() for item in self.items]
        self.oldExtremePriority = self.getOldExtremePriority()
        
    def getOldExtremePriority(self):
        raise NotImplementedError # pragma: no cover

    @patterns.eventSource
    def setNewExtremePriority(self, event=None):
        newExtremePriority = self.oldExtremePriority + self.delta 
        for item in self.items:
            item.setPriority(newExtremePriority, event=event)

    @patterns.eventSource
    def restorePriorities(self, event=None):
        for item, oldPriority in zip(self.items, self.oldPriorities):
            item.setPriority(oldPriority, event=event)

    def do_command(self):
        super(ExtremePriorityCommand, self).do_command()
        self.setNewExtremePriority()
        
    def undo_command(self):
        self.restorePriorities()
        super(ExtremePriorityCommand, self).undo_command()
        
    def redo_command(self):
        super(ExtremePriorityCommand, self).redo_command()
        self.setNewExtremePriority()


class MaxPriorityCommand(ExtremePriorityCommand):
    plural_name = _('Maximize priority')
    singular_name = _('Maximize priority of "%s"')
    
    delta = +1
    
    def getOldExtremePriority(self):
        return self.list.maxPriority()
    

class MinPriorityCommand(ExtremePriorityCommand):
    plural_name = _('Minimize priority')
    singular_name = _('Minimize priority of "%s"')
    
    delta = -1
                    
    def getOldExtremePriority(self):
        return self.list.minPriority()
    

class ChangePriorityCommand(base.BaseCommand): # pylint: disable-msg=W0223
    delta = 'Subclass responsibility'
    
    @patterns.eventSource
    def changePriorities(self, delta, event=None):
        for item in self.items:
            item.setPriority(item.priority() + delta, event=event)

    def do_command(self):
        super(ChangePriorityCommand, self).do_command()
        self.changePriorities(self.delta)

    def undo_command(self):
        self.changePriorities(-self.delta)
        super(ChangePriorityCommand, self).undo_command()

    def redo_command(self):
        super(ChangePriorityCommand, self).redo_command()
        self.changePriorities(self.delta)


class IncPriorityCommand(ChangePriorityCommand):
    plural_name = _('Increase priority')
    singular_name = _('Increase priority of "%s"')
    delta = +1


class DecPriorityCommand(ChangePriorityCommand):
    plural_name = _('Decrease priority')
    singular_name = _('Decrease priority of "%s"')
    delta = -1
    

class EditPriorityCommand(base.BaseCommand):
    plural_name = _('Change priority')
    singular_name = _('Change priority of "%s"')
    
    def __init__(self, *args, **kwargs):
        self.__newPriority = kwargs.pop('priority', '') or kwargs.pop('newValue', '')
        super(EditPriorityCommand, self).__init__(*args, **kwargs)
        self.__oldPriorities = [item.priority() for item in self.items]

    @patterns.eventSource
    def do_command(self, event=None):
        for item in self.items:
            item.setPriority(self.__newPriority, event=event)

    @patterns.eventSource
    def undo_command(self, event=None):
        for item, oldPriority in zip(self.items, self.__oldPriorities):
            item.setPriority(oldPriority, event=event)

    def redo_command(self):
        self.do_command()
    
    
class AddTaskNoteCommand(noteCommands.AddNoteCommand):
    plural_name = _('Add note to tasks')


class EditDateTimeCommand(base.BaseCommand):
    def __init__(self, *args, **kwargs):
        self._newDateTime = kwargs.pop('datetime', '') or kwargs.pop('newValue', '')
        super(EditDateTimeCommand, self).__init__(*args, **kwargs)
        self.__oldDateTimes = [self.getDateTime(item) for item in self.items]
        familyMembers = set()
        for item in self.items:
            for familyMember in item.family():
                if familyMember not in self.items:
                    familyMembers.add(familyMember)
        self.__oldFamilyMemberDateTimes = [(familyMember, self.getDateTime(familyMember)) for familyMember in familyMembers]                

    @staticmethod
    def getDateTime(item):
        raise NotImplementedError # pragma: no cover

    @staticmethod
    def setDateTime(item, newDateTime, event):
        raise NotImplementedError # pragma: no cover
    
    @patterns.eventSource
    def do_command(self, event=None):
        super(EditDateTimeCommand, self).do_command()
        for item in self.items:
            self.setDateTime(item, self._newDateTime, event=event)

    @patterns.eventSource
    def undo_command(self, event=None):
        super(EditDateTimeCommand, self).undo_command()
        for item, oldDateTime in zip(self.items, self.__oldDateTimes):
            self.setDateTime(item, oldDateTime, event=event)
        for familyMember, oldDateTime in self.__oldFamilyMemberDateTimes:
            self.setDateTime(familyMember, oldDateTime, event=event)
    
    def redo_command(self):
        self.do_command()

    
class _EditStartDateTimeCommandBase(EditDateTimeCommand):
    plural_name = _('Change start date')
    singular_name = _('Change start date of "%s"')

    @staticmethod
    def getDateTime(item):
        return item.startDateTime()
    
    @staticmethod
    def setDateTime(item, dateTime, event):
        item.setStartDateTime(dateTime, event=event)
        
    @patterns.eventSource
    def do_command(self, event=None):
        for item in self.items:
            if self.keep_delta and date.DateTime() not in [item.startDateTime(), item.dueDateTime()]:
                delta = self._newDateTime - item.startDateTime()
                item.setDueDateTime(item.dueDateTime() + delta, event=event)
        super(_EditStartDateTimeCommandBase, self).do_command(event=event)
                
    @patterns.eventSource
    def undo_command(self, event=None):
        super(_EditStartDateTimeCommandBase, self).undo_command(event=event)
        for item in self.items:
            if self.keep_delta and date.DateTime() not in [item.startDateTime(), item.dueDateTime()]:
                delta = self._newDateTime - item.startDateTime()
                item.setDueDateTime(item.dueDateTime() - delta, event=event)


class EditStartDateTimeCommand(_EditStartDateTimeCommandBase):
    keep_delta = False


class EditStartDateTimeSyncCommand(_EditStartDateTimeCommandBase):
    keep_delta = True


class _EditDueDateTimeCommandBase(EditDateTimeCommand):
    plural_name = _('Change due date')
    singular_name = _('Change due date of "%s"')
    keep_delta = False
    
    @staticmethod
    def getDateTime(item):
        return item.dueDateTime()
    
    @staticmethod
    def setDateTime(item, dateTime, event):
        item.setDueDateTime(dateTime, event=event)

    @patterns.eventSource
    def do_command(self, event=None):
        for item in self.items:
            if self.keep_delta and date.DateTime() not in [item.startDateTime(), item.dueDateTime()]:
                delta = self._newDateTime - item.dueDateTime()
                item.setStartDateTime(item.startDateTime() + delta, event=event)
        super(_EditDueDateTimeCommandBase, self).do_command(event=event)
                
    @patterns.eventSource
    def undo_command(self, event=None):
        super(_EditDueDateTimeCommandBase, self).undo_command(event=event)
        for item in self.items:
            if self.keep_delta and date.DateTime() not in [item.startDateTime(), item.dueDateTime()]:
                delta = self._newDateTime - item.dueDateTime()
                item.setStartDateTime(item.startDateTime() - delta, event=event)


class EditDueDateTimeCommand(_EditDueDateTimeCommandBase):
    keep_delta = False


class EditDueDateTimeSyncCommand(_EditDueDateTimeCommandBase):
    keep_delta = True


class EditCompletionDateTimeCommand(EditDateTimeCommand, EffortCommand):
    plural_name = _('Change completion date')
    singular_name = _('Change completion date of "%s"')
                    
    @staticmethod
    def getDateTime(item):
        return item.completionDateTime()
    
    @staticmethod
    def setDateTime(item, dateTime, event):
        item.setCompletionDateTime(dateTime, event=event)

    def tasksToStopTracking(self):
        return self.items
    
    
class EditReminderDateTimeCommand(EditDateTimeCommand):
    plural_name = _('Change reminder dates/times')
    singular_name = _('Change reminder date/time of "%s"')
    
    @staticmethod
    def getDateTime(item):
        return item.reminder()
    
    @staticmethod
    def setDateTime(item, dateTime, event):
        item.setReminder(dateTime, event=event)

        
class EditRecurrenceCommand(base.BaseCommand):
    plural_name = _('Change recurrences')
    singular_name = _('Change recurrence of "%s"')
    
    def __init__(self, *args, **kwargs):
        self.__newRecurrence = kwargs.pop('recurrence')
        super(EditRecurrenceCommand, self).__init__(*args, **kwargs)
        self.__oldRecurrences = [item.recurrence() for item in self.items]

    @patterns.eventSource
    def do_command(self, event=None):
        for item in self.items:
            item.setRecurrence(self.__newRecurrence, event=event)

    @patterns.eventSource
    def undo_command(self, event=None):
        for item, oldRecurrence in zip(self.items, self.__oldRecurrences):
            item.setRecurrence(oldRecurrence, event=event)

    def redo_command(self):
        self.do_command()
    
    
class EditPercentageCompleteCommand(base.BaseCommand):
    plurar_name = ('Change percentages complete')
    singular_name = _('Change percentage complete of "%s"')
    
    def __init__(self, *args, **kwargs):
        self.__newPercentage = kwargs.pop('percentage')
        super(EditPercentageCompleteCommand, self).__init__(*args, **kwargs)
        self.__oldPercentages = [item.percentageComplete() for item in self.items]
        
    @patterns.eventSource
    def do_command(self, event=None):
        for item in self.items:
            item.setPercentageComplete(self.__newPercentage, event=event)
            
    @patterns.eventSource
    def undo_command(self, event=None):
        for item, oldPercentage in zip(self.items, self.__oldPercentages):
            item.setPercentageComplete(oldPercentage, event=event)
            
    def redo_command(self):
        self.do_command()
        
        
class EditShouldMarkCompletedCommand(base.BaseCommand):
    plural_name = _('Change when tasks are marked completed')
    singular_name = _('Change when "%s" is marked completed')
    
    def __init__(self, *args, **kwargs):
        self.__newShouldMarkCompleted = kwargs.pop('shouldMarkCompleted')
        super(EditShouldMarkCompletedCommand, self).__init__(*args, **kwargs)
        self.__oldShouldMarkCompleted = [item.shouldMarkCompletedWhenAllChildrenCompleted() for item in self.items]
        
    @patterns.eventSource
    def do_command(self, event=None):
        for item in self.items:
            item.setShouldMarkCompletedWhenAllChildrenCompleted(self.__newShouldMarkCompleted, event=event)
            
    @patterns.eventSource
    def undo_command(self, event=None):
        for item, oldShouldMarkCompleted in zip(self.items, self.__oldShouldMarkCompleted):
            item.setShouldMarkCompletedWhenAllChildrenCompleted(oldShouldMarkCompleted, event=event)
            
    def redo_command(self):
        self.do_command()
        

class EditBudgetCommand(base.BaseCommand):
    plural_name = _('Change budgets')
    singular_name = _('Change budget of "%s"')
    
    def __init__(self, *args, **kwargs):
        self.__newBudget = kwargs.pop('budget', '') or kwargs.pop('newValue', '') 
        super(EditBudgetCommand, self).__init__(*args, **kwargs)
        self.__oldBudgets = [item.budget() for item in self.items]
        
    @patterns.eventSource
    def do_command(self, event=None):
        for item in self.items:
            item.setBudget(self.__newBudget, event=event)
            
    @patterns.eventSource
    def undo_command(self, event=None):
        for item, oldBudget in zip(self.items, self.__oldBudgets):
            item.setBudget(oldBudget, event=event)
            
    def redo_command(self):
        self.do_command()
            
            
class EditHourlyFeeCommand(base.BaseCommand):
    plural_name = _('Change hourly fees')
    singular_name = _('Change hourly fee of "%s"')
    
    def __init__(self, *args, **kwargs):
        self.__newHourlyFee = kwargs.pop('hourlyFee')
        super(EditHourlyFeeCommand, self).__init__(*args, **kwargs)
        self.__oldHourlyFees = [item.hourlyFee() for item in self.items]
        
    @patterns.eventSource
    def do_command(self, event=None):
        for item in self.items:
            item.setHourlyFee(self.__newHourlyFee, event=event)
            
    @patterns.eventSource
    def undo_command(self, event=None):
        for item, oldHourlyFee in zip(self.items, self.__oldHourlyFees):
            item.setHourlyFee(oldHourlyFee, event=event)
            
    def redo_command(self):
        self.do_command()


class EditFixedFeeCommand(base.BaseCommand):
    plural_name = _('Change fixed fees')
    singular_name = _('Change fixed fee of "%s"')
    
    def __init__(self, *args, **kwargs):
        self.__newFixedFee = kwargs.pop('fixedFee')
        super(EditFixedFeeCommand, self).__init__(*args, **kwargs)
        self.__oldFixedFees = [item.fixedFee() for item in self.items]
        
    @patterns.eventSource
    def do_command(self, event=None):
        for item in self.items:
            item.setFixedFee(self.__newFixedFee, event=event)
            
    @patterns.eventSource
    def undo_command(self, event=None):
        for item, oldFixedFee in zip(self.items, self.__oldFixedFees):
            item.setFixedFee(oldFixedFee, event=event)
            
    def redo_command(self):
        self.do_command()
            
            
class TogglePrerequisiteCommand(base.BaseCommand):
    plural_name = _('Toggle prerequisite')
    singular_name = _('Toggle prerequisite of "%s"')
    
    def __init__(self, *args, **kwargs):
        self.__checkedPrerequisites = set(kwargs.pop('checkedPrerequisites'))
        self.__uncheckedPrerequisites = set(kwargs.pop('uncheckedPrerequisites'))
        super(TogglePrerequisiteCommand, self).__init__(*args, **kwargs)
    
    @patterns.eventSource
    def do_command(self, event=None):
        for item in self.items:
            item.addPrerequisites(self.__checkedPrerequisites, event=event)
            item.addTaskAsDependencyOf(self.__checkedPrerequisites, event=event)
            item.removePrerequisites(self.__uncheckedPrerequisites, event=event)
            item.removeTaskAsDependencyOf(self.__uncheckedPrerequisites, event=event)

    @patterns.eventSource
    def undo_command(self, event=None):
        for item in self.items:
            item.removePrerequisites(self.__checkedPrerequisites, event=event)
            item.removeTaskAsDependencyOf(self.__checkedPrerequisites, event=event)
            item.addPrerequisites(self.__uncheckedPrerequisites, event=event)
            item.addTaskAsDependencyOf(self.__uncheckedPrerequisites, event=event)

    def redo_command(self):
        self.do_command()
