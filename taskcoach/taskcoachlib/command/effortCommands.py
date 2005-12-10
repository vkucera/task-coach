import base
from i18n import _
import domain.effort as effort
import domain.date as date

class NewEffortCommand(base.BaseCommand):
    def name(self):
        return _('New effort')
    
    def __init__(self, *args, **kwargs):
        super(NewEffortCommand, self).__init__(*args, **kwargs)
        self.efforts = [effort.Effort(task) for task in self.items]
        
    def do_command(self):
        for task, effort in zip(self.items, self.efforts):
            task.addEffort(effort)
            
    def undo_command(self):
        for task, effort in zip(self.items, self.efforts):
            task.removeEffort(effort)
            
    redo_command = do_command


class EditEffortCommand(base.BaseCommand, base.SaveStateMixin):
    # FIXME: Duplication with EditTaskCommand
    def name(self):
        return _('Edit effort')
    
    def __init__(self, *args, **kwargs):
        super(EditEffortCommand, self).__init__(*args, **kwargs)
        self.saveStates(self.getEffortsToSave())
        self.efforts = self.items # FIXME: hack
        # FIXME: EditEffortCommand doesn't need the (effort)list argument

    def getEffortsToSave(self):
        return self.items

    def do_command(self):
        pass

    def undo_command(self):
        self.undoStates()

    def redo_command(self):
        self.redoStates()
    
