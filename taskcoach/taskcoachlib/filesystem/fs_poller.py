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

import os, time, threading


class FilesystemNotifier(threading.Thread):
    def __init__(self):
        super(FilesystemNotifier, self).__init__()

        self.filename = None
        self.stamp = None
        self.lock = threading.RLock()
        self.cancelled = False

        self.setDaemon(True)
        self.start()

    def setFilename(self, filename):
        self.lock.acquire()
        try:
            self.filename = filename
            if filename and os.path.exists(filename):
                self.stamp = os.stat(filename).st_mtime
            else:
                self.stamp = None
        finally:
            self.lock.release()

    def run(self):
        while True:
            self.lock.acquire()
            try:
                if self.filename and os.path.exists(self.filename):
                    stamp = os.stat(self.filename).st_mtime
                    if stamp > self.stamp:
                        self.stamp = stamp
                        self.onFileChanged()
            finally:
                self.lock.release()

            for i in xrange(10):
                if self.cancelled:
                    return
                time.sleep(0.1) # XXXFIXME: increase timeout

    def stop(self):
        self.cancelled = True
        self.join()

    def onFileChanged(self):
        raise NotImplementedError

    def saved(self):
        self.lock.acquire()
        try:
            if self.filename and os.path.exists(self.filename):
                self.stamp = os.stat(self.filename).st_mtime
            else:
                self.stamp = None
        finally:
            self.lock.release()
