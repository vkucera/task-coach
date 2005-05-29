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


class CommandHistory:
    __metaclass__ = patterns.Singleton

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


