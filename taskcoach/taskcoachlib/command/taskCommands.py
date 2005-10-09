import task, date, base, effort
import sets
from i18n import _

def getAncestors(*tasks): 
    ancestors = []
    for task in tasks:
        ancestors.extend(task.ancestors())
    return ancestors


class DeleteTaskCommand(base.DeleteCommand):
    def name(self):
        return _('Delete task')


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
        super(CutTaskCommand, self).do_command()
        self.putTasksOnClipboard()

    def undo_command(self):
        super(CutTaskCommand, self).undo_command()
        self.removeTasksFromClipboard()

    def redo_command(self):
        super(CutTaskCommand, self).redo_command()
        self.putTasksOnClipboard()


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
        

class PasteTaskCommand(base.NewCommand):
    def name(self):
        return _('Paste')

    def createItems(self, selectedItems):
        return task.Clipboard().get()

    def getItemsToSave(self):
        return self.items 

    def do_command(self):
        self.setParentOfPastedTasks()
        super(PasteTaskCommand, self).do_command()
        
    def undo_command(self):
        super(PasteTaskCommand, self).undo_command()
        task.Clipboard().put(self.items)
        print task.Clipboard()._contents
        
    def redo_command(self):
        self.setParentOfPastedTasks()
        super(PasteTaskCommand, self).redo_command()
        task.Clipboard().clear() 

    def setParentOfPastedTasks(self):
        ''' Before we paste the tasks in the taskList, set the parent. '''
        newParent = self.newParentOfPastedTasks()
        for task in self.items:
            task.setParent(newParent) 

    def newParentOfPastedTasks(self):
        ''' This command pastes tasks as root tasks, so whatever their parent
            was before, it is now None (i.e. they have no parent task). '''
        return None


class PasteTaskAsSubtaskCommand(PasteTaskCommand):
    def name(self):
        return _('Paste as subtask')

    def getItemsToSave(self):
        ''' We save the state of the tasks to be pasted, the task they
            are pasted as subtask to, and any ancestors of that task. '''
        return self.items + [self.newParentOfPastedTasks()] + \
            getAncestors(self.newParentOfPastedTasks())

    def newParentOfPastedTasks(self):
        ''' This command pastes tasks as subtasks, so whatever their parent
            was before, it is now the first of the selected tasks. '''
        return self.selectedItems[0]


class NewTaskCommand(base.NewCommand):
    def name(self):
        return _('New task')

    def createItems(self, selectedItems):
        return [self.list.newItem()]


class NewSubTaskCommand(base.NewCommand):
    def name(self):
        return _('New subtask')

    def createItems(self, selectedItems):
        return [task.newSubTask(subject=_('New subtask')) for task in selectedItems]
        
    def getItemsToSave(self):
        return self.selectedItems + getAncestors(*self.selectedItems)


class EditTaskCommand(base.EditCommand):
    def name(self):
        return _('Edit task')

    def getItemsToSave(self):
        return sets.Set([relative for task in self.items for relative in task.family()])


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
               
 
