
from taskcoachlib.domain import date
from taskcoachlib.domain.task import Task

class Synchronizer(object):
    """Base class for synchronization with remote stores (examples:
    Palm, PSP, Outlook...)

    Dictionnaries used for remote tasks should use strings encoded in
    ISO-8859-15 and dates in the YYYY-MM-DD format.

    @ivar settings: Instance of taskcoachlib.config.settings.Settings."""

    # Names of attributes  that the remote store can  change. For each
    # 'fooBar' name, the  Task class must have a  fooBar() read method
    # and a setFooBar() write method.

    attributeNames = []

    # Each device synchronizer should have a unique dirtyIndex, in the
    # range [0:8].

    dirtyIndex = None

    @classmethod
    def isReady(klass, settings):
        """Subclasses should overload this. It must return a 2-tuple
        (isReady, msg). 'isReady' is a boolean which is True if the
        synchronization can occur now. If it is False, the 'msg'
        message is displayed to the user."""

        raise NotImplementedError

    def __init__(self, settings, *args, **kwargs):
        """Constructor. This should probably not be overriden.

        @todo: use a callback for user messages"""

        super(Synchronizer, self).__init__(*args, **kwargs)

        self.settings = settings

    def __getAttribute(self, task, name):
        value = getattr(task, name)()

        if name in ['subject']:
            return value.encode('ISO-8859-15')
        elif name in ['startDate', 'dueDate', 'completionDate']:
            if value == date.Date():
                return None
            return str(value)

        return value

    def __setAttribute(self, task, name, value):
        if name in ['subject']:
            value = value.decode('ISO-8859-15')
        elif name in ['startDate', 'dueDate', 'completionDate']:
            if value is None:
                value = date.Date()
            else:
                value = date.parseDate(value)

        getattr(task, 'set' + name[0].upper() + name[1:])(value)

    def synchronize(self, taskList):
        """Double-way synchronization."""

        idxLocal = {}

        def addToIndex(task):
            idxLocal[task.id()] = task
            for child in task.children():
                addToIndex(child)

        for task in taskList.rootItems():
            addToIndex(task)

        self.beforeSynchronization()

        # First, get changes from remote store.

        for remoteTask in self.getRemoteChanged():
            if idxLocal.has_key(remoteTask['id']):
                localTask = idxLocal[remoteTask['id']]

                for attrName in self.attributeNames:
                    if self.__getAttribute(localTask, attrName) != remoteTask[attrName]:
                        if localTask.isDirty(self.dirtyIndex):
                            raise NotImplementedError, 'Should ask the user...'
                        else:
                            self.__setAttribute(localTask, attrName, remoteTask[attrName])

            else:
                task = Task()
                for name in self.attributeNames + ['id']:
                    self.__setAttribute(task, name, remoteTask[name])
                task.cleanDirtyFlag(self.dirtyIndex)
                taskList.extend([task])

            self.remoteTaskSynchronized(remoteTask['id'])

        # Next, push local changes to remote store.

        for localTask in idxLocal.values():
            if localTask.isDirty(self.dirtyIndex):
                remoteTask = self.getRemoteTask(localTask.id())

                if remoteTask is None:
                    remoteTask = dict([(name, self.__getAttribute(localTask, name)) \
                            for name in ['id', 'subject', 'startDate', 'dueDate',
                                         'completionDate']])

                    self.addRemoteTask(remoteTask)
                else:
                    for attrName in self.attributeNames:
                        remoteTask[attrName] = self.__getAttribute(task, attrName)
                    self.updateRemoteTask(remoteTask)

                localTask.cleanDirtyFlag(self.dirtyIndex)

        self.afterSynchronization()

    def beforeSynchronization(self):
        """Called when beginning synchronization."""

    def getRemoteChanged(self):
        """Should return a sequence of dictionnaries mapping attribute
        names to their values for tasks that have been modified on the
        remote store."""

        raise NotImplementedError

    def remoteTaskSynchronized(self, taskId):
        """Called when a remote task has been synchronized. Should
        clean the 'dirty' flag."""

        raise NotImplementedError

    def getRemoteTask(self, taskId):
        """Should return a dictionnary mapping attribute names to
        their values for the specified task on the remote store, or
        None if there is none."""

        raise NotImplementedError

    def addRemoteTask(self, task):
        """Should add a task on the remote store."""

        raise NotImplementedError

    def updateRemoteTask(self, task):
        """Should update the specified task on the remote store."""

        raise NotImplementedError

    def afterSynchronization(self):
        """Called when the synchronization is finished."""
