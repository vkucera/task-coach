import patterns 

class Clipboard:
    __metaclass__ = patterns.Singleton

    def __init__(self):
        self.clear()

    def put(self, tasks):
        self._contents = tasks

    def get(self):
        currentContents = self._contents
        self.clear()
        return currentContents

    def clear(self):
        self._contents = []

    def __nonzero__(self):
        return len(self._contents)

