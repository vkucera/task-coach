import base
from i18n import _
from domain import task, effort, date


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
    def name(self):
        return _('Delete task')


class NewTaskCommand(base.BaseCommand):
    def name(self):
        return _('New task')

    def __init__(self, *args, **kwargs):
        subject = kwargs.pop('subject', _('New task'))
        description = kwargs.pop('description', '')
        attachments = kwargs.pop('attachments', None)
        categories = kwargs.pop('categories', [])
        super(NewTaskCommand, self).__init__(*args, **kwargs)
        self.items = [task.Task(subject=subject, description=description, 
                                attachments=attachments, categories=categories)]
        
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
    
    def __init__(self, *args, **kwargs):
        super(EditTaskCommand, self).__init__(*args, **kwargs)
        self.oldCategories = [task.categories() for task in self.items]
        
    def do_command(self):
        super(EditTaskCommand, self).do_command()
        self.newCategories = [task.categories() for task in self.items]
        self.updateCategories(self.oldCategories, self.newCategories)
        
    def undo_command(self):
        super(EditTaskCommand, self).undo_command()
        self.updateCategories(self.newCategories, self.oldCategories)
        
    def redo_command(self):
        super(EditTaskCommand, self).redo_command()
        self.updateCategories(self.oldCategories, self.newCategories)

    def getItemsToSave(self):
        return set([relative for task in self.items for relative in task.family()])
        
    def updateCategories(self, oldCategories, newCategories):
        for task, categories in zip(self.items, oldCategories):
            for category in categories:
                category.removeCategorizable(task)
        for task, categories in zip(self.items, newCategories):
            for category in categories:
                category.addCategorizable(task)
        
        
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
            if task.completed():
                task.setCompletionDate(date.Date())
            else:
                task.setCompletionDate()

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



class ExtremePriorityCommand(base.BaseCommand):
    def __init__(self, *args, **kwargs):
        super(ExtremePriorityCommand, self).__init__(*args, **kwargs)
        self.oldPriorities = [task.priority() for task in self.items]
        self.oldExtremePriority = self.oldExtremePriority() 

    def setNewExtremePriority(self):
        newExtremePriority = self.oldExtremePriority + self.delta 
        for task in self.items:
            task.setPriority(newExtremePriority)
            
    def newExtremePriority(self):
        raise NotImplementedError
        
    def restorePriorities(self):
        for task, oldPriority in zip(self.items, self.oldPriorities):
            task.setPriority(oldPriority)

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
    def name(self):
        return _('Maximize priority')
    
    delta = +1
    
    def oldExtremePriority(self):
        return self.list.maxPriority()
    

class MinPriorityCommand(ExtremePriorityCommand):
    def name(self):
        return _('Minimize priority')
    
    delta = -1
                    
    def oldExtremePriority(self):
        return self.list.minPriority()
    

class ChangePriorityCommand(base.BaseCommand):
    def changePriorities(self, delta):
        for task in self.items:
            task.setPriority(task.priority() + delta)

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
    def name(self):
        return _('Increase priority')

    delta = +1


class DecPriorityCommand(ChangePriorityCommand):
    def name(self):
        return _('Decrease priority')

    delta = -1
    
