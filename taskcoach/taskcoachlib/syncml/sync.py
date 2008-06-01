
from taskcoachlib.syncml.tasksource import TaskSource
from taskcoachlib.i18n import _

from _pysyncml import *

class Synchronizer(object):
    def __init__(self, verbose, reportCallback, taskFile, url, username, password,
                 taskdbname, synctasks, *args, **kwargs):
        super(Synchronizer, self).__init__(*args, **kwargs)

        self.verbose = verbose
        self.reportCallback = reportCallback
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

            self.sources.append(TaskSource(taskFile.tasks(),
                                           taskFile.categories(),
                                           'TaskCoach.Tasks', cfg))

    def synchronize(self):
        self.taskFile.beginSync()
        try:
            client = SyncClient()
            client.sync(self.dmt, self.sources)
        finally:
            self.taskFile.endSync()

        code = client.report.getLastErrorCode()
        if code:
            self.reportCallback(_('An error occurred in the synchronization.\nError code: %d; message: %s') % (code, client.report.getLastErrorMsg()))
            return False

        if self.verbose:
            self.reportCallback(_('Synchronization over. Report:\n\n') + str(client.report))

        self.dmt.save()
        return True
