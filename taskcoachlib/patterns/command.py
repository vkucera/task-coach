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

import singleton as patterns

class Command(object):
    def do(self):
        CommandHistory().append(self)

    def undo(self):
        pass

    def redo(self):
        pass

    def __str__(self):
        return 'command'


class AggregateCommand(Command):
    def __init__(self, commands):
        super(AggregateCommand, self).__init__()

        self.__commands = commands

    def undo(self):
        commands = self.__commands[:]
        commands.reverse()
        for command in commands:
            command.undo()

    def redo(self):
        for command in self.__commands:
            command.redo()


class CommandHistoryLayer:
    def __init__(self):
        self.__history = []
        self.__future = []

    def append(self, command):
        self.__history.append(command)
        del self.__future[:]

    def undo(self, *args):
        if self.__history:
            command = self.__history.pop()
            command.undo()
            self.__future.append(command)

    def redo(self, *args):
        if self.__future:
            command = self.__future.pop()
            command.redo()
            self.__history.append(command)

    def clear(self):
        del self.__history[:]
        del self.__future[:]

    def hasHistory(self):
        return self.__history
        
    def getHistory(self):
        return self.__history
        
    def hasFuture(self):
        return self.__future

    def getFuture(self):
        return self.__future
        
    def _extendLabel(self, label, commandList):
        if commandList:
            commandName = u' %s'%commandList[-1]
            label += commandName.lower()
        return label

    def undostr(self, label='Undo'):
        return self._extendLabel(label, self.__history)

    def redostr(self, label='Redo'):
        return self._extendLabel(label, self.__future)


class CommandHistory:
    __metaclass__ = patterns.Singleton

    def __init__(self):
        self.__stack = [CommandHistoryLayer()]

    def push(self):
        self.__stack.append(CommandHistoryLayer())

    def pop(self, keep=True):
        layer = self.__stack.pop()

        cmd = AggregateCommand(layer.getHistory())
        if keep:
            self.__stack[-1].append(cmd)
        else:
            cmd.undo()

    def clear(self):
        self.__stack = [CommandHistoryLayer()]

    def __getattr__(self, name):
        return getattr(self.__stack[-1], name)


## def _dump(node, indent=0):
##     if isinstance(node, CommandHistory):
##         for layer in node._CommandHistory__stack:
##             _dump(layer)
##     elif isinstance(node, CommandHistoryLayer):
##         if not (node.getHistory() or node.getFuture()):
##             print (' ' * indent) + 'Empty layer'
##         else:
##             print (' ' * indent) + 'Layer'
##             if node.getHistory():
##                 print (' ' * indent) + 'History:'
##                 for command in node.getHistory():
##                     _dump(command, indent + 2)
##             if node.getFuture():
##                 print (' ' * indent) + 'Future:'
##                 for command in node.getFuture():
##                     _dump(command, indent + 2)
##     elif isinstance(node, AggregateCommand):
##         print (' ' * indent) + 'Aggregate command'
##         for command in node._AggregateCommand__commands:
##             _dump(command, indent + 2)
##     else:
##         print (' ' * indent) + str(node)
