import patterns

class BaseCommand(patterns.Command):
    def __init__(self, list, selectedItems=None, *args, **kwargs):
        super(BaseCommand, self).__init__(*args, **kwargs)
        self.list = list
        self.selectedItems = selectedItems or []
        self.items = self.createItems(self.selectedItems) 
        self.__saveStates(self.getItemsToSave())

    def createItems(self, selectedItems):
        ''' By default, a command operates on the selected items. '''
        return selectedItems

    def getItemsToSave(self):
        ''' By default, no item states need to be saved. '''
        return []

    def canDo(self):
        return bool(self.items)
        
    def do(self):
        if self.canDo():
            super(BaseCommand, self).do()
            self.do_command()
            
    def undo(self):
        super(BaseCommand, self).undo()
        self.undo_command()
        self.__undoStates()

    def redo(self):
        super(BaseCommand, self).redo()
        self.redo_command()
        self.__redoStates()

    def do_command(self):
        self.__tryInvokeMethodOnSuper('do_command')
        
    def undo_command(self):
        self.__tryInvokeMethodOnSuper('undo_command')
        
    def redo_command(self):
        self.__tryInvokeMethodOnSuper('redo_command')

    def __tryInvokeMethodOnSuper(self, methodName, *args, **kwargs):
        try:
            method = getattr(super(BaseCommand, self), methodName)
        except AttributeError:
            return # no 'method' in any super class
        return method(*args, **kwargs)
        
    def __saveStates(self, objects):
        self.__objectsToBeSaved = objects
        self.__oldStates = self.__getStates()

    def __undoStates(self):
        self.__newStates = self.__getStates()
        self.__setStates(self.__oldStates)

    def __redoStates(self):
        self.__setStates(self.__newStates)

    def __getStates(self):
        return [object.__getstate__() for object in self.__objectsToBeSaved]

    def __setStates(self, states):
        for object, state in zip(self.__objectsToBeSaved, states):
            object.__setstate__(state)

    def __str__(self):
        return self.name()


class DeleteCommand(BaseCommand):
    def do_command(self):
        super(DeleteCommand, self).do_command()
        self.list.removeItems(self.items)

    def undo_command(self):
        super(DeleteCommand, self).undo_command()
        self.list.extend(self.items)

    def redo_command(self):
        super(DeleteCommand, self).redo_command()
        self.list.removeItems(self.items)


class NewCommand(BaseCommand):
    def createItems(self, selectedItems):
        raise NotImplementedError

    def do_command(self):
        super(NewCommand, self).do_command()
        self.list.extend(self.items)

    def undo_command(self):
        super(NewCommand, self).undo_command()
        self.list.removeItems(self.items)

    def redo_command(self):
        super(NewCommand, self).redo_command()
        self.list.extend(self.items)


class EditCommand(BaseCommand):
    def getItemsToSave(self):
        ''' Of which items do we need to save the current state so that
            it can be restored in case of an undo? '''
        return self.items
