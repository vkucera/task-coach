
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

def createDefaultSyncConfig(uid):
    cfg = SyncMLConfigNode('root')
    root = SyncMLConfigNode('TaskCoach-%s' % uid)
    cfg.addChild(root)
    spds = SyncMLConfigNode('spds')
    root.addChild(spds)
    sources = SyncMLConfigNode('sources')
    spds.addChild(sources)
    syncml = SyncMLConfigNode('syncml')
    spds.addChild(syncml)
    tasks = SyncMLConfigNode('TaskCoach-%s.Tasks' % uid)
    sources.addChild(tasks)
    notes = SyncMLConfigNode('TaskCoach-%s.Notes' % uid)
    sources.addChild(notes)
    auth = SyncMLConfigNode('Auth')
    syncml.addChild(auth)
    conn = SyncMLConfigNode('Conn')
    syncml.addChild(conn)

    return cfg
