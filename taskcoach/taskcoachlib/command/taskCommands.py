import task, date, base, effort
import sets
from i18n import _

class SaveTaskStateMixin(base.SaveStateMixin):
    def getAncestors(self, tasks): 
        ancestors = []
        for task in tasks:
            ancestors.extend(task.ancestors())
        return ancestors


class PasteTaskCommand(base.BaseCommand, SaveTaskStateMixin):
    def name(self):
        return _('Paste')

    def __init__(self, *args, **kwargs):
        super(PasteTaskCommand, self).__init__(*args, **kwargs)
        self.__tasksToPaste = task.Clipboard().get()
        self.saveStates(self.getTasksToSave())

    def getTasksToSave(self):
        return self.__tasksToPaste
    
    def canDo(self):
        return bool(self.__tasksToPaste)
        
    def do_command(self):
        self.setParentOfPastedTasks()
        self.list.extend(self.__tasksToPaste)

    def undo_command(self):
        self.list.removeItems(self.__tasksToPaste)
        self.undoStates()
        task.Clipboard().put(self.__tasksToPaste)
        
    def redo_command(self):
        task.Clipboard().clear() 
        self.redoStates()
        self.list.extend(self.__tasksToPaste)

    def setParentOfPastedTasks(self, newParent=None):
        for task in self.__tasksToPaste:
            task.setParent(newParent) 


class PasteTaskAsSubtaskCommand(PasteTaskCommand):
    def name(self):
        return _('Paste as subtask')

    def setParentOfPastedTasks(self):
        newParent = self.items[0]
        super(PasteTaskAsSubtaskCommand, self).setParentOfPastedTasks(newParent)

    def getTasksToSave(self):
        parents = [task for task in [self.items[0]] if task.completed()]
        return parents + self.getAncestors(parents) + \
            super(PasteTaskAsSubtaskCommand, self).getTasksToSave()


class NewTaskCommand(base.BaseCommand):
    def name(self):
        return _('New task')

    def __init__(self, *args, **kwargs):
        super(NewTaskCommand, self).__init__(*args, **kwargs)
        self.items = [task.Task(subject=_('New task'))]
        
    def do_command(self):
        self.list.extend(self.items)

    def undo_command(self):
        self.list.removeItems(self.items)

    def redo_command(self):
        self.list.extend(self.items)


class NewSubTaskCommand(base.BaseCommand, SaveTaskStateMixin):
    def name(self):
        return _('New subtask')

    def __init__(self, *args, **kwargs):
        super(NewSubTaskCommand, self).__init__(*args, **kwargs)
        self.items = [task.newSubTask(subject=_('New subtask')) for task in self.items]
        self.saveStates(self.getTasksToSave())
        
    def getTasksToSave(self):
        # FIXME: can be simplified to: return self.getAncestors(self.items) ?
        parents = [task.parent() for task in self.items if task.parent()]
        return parents + self.getAncestors(parents)

    def do_command(self):
        self.list.extend(self.items)

    def undo_command(self):
        self.list.removeItems(self.items)
        self.undoStates()

    def redo_command(self):
        self.list.extend(self.items)
        self.redoStates()


class EditTaskCommand(base.BaseCommand, SaveTaskStateMixin):
    def name(self):
        return _('Edit task')

    def __init__(self, *args, **kwargs):
        super(EditTaskCommand, self).__init__(*args, **kwargs)
        self.saveStates(self.getTasksToSave())
        # FIXME: EditTaskCommand doesn't need to get the tasklist as first argument
        
    def getTasksToSave(self):
        return sets.Set([relative for task in self.items for relative in task.family()])

    def do_command(self):
        super(EditTaskCommand, self).do_command()

    def undo_command(self):
        self.undoStates()
        super(EditTaskCommand, self).undo_command()

    def redo_command(self):
        self.redoStates()
        super(EditTaskCommand, self).redo_command()


class EffortCommand(base.BaseCommand):
    def stopTracking(self):
        self.stoppedEfforts = []
        for task in self.tasksToStopTracking():
            self.stoppedEfforts.extend(task.stopTracking())

    def startTracking(self):
        for effort in self.stoppedEfforts:
            effort.setStop(date.DateTime.max)
    
    def tasksToStopTracking(self):
        return self.list
                
    def do_command(self):
        self.stopTracking()
    
    def undo_command(self):
        self.startTracking()
        
    def redo_command(self):
        self.stopTracking()


class MarkCompletedCommand(EditTaskCommand, EffortCommand):
    def name(self):
        return _('Mark completed')

    def do_command(self):
        super(MarkCompletedCommand, self).do_command()
        for task in self.items:
            task.setCompletionDate()

    def undo_command(self):
        super(MarkCompletedCommand, self).undo_command()

    def tasksToStopTracking(self):
        return self.items


class StartEffortCommand(EffortCommand):
    def name(self):
        return _('Start tracking')

    def __init__(self, *args, **kwargs):
        super(StartEffortCommand, self).__init__(*args, **kwargs)
        start = date.DateTime.now()
        self.efforts = [effort.Effort(task, start) for task in self.items]

    def do_command(self):
        super(StartEffortCommand, self).do_command()
        for task, effort in zip(self.items, self.efforts):
            task.addEffort(effort)
        
    def undo_command(self):
        for task, effort in zip(self.items, self.efforts):
            task.removeEffort(effort)
        super(StartEffortCommand, self).undo_command()
        
    def redo_command(self):
        super(StartEffortCommand, self).redo_command()
        for task, effort in zip(self.items, self.efforts):
            task.addEffort(effort)
        
    
        
class StopEffortCommand(EffortCommand):
    def name(self):
        return _('Stop tracking')
                  
    def canDo(self):
        return True    
               
 