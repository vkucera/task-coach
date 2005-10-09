import base, effort, date
from i18n import _

class NewEffortCommand(base.NewCommand):
    def name(self):
        return _('New effort')
    
    def createItems(self, selectedItems):
        return [effort.Effort(task) for task in selectedItems]
        

class EditEffortCommand(base.EditCommand):
    def name(self):
        return _('Edit effort')
    

class DeleteEffortCommand(base.DeleteCommand):
    def name(self):
        return _('Delete effort')

