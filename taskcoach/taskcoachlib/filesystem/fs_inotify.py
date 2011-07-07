'''
Task Coach - Your friendly task manager
Copyright (C) 2011 Task Coach developers <developers@taskcoach.org>

Task Coach is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Task Coach is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import os, threading

try:
    import pyinotify
except ImportError:
    from fs_poller import *
else:
    class _EventHandler(pyinotify.ProcessEvent):
        def __init__(self, callback):
            self.callback = callback
            super(_EventHandler, self).__init__()

        def process_IN_MODIFY(self, event):
            self.callback(event)

        def process_IN_MOVED_TO(self, event):
            self.callback(event)

    class FilesystemNotifier(object):
        def __init__(self):
            self.lock = threading.RLock()
            self.filename = None
            self.name = None
            self.path = None
            self.wd = None

            self.wm = pyinotify.WatchManager()
            self.eh = _EventHandler(self._onFileChanged)
            self.notifier = pyinotify.ThreadedNotifier(self.wm, self.eh)
            self.notifier.start()

        def setFilename(self, filename):
            self.lock.acquire()
            try:
                if self.wd is not None:
                    self.wm.rm_watch(self.wd)
                    self.wd = None
                self.filename = filename
                if filename:
                    self.path, self.name = os.path.split(filename)
                    self.wm.add_watch(self.path, pyinotify.ALL_EVENTS)
                    self.wd = self.wm.get_wd(self.path)
                else:
                    self.path = None
                    self.name = None
            finally:
                self.lock.release()

        def stop(self):
            self.lock.acquire()
            try:
                self.wm.close()
                self.notifier.stop()
            finally:
                self.lock.release()

        def _onFileChanged(self, event):
            self.lock.acquire()
            try:
                if event.pathname == self.filename:
                    self.onFileChanged()
            finally:
                self.lock.release()

        def onFileChanged(self):
            raise NotImplementedError

        def saved(self):
            pass
