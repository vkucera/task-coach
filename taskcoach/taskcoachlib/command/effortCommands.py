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


class StartEffortCommand(base.BaseCommand):
    name = 'Start tracking'

    def __init__(self, *args, **kwargs):
        self._startAdjacent = 'adjacent' in kwargs and kwargs['adjacent']
        super(StartEffortCommand, self).__init__(*args, **kwargs)
        
    def do_command(self):
        self.previousTasks = self.list.getActiveTasks()
        self.start = self.list.start()
        self.stop = date.DateTime.now()
        self.efforts = []
        for task in self.previousTasks:
            self.efforts.append(effort.Effort(task, self.start, self.stop))
        self.list.setActiveTasks(self.items, adjacent=self._startAdjacent)
        self.list.extend(self.efforts)
        
    def undo_command(self):
        self.list.setActiveTasks(self.previousTasks)
        self.list.removeItems(self.efforts)
        
    def redo_command(self):
        self.list.setActiveTasks(self.items)
        self.list.extend(self.efforts)

        
class StopEffortCommand(base.BaseCommand):
    name = 'Stop tracking'
    
    def canDo(self):
        return True
        
    def do_command(self):
        self.activeTasks = self.list.getActiveTasks()
        self.start = self.list.start()
        self.stop = date.DateTime.now()
        self.efforts = []
        for task in self.activeTasks:
            self.efforts.append(effort.Effort(task, self.start, self.stop))
        self.redo_command()
        
    def undo_command(self):
        self.list.setActiveTasks(self.activeTasks, self.start)
        self.list.removeItems(self.efforts)
        
    def redo_command(self):
        self.list.setActiveTasks([])
        self.list.extend(self.efforts)
