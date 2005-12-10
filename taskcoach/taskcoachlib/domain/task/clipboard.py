import patterns 

class Clipboard:
    __metaclass__ = patterns.Singleton

    def __init__(self):
        self.clear()

    def put(self, items, source):
        self._contents = items
        self._source = source

    def get(self):
        currentContents = self._contents
        currentSource = self._source
        self.clear()
        return currentContents, currentSource

    def clear(self):
        self._contents = []
        self._source = None

    def __nonzero__(self):
        return len(self._contents)

