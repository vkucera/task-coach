
from taskcoachlib.syncml.tasksource import TaskSource
from _pysyncml import *

class Synchronizer(object):
    def __init__(self, taskFile, url, username, password,
                 taskdbname, synctasks, *args, **kwargs):
        super(Synchronizer, self).__init__(*args, **kwargs)

        self.taskFile = taskFile

        self.dmt = DMTClientConfig('TaskCoach')
        if not (self.dmt.read() and self.dmt.deviceConfig.devID == 'TaskCoach'):
            self.dmt.setClientDefaults()

        ac = self.dmt.accessConfig
        ac.username = username.encode('UTF-8') # Hum...
        ac.password = password.encode('UTF-8')

        ac.useProxy = 0
        ac.syncURL = url.encode('UTF-8')
        self.dmt.accessConfig = ac

        dc = self.dmt.deviceConfig
        dc.devID = 'TaskCoach'
        self.dmt.deviceConfig = dc

        # Tasks source configuration

        self.sources = []

        if synctasks:
            try:
                cfg = self.dmt.getSyncSourceConfig('TaskCoach.Tasks')
            except ValueError:
                cfg = SyncSourceConfig()

            cfg.name = 'TaskCoach.Tasks'
            cfg.URI = taskdbname.encode('UTF-8')
            cfg.syncModes = 'two-way'
            cfg.supportedTypes = 'text/vcard:3.0'
            cfg.version = '1.0'

            self.dmt.setSyncSourceConfig(cfg)

            self.sources.append(TaskSource(taskFile.tasks(), 'TaskCoach.Tasks', cfg))

    def synchronize(self):
        client = SyncClient()
        client.sync(self.dmt, self.sources)
        self.dmt.save()
        self.taskFile.markDirty()
        print client.report # TMP
        return client.report
