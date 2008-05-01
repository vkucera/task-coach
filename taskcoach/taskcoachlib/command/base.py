'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>

Task Coach is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Task Coach is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from taskcoachlib import patterns
from taskcoachlib.i18n import _
from taskcoachlib.domain import task


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


class CompositeMixin(object):
    ''' Mixin class for commands that deal with composites. '''
    def getAncestors(self, composites): 
        ancestors = []
        for composite in composites:
            ancestors.extend(composite.ancestors())
        return ancestors
    
    def getAllChildren(self, composites):
        allChildren = []
        for composite in composites:
            allChildren.extend(composite.children(recursive=True))
        return allChildren

    def getAllParents(self, composites):
        return [composite.parent() for composite in composites \
                if composite.parent() != None]


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
        self.__itemsToPaste, self.__sourceOfItemsToPaste = self.getItemsToPaste()
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
        self.restoreItemsToPasteToSource()
        
    def redo_command(self):
        self.clearSourceOfItemsToPaste()
        self.redoStates()
        self.__sourceOfItemsToPaste.extend(self.__itemsToPaste)

    def setParentOfPastedItems(self, newParent=None):
        for item in self.__itemsToPaste:
            item.setParent(newParent) 
    
    # Clipboard interaction:
    def getItemsToPaste(self):
        return task.Clipboard().get()

    def restoreItemsToPasteToSource(self):
        task.Clipboard().put(self.__itemsToPaste, self.__sourceOfItemsToPaste)
        
    def clearSourceOfItemsToPaste(self):
        task.Clipboard().clear() 
        
        
class EditCommand(BaseCommand, SaveStateMixin):
    def __init__(self, *args, **kwargs):
        super(EditCommand, self).__init__(*args, **kwargs)
        self.saveStates(self.getItemsToSave())
        
    def getItemsToSave(self):
        raise NotImplementedError
        
    def undo_command(self):
        self.undoStates()
        super(EditCommand, self).undo_command()

    def redo_command(self):
        self.redoStates()
        super(EditCommand, self).redo_command()
        

class DragAndDropCommand(BaseCommand, SaveStateMixin, CompositeMixin):
    def name(self):
        return _('Drag and drop')
    
    def __init__(self, *args, **kwargs):
        dropTargets = kwargs.pop('drop')
        if dropTargets:
            self.__itemToDropOn = dropTargets[0]
        else:
            self.__itemToDropOn = None
        super(DragAndDropCommand, self).__init__(*args, **kwargs)
        self.saveStates(self.getItemsToSave())
        
    def getItemsToSave(self):
        if self.__itemToDropOn is None:
            return self.items
        else:
            return [self.__itemToDropOn] + self.items
    
    def canDo(self):
        return self.__itemToDropOn not in (self.items + \
            self.getAllChildren(self.items) + self.getAllParents(self.items))
    
    def do_command(self):
        self.list.removeItems(self.items)
        for item in self.items:
            item.setParent(self.__itemToDropOn)
        self.list.extend(self.items)
        
    def undo_command(self):
        self.list.removeItems(self.items)
        self.undoStates()
        self.list.extend(self.items)
        
    def redo_command(self):
        self.list.removeItems(self.items)
        self.redoStates()
        self.list.extend(self.items)
        
