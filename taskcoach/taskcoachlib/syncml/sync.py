
from taskcoachlib.syncml.tasksource import TaskSource
from taskcoachlib.syncml.notesource import NoteSource

from taskcoachlib.i18n import _

from _pysyncml import *

class Synchronizer(object):
    def __init__(self, mode, verbose, clientName, reportCallback,
                 conflictCallback, taskFile, url, username, password,
                 taskdbname, synctasks,
                 notedbname, syncnotes,
                 *args, **kwargs):
        super(Synchronizer, self).__init__(*args, **kwargs)

        self.clientName = clientName.encode('UTF-8')
        self.verbose = verbose
        self.reportCallback = reportCallback
        self.conflictCallback = conflictCallback
        self.taskFile = taskFile

        self.username = username.encode('UTF-8') # Hum...
        self.password = password.encode('UTF-8')
        self.url = url.encode('UTF-8')

        self.synctasks = synctasks
        self.syncnotes = syncnotes
        self.taskdbname = taskdbname.encode('UTF-8')
        self.notedbname = notedbname.encode('UTF-8')

        self.mode = mode

    def init(self):
        self.dmt = DMTClientConfig(self.clientName)
        if not (self.dmt.read() and \
                self.dmt.deviceConfig.devID == self.clientName):
            self.dmt.setClientDefaults()

        ac = self.dmt.accessConfig
        ac.username = self.username
        ac.password = self.password

        ac.useProxy = 0
        ac.syncURL = self.url
        self.dmt.accessConfig = ac

        dc = self.dmt.deviceConfig
        dc.devID = self.clientName
        self.dmt.deviceConfig = dc

        # Tasks source configuration

        self.sources = []

        if self.synctasks:
            try:
                cfg = self.dmt.getSyncSourceConfig('%s.Tasks' % self.clientName)
            except ValueError:
                cfg = SyncSourceConfig()

            cfg.name = '%s.Tasks' % self.clientName
            cfg.URI = self.taskdbname
            cfg.syncModes = 'two-way'
            cfg.supportedTypes = 'text/vcard:3.0'
            cfg.version = '1.0'

            self.dmt.setSyncSourceConfig(cfg)

            self.sources.append(TaskSource(self,
                                           self.taskFile.tasks(),
                                           self.taskFile.categories(),
                                           '%s.Tasks' % self.clientName, cfg))

        if self.syncnotes:
            try:
                cfg = self.dmt.getSyncSourceConfig('%s.Notes' % self.clientName)
            except ValueError:
                cfg = SyncSourceConfig()

            cfg.name = '%s.Notes' % self.clientName
            cfg.URI = self.notedbname
            cfg.syncModes = 'two-way'
            cfg.supportedTypes = 'text/plain'
            cfg.version = '1.0'

            self.dmt.setSyncSourceConfig(cfg)

            self.sources.append(NoteSource(self,
                                           self.taskFile.notes(),
                                           '%s.Notes' % self.clientName, cfg))

        for source in self.sources:
            source.preferredSyncMode = globals()[self.mode] # Hum

    def error(self, code, msg):
        self.reportCallback(_('An error occurred in the synchronization.\nError code: %d; message: %s') \
                            % (code, msg))

    def synchronize(self):
        self.taskFile.beginSync()
        try:
            # Actually  make  two  synchronizations. Funambol  servers
            # seem  to do  conflict resolution  without  notifying the
            # client. Here, we make a first sync "pretending" no local
            # items  are modified,  so that  the server  sends  us its
            # modifications  and new  items.  On the  second pass,  we
            # ignore  remote modifications  and new  items  but upload
            # local modifications. The last anchors of each source are
            # finally set to their value after the first sync, so that
            # items added/deleted/modified between  the two are synced
            # on the next synchronization...

            # See BaseSource for the state mechanism itself. This only
            # holds for two-way syncs.

            self.init()

            client = SyncClient()
            client.sync(self.dmt, self.sources)

            code = client.report.lastErrorCode

            if code:
                self.error(code, client.report.lastErrorMsg)

                # TODO: undo local modifications ?
                return False

            self.dmt.save()

            states = [source.__getstate__() for source in self.sources]
            self.init()
            for idx, state in enumerate(states):
                self.sources[idx].__setstate__(state)

            # Some sources may not need a second sync.
            self.sources = [source for source in self.sources if source.state != source.STATE_NORMAL]

            if self.sources:
                client = SyncClient()
                client.sync(self.dmt, self.sources)

                code = client.report.lastErrorCode

                if code:
                    self.error(code, client.report.lastErrorMsg)

                    # TODO: undo local modifications ?
                    return False

                self.dmt.save()
        finally:
            self.taskFile.endSync()

        return True

    def resolveNoteConflict(self, flags, local, remote):
        return self.conflictCallback.resolveNoteConflict(flags, local, remote)

    def resolveTaskConflict(self, flags, local, remote):
        return self.conflictCallback.resolveTaskConflict(flags, local, remote)
