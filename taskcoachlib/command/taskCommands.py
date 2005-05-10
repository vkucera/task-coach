import task, date, base, effort
import sets
from i18n import _

class SaveTaskStateMixin(base.SaveStateMixin):
    def getAncestors(self, tasks): 
        ancestors = []
        for task in tasks:
            ancestors.extend(task.ancestors())
        return ancestors


class DeleteTaskCommand(base.BaseCommand, SaveTaskStateMixin):
    def name(self):
        return _('Delete task')

    def __init__(self, *args, **kwargs):
        super(DeleteTaskCommand, self).__init__(*args, **kwargs)
        self.saveStates(self.getTasksToSave())

    def getTasksToSave(self):
        return self.getAncestors(self.items)

    def do_command(self):
        self.list.removeItems(self.items)

    def undo_command(self):
        self.undoStates()
        self.list.extend(self.items)

    def redo_command(self):
        self.list.removeItems(self.items)
        self.redoStates()


class CutTaskCommand(DeleteTaskCommand):
    def name(self):
        return _('Cut')

    def putTasksOnClipboard(self):
        cb = task.Clipboard()
        self.previousClipboardContents = cb.get()
        cb.put(self.items)

    def removeTasksFromClipboard(self):
        cb = task.Clipboard()
        cb.put(self.previousClipboardContents)

    def do_command(self):
        self.putTasksOnClipboard()
        super(CutTaskCommand, self).do_command()

    def undo_command(self):
        self.removeTasksFromClipboard()
        super(CutTaskCommand, self).undo_command()

    def redo_command(self):
        self.putTasksOnClipboard()
        super(CutTaskCommand, self).redo_command()


class CopyTaskCommand(base.BaseCommand):
    def name(self):
        return _('Copy')

    def do_command(self):
        self.copies = [origTask.copy() for origTask in self.items]
        task.Clipboard().put(self.copies)

    def undo_command(self):
        task.Clipboard().clear()

    def redo_command(self):
        task.Clipboard().put(self.copies)
        

class PasteTaskCommand(base.BaseCommand, SaveTaskStateMixin):
    def name(self):
        return _('Paste')

    def __init__(self, *args, **kwargs):
        super(PasteTaskCommand, self).__init__(*args, **kwargs)
        self.tasksToPaste = task.Clipboard().get()
        self.saveStates(self.tasksToPaste)

    def canDo(self):
        return bool(self.tasksToPaste)
        
    def do_command(self):
        self.setParentOfPastedTasks()
        self.list.extend(self.tasksToPaste)

    def undo_command(self):
        self.list.removeItems(self.tasksToPaste)
        self.undoStates()
        task.Clipboard().put(self.tasksToPaste)
        
    def redo_command(self):
        task.Clipboard().clear() 
        self.redoStates()
        self.list.extend(self.tasksToPaste)

    def setParentOfPastedTasks(self, newParent=None):
        for task in self.tasksToPaste:
            task.setParent(newParent) 


class PasteTaskAsSubtaskCommand(PasteTaskCommand):
    def name(self):
        return _('Paste as subtask')

    def __init__(self, *args, **kwargs):
        super(PasteTaskAsSubtaskCommand, self).__init__(*args, **kwargs)
        self.saveStates(self.getTasksToSave())

    def do_command(self):
        super(PasteTaskAsSubtaskCommand, self).do_command()

    def setParentOfPastedTasks(self):
        newParent = self.items[0]
        super(PasteTaskAsSubtaskCommand, self).setParentOfPastedTasks(newParent)

    def getTasksToSave(self):
        parents = [task for task in [self.items[0]] if task.completed()]
        return parents + self.getAncestors(parents)



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
               
 