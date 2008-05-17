
import test
from taskcoachlib.synchronization import Synchronizer
from taskcoachlib.domain import task, date

class FakeTaskList(list):
    def rootItems(self):
        return self

class SynchronizerTest(test.TestCase, Synchronizer):
    dirtyIndex = 0
    attributeNames = ['startDate']

    def testNewOnDesktopNoDate(self):
        localTasks = FakeTaskList([task.Task('subject', startDate=date.Date())])
        self.remoteTasks = []

        self.synchronize(localTasks)

        self.assertEqual(len(self.remoteTasks), 1)
        self.assertEqual(self.remoteTasks[0]['id'], localTasks[0].id())
        self.assertEqual(self.remoteTasks[0]['startDate'], None)
        self.failIf(localTasks[0].isDirty(self.dirtyIndex))
        self.failIf(self.remoteTasks[0]['dirty'])

    def testNewOnDesktopDate(self):
        localTasks = FakeTaskList([task.Task('subject', startDate=date.Date(2008, 5, 17))])
        self.remoteTasks = []

        self.synchronize(localTasks)

        self.assertEqual(len(self.remoteTasks), 1)
        self.assertEqual(self.remoteTasks[0]['id'], localTasks[0].id())
        self.assertEqual(self.remoteTasks[0]['startDate'], '2008-05-17')
        self.failIf(localTasks[0].isDirty(self.dirtyIndex))
        self.failIf(self.remoteTasks[0]['dirty'])

    def testNewOnRemoteNoDate(self):
        localTasks = FakeTaskList()
        self.remoteTasks = [{'id': 'foo', 'startDate': None, 'dirty': True}]

        self.synchronize(localTasks)

        self.assertEqual(len(localTasks), 1)
        self.assertEqual(localTasks[0].id(), 'foo')
        self.assertEqual(localTasks[0].startDate(), date.Date())
        self.failIf(localTasks[0].isDirty(self.dirtyIndex))
        self.failIf(self.remoteTasks[0]['dirty'])

    def testNewOnRemoteDate(self):
        localTasks = FakeTaskList()
        self.remoteTasks = [{'id': 'foo', 'startDate': '2008-05-17', 'dirty': True}]

        self.synchronize(localTasks)

        self.assertEqual(len(localTasks), 1)
        self.assertEqual(localTasks[0].id(), 'foo')
        self.assertEqual(localTasks[0].startDate(), date.Date(2008, 5, 17))
        self.failIf(localTasks[0].isDirty(self.dirtyIndex))
        self.failIf(self.remoteTasks[0]['dirty'])

    def testNewOnDesktopNotDirty(self):
        localTasks = FakeTaskList([task.Task('subject')])
        localTasks[0].cleanDirtyFlag(self.dirtyIndex)
        self.remoteTasks = []

        self.synchronize(localTasks)

        self.assertEqual(len(self.remoteTasks), 0)

    def testNewOnRemoteNotDirty(self):
        localTasks = FakeTaskList()
        self.remoteTasks = [{'id': 'foo', 'startDate': '2008-05-17', 'dirty': False}]

        self.synchronize(localTasks)

        self.assertEqual(len(localTasks), 0)

    def testLocalChanged(self):
        localTasks = FakeTaskList([task.Task(u'subject1', startDate=date.Date(2008, 5, 17))])
        self.remoteTasks = [{'id': localTasks[0].id(),
                             'subject': 'subject2',
                             'startDate': '2008-05-16',
                             'dirty': False}]

        self.synchronize(localTasks)

        self.assertEqual(len(self.remoteTasks), 1)
        self.assertEqual(self.remoteTasks[0]['subject'], 'subject2')
        self.assertEqual(self.remoteTasks[0]['startDate'], '2008-05-17')
        self.failIf(localTasks[0].isDirty(self.dirtyIndex))
        self.failIf(self.remoteTasks[0]['dirty'])

    def testRemoteChanged(self):
        localTasks = FakeTaskList([task.Task(u'subject1', startDate=date.Date(2008, 5, 17))])
        self.remoteTasks = [{'id': localTasks[0].id(),
                             'subject': 'subject2',
                             'startDate': '2008-05-16',
                             'dirty': True}]
        localTasks[0].cleanDirtyFlag(self.dirtyIndex)

        self.synchronize(localTasks)

        self.assertEqual(len(localTasks), 1)
        self.assertEqual(localTasks[0].subject(), u'subject1')
        self.assertEqual(localTasks[0].startDate(), date.Date(2008, 5, 16))
        self.failIf(localTasks[0].isDirty(self.dirtyIndex))
        self.failIf(self.remoteTasks[0]['dirty'])

    #======================================
    # Synchronizer methods

    def getRemoteChanged(self):
        return [ task for task in self.remoteTasks if task['dirty'] ]

    def remoteTaskSynchronized(self, taskId):
        for task in self.remoteTasks:
            if task['id'] == taskId:
                task['dirty'] = False
                break
        else:
            self.fail('No such task: %s' % taskId)

    def getRemoteTask(self, taskId):
        for task in self.remoteTasks:
            if task['id'] == taskId:
                return task
        return None

    def addRemoteTask(self, task):
        task['dirty'] = False
        self.remoteTasks.append(task)

    def updateRemoteTask(self, task):
        pass
