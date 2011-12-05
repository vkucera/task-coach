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


import os, atexit


class NotifierBase(object):
    def __init__(self):
        super(NotifierBase, self).__init__()

        self.filename = None
        self.path = None
        self.name = None
        self.stamp = None
        atexit.register(self._stop)

    def _stop(self):
        self.stop()

    def stop(self):
        pass # Should be overloaded if needed

    def _check(self, filename):
        return self.stamp is None or \
               (filename and \
                os.path.exists(filename) and \
                os.stat(filename).st_mtime > self.stamp)

    def setFilename(self, filename):
        self.filename = filename
        self.stamp = None
        if filename:
            self.path, self.name = os.path.split(filename)
            if os.path.exists(filename):
                self.stamp = os.stat(filename).st_mtime
        else:
            self.path, self.name = None, None

    def saved(self):
        self.lock.acquire()
        try:
            if self.filename and os.path.exists(self.filename):
                self.stamp = os.stat(self.filename).st_mtime
            else:
                self.stamp = None
        finally:
            self.lock.release()
