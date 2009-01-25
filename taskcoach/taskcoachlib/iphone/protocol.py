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
from taskcoachlib.gui.dialog.iphone import IPhoneSyncDialog
from taskcoachlib.patterns.network import Acceptor
from taskcoachlib.domain.date import Date

from taskcoachlib.i18n import _

import wx, asynchat, threading, asyncore, struct, StringIO, random, time, sha

# Default port is 8001.
#
# Integers are sent as 32 bits signed, network byte order.
# Strings are sent as their length (as integer), then data (UTF-8 encoded).
#
# 1) The protocol version is negotiated: Task Coach sends its higher
# supported version (currently 1). If the iPhone answers 0, it doesn't
# support it, so decrement and try again. If it answers 1, go to 2.
#
# 2) SHA1 challenge: Task Coach sends 512 random bytes to the
# device. The device appends the user provided password as UTF-8 data
# and sends back the SHA1 hash of the result. Task Coach checks the
# hash and sends 0 (wrong hash) or 1 (authenticated), and then go to 3.
#
# 3) The iPhone sends its device name.
#
# 4) The iPhone sends the task file GUID it's associated with, or an
# empty string if it has never been synced before. If the GUID doesn't
# match the currently open file, the user is prompted for the kind of
# synchronization he wants (full from Task Coach or full from device).
#
# 5) TaskCoach sends the synchronization type to the iPhone. The
# actual synchronization can begin now.
#
# Types are
#   0 two ways
#   1 full from Task Coach
#   2 full from iPhone
#   3 user cancelled
#
# Two-way is actually implemented as: get changes from iPhone, then
# full from Task Coach. This allows us to avoid keeping track of
# changes on the TaskCoach side; we're not using the change tracking
# mechanism because it would interfere with SyncML. Cons: no conflict
# resolution, the device always wins. This should not be a problem in
# this use case.
#
# == Full from Task Coach ==
#
# In this scenario, Task Coach first sends the number of categories it
# will send, then the number of tasks. Then it sends the objects
# themselves.
#
# Categories are sent as:
#
#  1) name (string)
#  2) ID (string)
#
# Tasks are sent as:
#
#  1) title (string)
#  2) ID (string)
#  3) description (string)
#  4) start date
#  5) due date
#  6) completion date
#  7) category ID (string)
#
# All dates are string, formatted YYYY-MM-DD. An empty string means None.
# As the iPhone version does not support hierarchical categories, the following
# algorithm is used to select the task category to send:
#
# 1) List all top-level categories of the task's categories
# 2) Sort them by name
# 3) Take the first one
#
# After all categories and tasks have been sent, Task Coach sends the file
# GUID as a string.

class IPhoneAcceptor(Acceptor):
    def __init__(self, window, settings):
        def factory(fp, addr):
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

        random.seed(time.time())

    def collect_incoming_data(self, data):
        self.data.write(data)

    def found_terminator(self):
        data = self.data.getvalue()
        self.data = StringIO.StringIO()
        self.state.handleData(self, data)

    def handle_close(self):
        print 'Closed.'
        self.state.handleClose(self)
        self.close()

    def handle_error(self):
        asynchat.async_chat.handle_error(self)
        self.close()

    def pushString(self, string):
        string = string.encode('UTF-8')
        self.push(struct.pack('!i', len(string)) + string)

    def pushInteger(self, value):
        self.push(struct.pack('!i', value))

    def pushDate(self, date):
        if date == Date():
            self.pushString('')
        else:
            self.pushString('%04d-%02d-%02d' % (date.year, date.month, date.day))


class BaseState(object):
    def __init__(self, *args, **kwargs):
        self.init(*args, **kwargs)

        self.dlg = None

    def setState(self, state, *args, **kwargs):
        self.__class__ = state
        self.init(*args, **kwargs)

    def handleClose(self, disp):
        if self.dlg is not None:
            self.dlg.Finished()

    def init(self):
        pass


class InitialState(BaseState):
    def init(self, disp):
        print 'New connection.'

        disp.set_terminator(4)
        disp.pushInteger(1) # Protocol version

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
        self.hashData = ''.join([struct.pack('B', random.randint(0, 255)) for i in xrange(512)])
        disp.push(self.hashData)

        self.length = None
        disp.set_terminator(20)

    def handleData(self, disp, data):
        if data == sha.sha(self.hashData + disp.password.encode('UTF-8')).digest():
            disp.pushInteger(1)
            print 'Authentication OK'
            self.setState(DeviceNameState, disp)
        else:
            disp.pushInteger(0)


class DeviceNameState(BaseState):
    def init(self, disp):
        self.length = None
        disp.set_terminator(4)

    def handleData(self, disp, data):
        if self.length is None:
            self.length, = struct.unpack('!i', data)
            print 'Name length:', self.length
            disp.set_terminator(self.length)
        else:
            print 'Device name:', data
            self.deviceName = data.decode('UTF-8')
            self.setState(GUIDState, disp)


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

        if type_ == 0:
            pass # XXXTODO
        elif type_ == 1:
            self.dlg = IPhoneSyncDialog(self.deviceName, disp.window, wx.ID_ANY, _('iPhone/iPod'))
            self.dlg.Started()

            self.setState(FullFromDesktopState, disp)
        elif type_ == 2:
            pass # XXXTODO

        # On cancel, the other end will close the connection


class FullFromDesktopState(BaseState):
    def init(self, disp):
        # Send only top-level categories
        disp.pushInteger(len(disp.window.taskFile.categories().rootItems()))
        disp.pushInteger(len(disp.window.taskFile.tasks()))

        total = len(disp.window.taskFile.categories().rootItems()) + len(disp.window.taskFile.tasks())
        count = 0

        for category in disp.window.taskFile.categories().rootItems():
            disp.pushString(category.subject())
            disp.pushString(category.id())
            count += 1
            self.dlg.SetProgress(count, total)

        for task in disp.window.taskFile.tasks():
            def getTopCategory(t):
                s = set()
                for category in t.categories(recursive=True):
                    while category.parent():
                        category = category.parent()
                    s.add(category)
                s = list(s)
                s.sort(lambda x, y: cmp(unicode(x), unicode(y)))
                if s:
                    return s[0].id()
                return ''

            disp.pushString(task.subject())
            disp.pushString(task.id())
            disp.pushString(task.description())
            disp.pushDate(task.startDate())
            disp.pushDate(task.dueDate())
            disp.pushDate(task.completionDate())
            disp.pushString(getTopCategory(task))

            count += 1
            self.dlg.SetProgress(count, total)

        disp.pushString(disp.window.taskFile.guid())
        disp.close_when_done()
        self.dlg.Finished()
