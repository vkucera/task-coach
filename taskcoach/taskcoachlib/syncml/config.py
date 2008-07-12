
"""

Classes for storing Funambol client configuration

"""

class SyncMLConfigNode(object):
    def __init__(self, name):
        super(SyncMLConfigNode, self).__init__()

        self.name = name

        self.__children = []
        self.__properties = {}

    def children(self):
        return self.__children

    def properties(self):
        return self.__properties.items()

    def addChild(self, child):
        self.__children.append(child)

    def get(self, name):
        return self.__properties.get(name, '')

    def set(self, name, value):
        self.__properties[name] = value

    def __getitem__(self, name):
        for child in self.__children:
            if child.name == name:
                return child
        raise KeyError, name
