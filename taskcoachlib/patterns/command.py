import singleton as patterns

class Command(object):
    def do(self):
        CommandHistory().append(self)

    def undo(self):
        pass

    def redo(self):
        pass


class CommandHistory:
    __metaclass__ = patterns.Singleton

    def __init__(self):
        self.history = []
        self.future = []

    def append(self, command):
        self.history.append(command)
        del self.future[:]

    def undo(self, *args):
        if self.history:
            command = self.history.pop()
            command.undo()
            self.future.append(command)

    def redo(self, *args):
        if self.future:
            command = self.future.pop()
            command.redo()
            self.history.append(command)

    def clear(self):
        del self.history[:]
        del self.future[:]

    def hasHistory(self):
        return self.history

    def hasFuture(self):
        return self.future

    def _extendLabel(self, label, commandList):
        if commandList:
            label += ' %s'%commandList[-1]
        return label

    def undostr(self, label='Undo'):
        return self._extendLabel(label, self.history)

    def redostr(self, label='Redo'):
        return self._extendLabel(label, self.future)


