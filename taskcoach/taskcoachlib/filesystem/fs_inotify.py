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

import os, threading, time

try:
    import inotifyx
except ImportError:
    from fs_poller import *
else:
    class FilesystemNotifier(threading.Thread):
        def __init__(self):
            super(FilesystemNotifier, self).__init__()

            self.lock = threading.RLock()
            self.filename = None
            self.name = None
            self.path = None
            self.fd = inotifyx.init()
            self.wd = None
            self.cancelled = False

            self.setDaemon(True)
            self.start()

        def run(self):
            try:
                while not self.cancelled:
                    events = inotifyx.get_events(self.fd, 0)
                    self.lock.acquire()
                    try:
                        for event in events:
                            if event.name == self.filename:
                                self.onFileChanged()
                    finally:
                        self.lock.release()
                    time.sleep(1)
            except TypeError:
                # Interpreter termination (we're daemon)
                pass

        def setFilename(self, filename):
            self.lock.acquire()
            try:
                filename = os.path.normpath(os.path.abspath(filename))
                if self.wd is not None:
                    inotifyx.rm_watch(self.fd, self.wd)
                    self.wd = None
                self.filename = filename
                if filename:
                    self.path, self.name = os.path.split(filename)
                    self.wd = inotifyx.add_watch(self.fd, self.path,
                                                 inotifyx.IN_MOVED_TO|inotifyx.IN_MODIFY)
            finally:
                self.lock.release()

        def stop(self):
            self.cancelled = True
            self.join()

            if self.fd is not None:
                os.close(self.fd)
                self.fd = None

        def onFileChanged(self):
            raise NotImplementedError

        def saved(self):
            pass
