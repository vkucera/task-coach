import base, effort, date

class NewEffortCommand(base.BaseCommand):
    name = 'New effort'
    
    def __init__(self, *args, **kwargs):
        super(NewEffortCommand, self).__init__(*args, **kwargs)
        self.efforts = [effort.Effort(task) for task in self.items]
        
    def do_command(self):
        self.list.extend(self.efforts)
            
    def undo_command(self):
        self.list.removeItems(self.efforts)
            
    redo_command = do_command


class EditEffortCommand(base.BaseCommand, base.SaveStateMixin):
    # FIXME: Duplication with EditTaskCommand
    name = 'Edit effort'
    
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
    

class DeleteEffortCommand(base.BaseCommand):
    name = 'Delete effort'

    def __init__(self, *args, **kwargs):
        super(DeleteEffortCommand, self).__init__(*args, **kwargs)
        self.efforts = self.items # FIXME: hack

    def do_command(self):
        self.list.removeItems(self.items)

    def undo_command(self):
        self.list.extend(self.items)

    redo_command = do_command


class StartEffortCommand(base.BaseCommand, base.SaveStateMixin):
    name = 'Start tracking'

    def __init__(self, *args, **kwargs):
        super(StartEffortCommand, self).__init__(*args, **kwargs)
        adjacent = 'adjacent' in kwargs and kwargs['adjacent']
        if adjacent:
            start = self.list.maxDateTime() or date.DateTime.now()
        else:
            start = date.DateTime.now()
        self.saveStates(self.getEffortsToSave())
        self.efforts = [effort.Effort(task, start) for task in self.items]

    def getEffortsToSave(self):
        return [effort for effort in self.list if effort.getStop() is None]
               
    def do_command(self):
        self.list.stopTracking()
        self.list.extend(self.efforts)
        
    def undo_command(self):
        self.list.removeItems(self.efforts)
        self.undoStates()
        
    def redo_command(self):
        self.list.extend(self.efforts)
        self.redoStates()
    
        
class StopEffortCommand(base.BaseCommand, base.SaveStateMixin):
    name = 'Stop tracking'
    
    def __init__(self, *args, **kwargs):
        super(StopEffortCommand, self).__init__(*args, **kwargs)
        self.saveStates(self.getEffortsToSave())
 
    def getEffortsToSave(self):
        return [effort for effort in self.list if effort.getStop() is None]
               
    def canDo(self):
        return True    
        
    def do_command(self):
        self.list.stopTracking()
        
    def undo_command(self):
        self.undoStates()
        
    def redo_command(self):
        self.redoStates()