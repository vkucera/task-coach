import base
from i18n import _
import domain.task as task
import domain.effort as effort
import domain.date as date

class SaveTaskStateMixin(base.SaveStateMixin, base.CompositeMixin):
    pass


class PasteIntoTaskCommand(base.PasteCommand, base.CompositeMixin):
    def name(self):
        return _('Paste into task')

    def setParentOfPastedItems(self):
        newParent = self.items[0]
        super(PasteIntoTaskCommand, self).setParentOfPastedItems(newParent)

    def getItemsToSave(self):
        parents = [task for task in [self.items[0]] if task.completed()]
        return parents + self.getAncestors(parents) + \
            super(PasteIntoTaskCommand, self).getItemsToSave()


class DragAndDropTaskCommand(base.DragAndDropCommand):
    def name(self):
        return _('Drag and drop task')


class DeleteTaskCommand(base.DeleteCommand):
    def __init__(self, *args, **kwargs):
        self.__categories = kwargs.pop('categories')
        self.__map = {}
        super(DeleteTaskCommand, self).__init__(*args, **kwargs)

    def do_command(self):
        for category in self.__categories:
            for task in self.items:
                if task in category.tasks():
                    category.removeTask(task)
                    self.__map.setdefault(task, []).append(category)
        super(DeleteTaskCommand, self).do_command()
        
    def undo_command(self):
        for task in self.__map:
            for category in self.__map[task]:
                category.addTask(task)
        super(DeleteTaskCommand, self).undo_command()
        
    def redo_command(self):
        for task in self.__map:
            for category in self.__map[task]:
                category.removeTask(task)
        super(DeleteTaskCommand, self).redo_command()


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
        self.items = [task.newChild(subject=_('New subtask')) for task in self.items]
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


class EditTaskCommand(base.EditCommand):
    def name(self):
        return _('Edit task')
        
    def getItemsToSave(self):
        return set([relative for task in self.items for relative in task.family()])
        
        
class AddAttachmentToTaskCommand(base.BaseCommand):
    def name(self):
        return _('Add attachment')
    
    def __init__(self, *args, **kwargs):
        self.__attachments = kwargs.pop('attachments')
        super(AddAttachmentToTaskCommand, self).__init__(*args, **kwargs)

    def addAttachments(self):
        for task in self.items:
            task.addAttachments(*self.__attachments)
        
    def removeAttachments(self):
        for task in self.items:
            task.removeAttachments(*self.__attachments)
                
    def do_command(self):
        self.addAttachments()
        
    def undo_command(self):
        self.removeAttachments()

    def redo_command(self):
        self.addAttachments()
        
        
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
               
 
