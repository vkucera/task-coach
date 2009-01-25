'''
Task Coach - Your friendly task manager
Copyright (C) 2008 Jerome Laheurte <fraca7@free.fr>

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

from taskcoachlib.gui.threads import synchronized, DeferredCallMixin
from taskcoachlib.patterns.network import Acceptor
from taskcoachlib.i18n import _

import wx, asynchat, threading, asyncore, struct, StringIO

# Default port is 8001.
#
# Integers are sent as 32 bits signed, network byte order.
# Strings are sent as their length (as integer), then data (UTF-8 encoded).
#
# 1) The protocol version is negotiated: Task Coach sends its higher
# supported version (currently 1). If the iPhone answers 0, it doesn't
# support it, so decrement and try again. If it answers 1, go to 2.
#
# 2) The iPhone sends the password. No challenge or encryption
# supported yet. Task Coach answers either 0 (wrong password) and
# closes the connection, or 1 (authentication OK), then go to 3.
#
# 3) The iPhone sends the task file GUID it's associated with, or an
# empty string if it has never been synced before. If the GUID doesn't
# match the currently open file, the user is prompted for the kind of
# synchronization he wants (full from Task Coach or full from device).
#
# 4) TaskCoach sends the synchronization type to the iPhone. The
# actual synchronization can begin now.
#
# Types are
#   0 two ways
#   1 full from Task Coach
#   2 full from iPhone
#
# Two-way is actually implemented as: get changes from iPhone, then
# full from Task Coach. This allows us to avoid keeping track of
# changes on the TaskCoach side; we're not using the change tracking
# mechanism because it would interfere with SyncML. Cons: no conflict
# resolution, the device always wins. This should not be a problem in
# this use case.


class IPhoneAcceptor(Acceptor):
    def __init__(self, window, settings):
        def factory(fp, addr):
            print 'New connection from', addr

            password = settings.get('iphone', 'password')

            if password:
                return IPhoneHandler(window, settings.get('iphone', 'password'), fp)

            wx.MessageBox(_('An iPhone or iPod Touch tried to connect to Task Coach,\n') + \
                          _('but no password is set. Please set a password in the\n') + \
                          _('iPhone section of the configuration and try again.'),
                          _('Error'), wx.OK)

        Acceptor.__init__(self, factory,
                          settings.get('iphone', 'host'),
                          settings.getint('iphone', 'port'))

        thread = threading.Thread(target=asyncore.loop)
        thread.setDaemon(True)
        thread.start()


class IPhoneHandler(asynchat.async_chat):
    def __init__(self, window, password, fp):
        asynchat.async_chat.__init__(self, fp)

        self.window = window
        self.password = password
        self.data = StringIO.StringIO()
        self.state = InitialState(self)

    def collect_incoming_data(self, data):
        self.data.write(data)

    def found_terminator(self):
        data = self.data.getvalue()
        self.data = StringIO.StringIO()
        self.state.handleData(self, data)

    def handle_close(self):
        print 'Closed.'
        self.close()

    # XXXTODO: handle_error


class BaseState(object):
    def __init__(self, *args, **kwargs):
        self.init(*args, **kwargs)

    def setState(self, state, *args, **kwargs):
        self.__class__ = state
        self.init(*args, **kwargs)

    def init(self):
        pass

class InitialState(BaseState):
    def init(self, disp):
        print 'New connection.'

        disp.set_terminator(4)
        disp.push(struct.pack('!i', 1)) # Protocol version

    def handleData(self, disp, data):
        response, = struct.unpack('!i', data)

        if response:
            print 'Protocol OK.'
            self.setState(PasswordState, disp)
        else:
            print 'Protocol KO.'
            disp.close()
            # XXXTODO: notify user


class PasswordState(BaseState):
    def init(self, disp):
        self.length = None
        disp.set_terminator(4)

    def handleData(self, disp, data):
        if self.length is None:
            self.length, = struct.unpack('!i', data)
            print 'Password length:', self.length
            disp.set_terminator(self.length)
        else:
            print 'Password:', data
            if data.decode('UTF-8') == disp.password:
                disp.push(struct.pack('!i', 1))
                self.setState(GUIDState, disp)
            else:
                disp.push(struct.pack('!i', 0))
                # The other end will close.


class GUIDState(BaseState):
    def init(self, disp):
        self.length = None
        disp.set_terminator(4)

    def handleData(self, disp, data):
        if self.length is None:
            self.length, = struct.unpack('!i', data)
            if self.length:
                disp.set_terminator(self.length)
            else:
                print 'No GUID.'
                self.onSyncType(disp, disp.window.getIPhoneSyncType(None))
        else:
            print 'GUID:', data
            self.onSyncType(disp, disp.window.getIPhoneSyncType(data))

    def onSyncType(self, disp, type_):
        print 'Synchronization type:', type_
        disp.push(struct.pack('!i', type_))

        if type_ == 3:
            disp.close_when_done()
        else:
            disp.close_when_done() # XXXTODO
