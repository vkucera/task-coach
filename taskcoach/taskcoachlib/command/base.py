import patterns

class BaseCommand(patterns.Command):
    def __init__(self, list, items=None, *args, **kwargs):
        super(BaseCommand, self).__init__(*args, **kwargs)
        self.list = list
        self.items = items or []

    def __str__(self):
        return self.name

    def canDo(self):
        return bool(self.items)
        
    def do(self):
        if self.canDo():
            super(BaseCommand, self).do()
            self.do_command()
            
    def undo(self):
        super(BaseCommand, self).undo()
        self.undo_command()

    def redo(self):
        super(BaseCommand, self).redo()
        self.redo_command()

    def __tryInvokeMethodOnSuper(self, methodName, *args, **kwargs):
        try:
            method = getattr(super(BaseCommand, self), methodName)
        except AttributeError:
            return # no 'method' in any super class
        return method(*args, **kwargs)
        
    def do_command(self):
        self.__tryInvokeMethodOnSuper('do_command')
        
    def undo_command(self):
        self.__tryInvokeMethodOnSuper('undo_command')
        
    def redo_command(self):
        self.__tryInvokeMethodOnSuper('redo_command')
        

class SaveStateMixin:
    ''' Mixin class for commands that need to keep the states of objects. 
        Objects should provide __getstate__ and __setstate__ methods. '''
        
    def saveStates(self, objects):
        self.objectsToBeSaved = objects
        self.oldStates = self.__getStates()

    def undoStates(self):
        self.newStates = self.__getStates()
        self.__setStates(self.oldStates)

    def redoStates(self):
        self.__setStates(self.newStates)

    def __getStates(self):
        return [object.__getstate__() for object in self.objectsToBeSaved]

    def __setStates(self, states):
        for object, state in zip(self.objectsToBeSaved, states):
            object.__setstate__(state)

