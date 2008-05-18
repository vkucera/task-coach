
"""

Synchronization class for the PSP. This is intended for my
minimalistic PSP version of TaskCoach (URL to come).

fraca7

"""

from taskcoachlib.synchronization.synchronizer import Synchronizer
from taskcoachlib.i18n import _

import os

class PSPSynchronizer(Synchronizer):
    attributeNames = ['completionDate']
    dirtyIndex = 0

    @classmethod
    def isReady(klass, settings):
        return (os.path.exists(os.path.join(settings.get('file', 'psppath'),
                                            'psp',
                                            'game150', # FIXME: hybrid firmware only
                                            '__SCE__TaskCoach')),
                _('Your PSP does not seem to be mounted/plugged in.'))

    def beforeSynchronization(self):
        path = os.path.join(self.settings.get('file', 'psppath'),
                            'psp',
                            'game150',
                            '__SCE__TaskCoach',
                            'tasks')

        self.__remoteTasks = []
        if os.path.exists(path):
            for line in file(path, 'rb'):
                data = line.rstrip('\n').split(' ')
                self.__remoteTasks.append({'dirty': int(data[0]),
                                           'id': data[1],
                                           'startDate': data[2],
                                           'dueDate': data[3],
                                           'completionDate': data[4],
                                           'subject': ' '.join(data[5:])})

    def afterSynchronization(self):
        path = os.path.join(self.settings.get('file', 'psppath'),
                            'psp',
                            'game150',
                            '__SCE__TaskCoach',
                            'tasks')

        fp = file(path, 'wb')
        try:
            for task in self.__remoteTasks:
                fp.write('%d %s %s %s %s ' % (int(task['dirty']),
                                              task['id'],
                                              task['startDate'],
                                              task['dueDate'],
                                              task['completionDate']))
                fp.write(task['subject'] + '\n')
        finally:
            fp.close()

    def getRemoteChanged(self):
        return [task for task in self.__remoteTasks if task['dirty']]

    def remoteTaskSynchronized(self, taskId):
        for task in self.__remoteTasks:
            if task['id'] == taskId:
                task['dirty'] = False
                break
        else:
            raise ValueError, 'No such remote task: %s' % taskId

    def getRemoteTask(self, taskId):
        for task in self.__remoteTasks:
            if task['id'] == taskId:
                return task
        return None

    def addRemoteTask(self, task):
        task['dirty'] = False
        self.__remoteTasks.append(task)

    def updateRemoteTask(self, task):
        for tsk in self.__remoteTasks:
            if tsk['id'] == task['id']:
                tsk.update(task)
                break
        else:
            raise ValueError, 'No such task: %s' % task['id']
