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

import os, select, threading

from ctypes import *

_libSM = CDLL('libSM.so.6')
_libICE = CDLL('libICE.so.6')

#==============================================================================
# ICE stuff...

Bool   = c_int
Status = c_int

class _IceConn(Structure):
    pass

IceConn = POINTER(_IceConn)

IceWatchProc = CFUNCTYPE(None, IceConn, c_void_p, Bool, POINTER(c_void_p))

IceInitThreads           = CFUNCTYPE(Status)(('IceInitThreads', _libICE))
IceAddConnectionWatch    = CFUNCTYPE(Status, IceWatchProc, c_void_p)(('IceAddConnectionWatch', _libICE))
IceRemoveConnectionWatch = CFUNCTYPE(None, IceWatchProc, c_void_p)(('IceRemoveConnectionWatch', _libICE))
IceConnectionNumber      = CFUNCTYPE(c_int, IceConn)(('IceConnectionNumber', _libICE))
IceProcessMessages       = CFUNCTYPE(c_int, IceConn, c_void_p, c_void_p)(('IceProcessMessages', _libICE))

#==============================================================================
# Constants

# Callback masks

SmcSaveYourselfProcMask      = (1 << 0)
SmcDieProcMask               = (1 << 1)
SmcSaveCompleteProcMask      = (1 << 2)
SmcShutdownCancelledProcMask = (1 << 3)

# Status

SmcClosedNow                 = 0
SmcClosedASAP                = 1
SmcConnectionInUse           = 2

# Interaction types

SmInteractStyleNone          = 0
SmInteractStyleErrors        = 1
SmInteractStyleAny           = 2

# Save types

SmSaveGlobal                 = 0
SmSaveLocal                  = 1
SmSaveBoth                   = 2

#==============================================================================
# Types and structures

class _SmcConn(Structure):
    pass

SmcConn = POINTER(_SmcConn)

SmcSaveYourselfProc      = CFUNCTYPE(None, SmcConn, c_void_p, c_int, Bool, c_int, Bool)
SmcDieProc               = CFUNCTYPE(None, SmcConn, c_void_p)
SmcSaveCompleteProc      = CFUNCTYPE(None, SmcConn, c_void_p)
SmcShutdownCancelledProc = CFUNCTYPE(None, SmcConn, c_void_p)

class SmcSaveYourselfCallback(Structure):
    _fields_ = [('callback', SmcSaveYourselfProc),
                ('client_data', c_void_p)]

class SmcDieCallback(Structure):
    _fields_ = [('callback', SmcDieProc),
                ('client_data', c_void_p)]

class SmcSaveCompleteCallback(Structure):
    _fields_ = [('callback', SmcSaveCompleteProc),
                ('client_data', c_void_p)]

class SmcShutdownCancelledCallback(Structure):
    _fields_ = [('callback', SmcShutdownCancelledProc),
                ('client_data', c_void_p)]

class SmcCallbacks(Structure):
    _fields_ = [('save_yourself', SmcSaveYourselfCallback),
                ('die', SmcDieCallback),
                ('save_complete', SmcSaveCompleteCallback),
                ('shutdown_cancelled', SmcShutdownCancelledCallback)]

#==============================================================================
# Functions

SmcOpenConnection = CFUNCTYPE(SmcConn,
                              c_char_p,
                              c_void_p,
                              c_int,
                              c_int,
                              c_ulong,
                              POINTER(SmcCallbacks),
                              c_char_p,
                              POINTER(c_char_p),
                              c_int,
                              c_char_p)(('SmcOpenConnection', _libSM))

SmcCloseConnection = CFUNCTYPE(c_int,
                               SmcConn,
                               c_int,
                               POINTER(c_char_p))(('SmcCloseConnection', _libSM))

SmcModifyCallbacks = CFUNCTYPE(None,
                               SmcConn,
                               c_ulong,
                               POINTER(SmcCallbacks))(('SmcModifyCallbacks', _libSM))

SmcSaveYourselfDone = CFUNCTYPE(None,
                                SmcConn,
                                Bool)(('SmcSaveYourselfDone', _libSM))

SmcProtocolVersion = CFUNCTYPE(c_int,
                               SmcConn)(('SmcProtocolVersion', _libSM))

SmcProtocolRevision = CFUNCTYPE(c_int,
                                SmcConn)(('SmcProtocolRevision', _libSM))

SmcVendor = CFUNCTYPE(c_char_p,
                      SmcConn)(('SmcVendor', _libSM))

SmcRelease = CFUNCTYPE(c_char_p,
                       SmcConn)(('SmcRelease', _libSM))

#==============================================================================
# Higher-level stuff

class ICELoop(threading.Thread):
    """
    This class manages ICE connections tracking and select()ing them
    before calling IceProcessMessages.
    """
    def __init__(self):
        self.connections = dict()
        self.cancelled = False

        self.watchProc = IceWatchProc(self._onWatch)

        IceAddConnectionWatch(self.watchProc, None)

        super(ICELoop, self).__init__()

        self.start()

    def stop(self):
        """
        Stop the main loop. Don't forget to join() this afterwards.
        """

        IceRemoveConnectionWatch(self.watchProc, None)
        self.cancelled = True

    def _onWatch(self, conn, client_data, opening, watchdata):
        if opening:
            self.connections[IceConnectionNumber(conn)] = conn
        else:
            del self.connections[IceConnectionNumber(conn)]

    def run(self):
        class DummyDescriptor(object):
            def __init__(self, fd):
                self.fd = fd

            def fileno(self):
                return self.fd

        while not self.cancelled:
            fds = [DummyDescriptor(fd) for fd in self.connections.keys()]

            ready, _, _ = select.select(fds, [], [], 1.0)
            for fd in ready:
                if fd.fileno() in self.connections:
                    IceProcessMessages(self.connections[fd.fileno()], None, None)


class SessionMonitor(ICELoop):
    """
    Higher-level class to monitor session management event. Subclass
    this and overload the saveYourself, die, saveComplete and
    shutdownCancelled methods to do actual work.
    """
    def __init__(self):
        super(SessionMonitor, self).__init__()

        self.callbacks = SmcCallbacks(SmcSaveYourselfCallback(SmcSaveYourselfProc(self._saveYourself), None),
                                      SmcDieCallback(SmcDieProc(self._die), None),
                                      SmcSaveCompleteCallback(SmcSaveCompleteProc(self._saveComplete), None),
                                      SmcShutdownCancelledCallback(SmcShutdownCancelledProc(self._shutdownCancelled), None))

        id_ret = c_char_p()

        try:
            # Some distros seem to not define this env variable. Strange.
            os.environ['SESSION_MANAGER']
        except KeyError:
            self.conn = None
        else:
            self.conn = SmcOpenConnection(os.environ['SESSION_MANAGER'],
                                          None,
                                          1, 0,
                                          SmcSaveYourselfProcMask|SmcDieProcMask|SmcSaveCompleteProcMask|SmcShutdownCancelledProcMask,
                                          byref(self.callbacks),
                                          None,
                                          byref(id_ret),
                                          0,
                                          None)

            self.clientID = id_ret.value

    def stop(self):
        super(SessionMonitor, self).stop()
        self.join()
        if self.conn is not None:
            SmcCloseConnection(self.conn, 0, None)

    def saveYourselfDone(self, status=True):
        """
        Call this after a save yourself.
        """
        SmcSaveYourselfDone(self.conn, int(status))

    def _saveYourself(self, conn, client_data, save_type, shutdown, interact_style, fast):
        self.saveYourself(save_type, shutdown, interact_style, fast)

    def saveYourself(self, save_type, shutdown, interact_style, fast):
        """
        Save yourself request.

        @param save_type: Type of save; see the SmSave* constants.
        @param shutdown: True if a shutdown is in progress.
        @param interact_style: Types of user interactions allowed. See the
            smInteractStyle* constants.
        @param fast: Dunno.
        """
        raise NotImplementedError

    def _die(self, conn, client_data):
        self.die()

    def die(self):
        """
        Die request. A competent session manager should have sent a save
        yourself request before this.
        """
        raise NotImplementedError

    def _saveComplete(self, conn, client_data):
        self.saveComplete()

    def saveComplete(self):
        """
        A save has completed.
        """
        raise NotImplementedError

    def _shutdownCancelled(self, conn, client_data):
        self.shutdownCancelled()

    def shutdownCancelled(self):
        """
        Shutdown cancelled by the user.
        """
        raise NotImplementedError

    # Properties

    @property
    def version(self):
        return SmcProtocolVersion(self.conn)

    @property
    def revision(self):
        return SmcProtocolRevision(self.conn)

    @property
    def vendor(self):
        return SmcVendor(self.conn) # Leak

    @property
    def release(self):
        return SmcRelease(self.conn) # Leak

#==============================================================================
# Testing

if __name__ == '__main__':
    class TestMonitor(SessionMonitor):
        def __init__(self):
            super(TestMonitor, self).__init__()

            print 'Version:', self.version
            print 'Revision:', self.revision
            print 'Vendor:', self.vendor
            print 'Release:', self.release

            print 'Client ID:', self.clientID

        def log(self, msg):
            file('session.txt', 'a+').write('==== %s\n' % msg)
            print msg

        def saveYourself(self, save_type, shutdown, interact_style, fast):
            self.log('Save yourself %d %d %d %d' % (save_type, shutdown, interact_style, fast))
            self.saveYourselfDone(True)

        def die(self):
            self.log('Die')

        def saveComplete(self):
            self.log('Save complete')

        def shutdownCancelled(self):
            self.log('Shutdown cancelled')

    monitor = TestMonitor()
    raw_input('')
    monitor.stop()
    monitor.join()