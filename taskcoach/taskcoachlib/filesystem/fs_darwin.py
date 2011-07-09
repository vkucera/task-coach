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

from ctypes import *
import os, tempfile, threading

_libc = CDLL('libc.dylib')

# Constants

O_EVTONLY       = 0x8000

EVFILT_VNODE    = -4

EV_ADD          = 0x0001
EV_ENABLE       = 0x0004
EV_ONESHOT      = 0x0010

NOTE_DELETE     = 0x00000001
NOTE_EXTEND     = 0x00000004
NOTE_WRITE      = 0x00000002
NOTE_ATTRIB     = 0x00000008
NOTE_LINK       = 0x00000010
NOTE_RENAME     = 0x00000020
NOTE_REVOKE     = 0x00000040

# Structures

class keventstruct(Structure):
    _fields_ = [('ident', c_ulong),
                ('filter', c_int16),
                ('flags', c_uint16),
                ('fflags', c_uint32),
                ('data', c_long),
                ('udata', c_void_p)]

# Functions

opendir  = CFUNCTYPE(c_void_p, c_char_p)(('opendir', _libc))
closedir = CFUNCTYPE(c_int, c_void_p)(('closedir', _libc))
open_    = CFUNCTYPE(c_int, c_char_p, c_int)(('open', _libc))
close    = CFUNCTYPE(c_int, c_int)(('close', _libc))

# dirfd seems to be defined as a macro. Let's assume the fd field is
# the first one in the structure.

def dirfd(p):
    return cast(p, POINTER(c_int)).contents.value

kqueue = CFUNCTYPE(c_int)(('kqueue', _libc))
kevent = CFUNCTYPE(c_int, c_int, POINTER(keventstruct), c_int, POINTER(keventstruct), c_int, c_void_p)(('kevent', _libc))

# Macros

def EV_SET(kev, ident, filter_, flags, fflags, data, udata):
    kev.ident = ident
    kev.filter = filter_
    kev.flags = flags
    kev.fflags = fflags
    kev.data = data
    kev.udata = udata

# Higher-evel API

class FileMonitor(object):
    def __init__(self, filename, callback):
        super(FileMonitor, self).__init__()

        self.callback = callback

        if isinstance(filename, unicode):
            filename = filename.encode('UTF-8') # Not sure...

        self.filename = filename
        path, name = os.path.split(filename)

        self.fd = None

        if os.path.exists(filename):
            self.fd = open_(filename, O_EVTONLY)
            if self.fd < 0:
                raise OSError('Could not open "%s"' % filename)
            self.state = 2
        else:
            self.state = 1

        self.dir = opendir(path)
        if self.dir is None:
            close(self.fd)
            self.fd = None
            raise OSError('Could not open "%s"' % path)
        self.dirfd = dirfd(self.dir)

        self.cancelled = False

    def loop(self):
        kq = kqueue()
        try:
            event = keventstruct()
            changes = (keventstruct * 2)()

            EV_SET(changes[0], self.dirfd, EVFILT_VNODE, EV_ADD | EV_ENABLE | EV_ONESHOT,
                   NOTE_WRITE | NOTE_EXTEND, 0, 0)
            if self.fd is not None:
                EV_SET(changes[1], self.fd, EVFILT_VNODE, EV_ADD | EV_ENABLE | EV_ONESHOT,
                       NOTE_WRITE | NOTE_EXTEND | NOTE_DELETE | NOTE_ATTRIB | \
                       NOTE_LINK | NOTE_RENAME | NOTE_REVOKE, 0, 0)

            while True:
                if kevent(kq, changes, self.state, byref(event), 1, None) > 0:
                    if self.cancelled:
                        break
                    if self.state == 2:
                        if event.ident == self.fd and event.fflags & NOTE_DELETE:
                            # File deleted.
                            close(self.fd)
                            self.fd = None
                            self.state = 1
                        elif event.ident == self.fd:
                            self.onFileChanged()
                    elif self.state == 1:
                        # The event can only concern the directory anyway.
                        if os.path.exists(self.filename):
                            # File was re-created
                            self.fd = open_(self.filename, O_EVTONLY)
                            if self.fd < 0:
                                raise OSError('Could not open "%s"' % self.filename)
                            EV_SET(changes[1], self.fd, EVFILT_VNODE, EV_ADD | EV_ENABLE | EV_ONESHOT,
                                   NOTE_WRITE | NOTE_EXTEND | NOTE_DELETE | NOTE_ATTRIB | \
                                   NOTE_LINK | NOTE_RENAME | NOTE_REVOKE, 0, 0)
                            self.state = 2
                            self.onFileChanged()
        finally:
            close(kq)

    def stop(self):
        self.cancelled = True
        # To break the kevent() call
        tempfile.TemporaryFile(dir=os.path.split(self.filename)[0])

    def close(self):
        if self.fd is not None:
            close(self.fd)
            self.fd = None
        if self.dir is not None:
            closedir(self.dir)
            self.dir = None

    def __del__(self):
        self.close()

    def onFileChanged(self):
        self.callback(self.filename)


class FilesystemNotifier(object):
    def __init__(self):
        super(FilesystemNotifier, self).__init__()

        self.filename = None
        self.path = None
        self.name = None
        self.monitor = None
        self.thread = None
        self.lock = threading.Lock()

    def setFilename(self, filename):
        self.lock.acquire()
        try:
            if self.monitor is not None:
                self.monitor.stop()
                self.thread.join()
                self.monitor.close()
                self.monitor = None
                self.thread = None
            if filename:
                self.filename = os.path.normpath(os.path.abspath(filename))
                self.path, self.name = os.path.split(self.filename)
                self.monitor = FileMonitor(self.filename, self._onFileChanged)
                self.thread = threading.Thread(target=self._run)
                self.thread.setDaemon(True)
                self.thread.start()
            else:
                self.filename = None
                self.path = None
                self.name = None
        finally:
            self.lock.release()

    def stop(self):
        self.lock.acquire()
        try:
            if self.monitor is not None:
                self.monitor.stop()
                self.thread.join()
                self.monitor.close()
                self.monitor = None
                self.thread = None
        finally:
            self.lock.release()

    def _onFileChanged(self, filename):
        self.onFileChanged()

    def onFileChanged(self):
        raise NotImplementedError

    def saved(self):
        pass

    def _run(self):
        self.monitor.loop()
