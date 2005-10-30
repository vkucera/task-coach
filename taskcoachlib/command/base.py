import patterns, task
from i18n import _

class BaseCommand(patterns.Command):
    def __init__(self, list=None, items=None, *args, **kwargs):
        super(BaseCommand, self).__init__(*args, **kwargs)
        self.list = list
        self.items = items or []

    def __str__(self):
        return self.name()

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


class CopyCommand(BaseCommand):
    def name(self):
        return _('Copy')

    def do_command(self):
        self.__copies = [item.copy() for item in self.items]
        task.Clipboard().put(self.__copies, self.list)

    def undo_command(self):
        task.Clipboard().clear()

    def redo_command(self):
        task.Clipboard().put(self.__copies, self.list)

        
class DeleteCommand(BaseCommand):
    def name(self):
        return _('Delete')

    def do_command(self):
        self.list.removeItems(self.items)

    def undo_command(self):
        self.list.extend(self.items)

    def redo_command(self):
        self.list.removeItems(self.items)


class CutCommand(DeleteCommand):
    def name(self):
        return _('Cut')

    def __putItemsOnClipboard(self):
        cb = task.Clipboard()
        self.__previousClipboardContents = cb.get()
        cb.put(self.items, self.list)

    def __removeItemsFromClipboard(self):
        cb = task.Clipboard()
        cb.put(*self.__previousClipboardContents)

    def do_command(self):
        self.__putItemsOnClipboard()
        super(CutCommand, self).do_command()

    def undo_command(self):
        self.__removeItemsFromClipboard()
        super(CutCommand, self).undo_command()

    def redo_command(self):
        self.__putItemsOnClipboard()
        super(CutCommand, self).redo_command()

        
class PasteCommand(BaseCommand, SaveStateMixin):
    def name(self):
        return _('Paste')

    def __init__(self, *args, **kwargs):
        super(PasteCommand, self).__init__(*args, **kwargs)
        self.__itemsToPaste, self.__sourceOfItemsToPaste = task.Clipboard().get()
        self.saveStates(self.getItemsToSave())

    def getItemsToSave(self):
        return self.__itemsToPaste
    
    def canDo(self):
        return bool(self.__itemsToPaste)
        
    def do_command(self):
        self.setParentOfPastedItems()
        self.__sourceOfItemsToPaste.extend(self.__itemsToPaste)

    def undo_command(self):
        self.__sourceOfItemsToPaste.removeItems(self.__itemsToPaste)
        self.undoStates()
        task.Clipboard().put(self.__itemsToPaste, self.__sourceOfItemsToPaste)
        
    def redo_command(self):
        task.Clipboard().clear() 
        self.redoStates()
        self.__sourceOfItemsToPaste.extend(self.__itemsToPaste)

    def setParentOfPastedItems(self, newParent=None):
        for item in self.__itemsToPaste:
            item.setParent(newParent) 

    

        