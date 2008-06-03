
from taskcoachlib.syncml.tasksource import TaskSource
from taskcoachlib.syncml.notesource import NoteSource

from taskcoachlib.i18n import _

from _pysyncml import *

class Synchronizer(object):
    def __init__(self, mode, verbose, clientName, reportCallback,
                 taskFile, url, username, password,
                 taskdbname, synctasks,
                 notedbname, syncnotes,
                 *args, **kwargs):
        super(Synchronizer, self).__init__(*args, **kwargs)

        clientName = clientName.encode('UTF-8')

        self.verbose = verbose
        self.reportCallback = reportCallback
        self.taskFile = taskFile

        self.dmt = DMTClientConfig(clientName)
        if not (self.dmt.read() and self.dmt.deviceConfig.devID == clientName):
            self.dmt.setClientDefaults()

        ac = self.dmt.accessConfig
        ac.username = username.encode('UTF-8') # Hum...
        ac.password = password.encode('UTF-8')

        ac.useProxy = 0
        ac.syncURL = url.encode('UTF-8')
        self.dmt.accessConfig = ac

        dc = self.dmt.deviceConfig
        dc.devID = clientName
        self.dmt.deviceConfig = dc

        # Tasks source configuration

        self.sources = []

        if synctasks:
            try:
                cfg = self.dmt.getSyncSourceConfig('TaskCoach.Tasks')
            except ValueError:
                cfg = SyncSourceConfig()

            cfg.name = '%s.Tasks' % clientName
            cfg.URI = taskdbname.encode('UTF-8')
            cfg.syncModes = 'two-way'
            cfg.supportedTypes = 'text/vcard:3.0'
            cfg.version = '1.0'

            self.dmt.setSyncSourceConfig(cfg)

            self.sources.append(TaskSource(taskFile.tasks(),
                                           taskFile.categories(),
                                           '%s.Tasks' % clientName, cfg))

        if syncnotes:
            try:
                cfg = self.dmt.getSyncSourceConfig('%s.Notes' % clientName)
            except ValueError:
                cfg = SyncSourceConfig()

            cfg.name = '%s.Notes' % clientName
            cfg.URI = notedbname.encode('UTF-8')
            cfg.syncModes = 'two-way'
            cfg.supportedTypes = 'text/plain'
            cfg.version = '1.0'

            self.dmt.setSyncSourceConfig(cfg)

            self.sources.append(NoteSource(taskFile.notes(),
                                           '%s.Notes' % clientName, cfg))

        for source in self.sources:
            source.preferredSyncMode = globals()[mode] # Hum

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
