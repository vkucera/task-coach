'''
Task Coach - Your friendly task manager
Copyright (C) 2008-2009 Jerome Laheurte <fraca7@free.fr>

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
from taskcoachlib.domain.date import Date, parseDate

from taskcoachlib.domain.category import Category
from taskcoachlib.domain.task import Task

from taskcoachlib.i18n import _

import wx, asynchat, threading, asyncore, struct, StringIO, random, time, sha

# Default port is 8001.
#
# Integers are sent as 32 bits signed, network byte order.
# Strings are sent as their length (as integer), then data (UTF-8
# encoded). The length is computed after encoding.
# Dates are sent as strings, formatted YYYY-MM-DD.
#
# The exact workflow for both desktop and device is documented as Dia
# diagrams, in the "Design" subdirectory of the iPhone sources.

class IPhoneAcceptor(Acceptor):
    def __init__(self, window, settings):
        def factory(fp, addr):
            password = settings.get('iphone', 'password')

            if password:
                return IPhoneHandler(window, settings.get('iphone', 'password'), fp)

            wx.MessageBox(_('''An iPhone or iPod Touch tried to connect to Task Coach,\n'''
                            '''but no password is set. Please set a password in the\n'''
                            '''iPhone section of the configuration and try again.'''),
                          _('Error'), wx.OK)

        Acceptor.__init__(self, factory, '', None)

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
        self.state.handleClose(self)
        self.close()

    def handle_error(self):
        asynchat.async_chat.handle_error(self)
        self.close()
        self.state.handleClose(self)

    def pushString(self, string):
        if string is None:
            self.pushInteger(0)
        else:
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
    def __init__(self, disp, *args, **kwargs):
        self.oldTasks = disp.window.taskFile.tasks().copy()
        self.oldCategories = disp.window.taskFile.categories().copy()

        self.dlg = None

        self.init(disp, *args, **kwargs)

    def isTaskEligible(self, task):
        """Returns True if a task should be considered when syncing with an iPhone/iPod Touch
        device. Right now, a task is eligible if

         * It's a leaf task (no children)
         * Or it has a reminder
         * Or it's overdue
         * Or it belongs to a category named 'iPhone'

         This will probably be more configurable in the future."""

        if task.isDeleted():
            return False

        if len(task.children()) == 0:
            return True

        if task.reminder() is not None:
            return True

        if task.overdue():
            return True

        for category in task.categories():
            if category.subject() == 'iPhone':
                return True

        return False

    def setState(self, state, *args, **kwargs):
        self.__class__ = state
        self.init(*args, **kwargs)

    def handleClose(self, disp):
        if self.dlg is not None:
            self.dlg.Finished()

        # Rollback
        disp.window.restoreTasks(self.oldCategories, self.oldTasks)

    def init(self, disp):
        pass


class InitialState(BaseState):
    def init(self, disp):
        self.currentProtocolVersion = 3
        disp.set_terminator(4)
        disp.pushInteger(self.currentProtocolVersion)

    def handleData(self, disp, data):
        response, = struct.unpack('!i', data)

        if response:
            disp.protocolVersion = self.currentProtocolVersion
            self.setState(PasswordState, disp)
        else:
            if self.currentProtocolVersion == 1:
                disp.close()
                disp.window.notifyIPhoneProtocolFailed()
            else:
                self.currentProtocolVersion -= 1
                disp.set_terminator(4)
                disp.pushInteger(self.currentProtocolVersion)


class PasswordState(BaseState):
    def init(self, disp):
        self.hashData = ''.join([struct.pack('B', random.randint(0, 255)) for i in xrange(512)])
        disp.push(self.hashData)

        self.length = None
        disp.set_terminator(20)

    def handleData(self, disp, data):
        if data == sha.sha(self.hashData + disp.password.encode('UTF-8')).digest():
            disp.pushInteger(1)
            self.setState(DeviceNameState, disp)
        else:
            disp.pushInteger(0)
            self.setState(PasswordState, disp)


class DeviceNameState(BaseState):
    def init(self, disp):
        self.length = None
        disp.set_terminator(4)

    def handleData(self, disp, data):
        if self.length is None:
            self.length, = struct.unpack('!i', data)
            disp.set_terminator(self.length)
        else:
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
                self.onSyncType(disp, disp.window.getIPhoneSyncType(None))
        else:
            self.onSyncType(disp, disp.window.getIPhoneSyncType(data))

    def onSyncType(self, disp, type_):
        disp.push(struct.pack('!i', type_))

        if type_ != 3:
            self.dlg = disp.window.createIPhoneProgressDialog(self.deviceName)
            self.dlg.Started()

        if type_ == 0:
            self.setState(TwoWayState, disp)
        elif type_ == 1:
            self.setState(FullFromDesktopState, disp)
        elif type_ == 2:
            self.setState(FullFromDeviceState, disp)

        # On cancel, the other end will close the connection


class FullFromDesktopState(BaseState):
    def init(self, disp):
        self.tasks = filter(self.isTaskEligible, disp.window.taskFile.tasks())
        self.categories = list([cat for cat in disp.window.taskFile.categories().allItemsSorted() if not cat.isDeleted()])

        disp.pushInteger(len(self.categories))
        disp.pushInteger(len(self.tasks))

        self.total = len(self.categories) + len(self.tasks)
        self.count = 0

        self.setState(FullFromDesktopCategoryState, disp)


class FullFromDesktopCategoryState(BaseState):
    def init(self, disp):
        if self.categories:
            disp.pushString(self.categories[0].subject())
            disp.pushString(self.categories[0].id())
            parent = self.categories[0].parent()
            if parent is None:
                disp.pushString(None)
            else:
                disp.pushString(parent.id())
            self.index = 0
            disp.set_terminator(4)
        else:
            self.setState(FullFromDesktopTaskState, disp)

    def handleData(self, disp, data):
        self.count += 1
        self.dlg.SetProgress(self.count, self.total)

        self.index += 1
        if self.index < len(self.categories):
            disp.pushString(self.categories[self.index].subject())
            disp.pushString(self.categories[self.index].id())
            parent = self.categories[self.index].parent()
            if parent is None:
                disp.pushString(None)
            else:
                disp.pushString(parent.id())

            disp.set_terminator(4)
        else:
            self.setState(FullFromDesktopTaskState, disp)

class FullFromDesktopTaskState(BaseState):
    def init(self, disp):
        if self.tasks:
            disp.pushString(self.tasks[0].subject())
            disp.pushString(self.tasks[0].id())
            disp.pushString(self.tasks[0].description())
            disp.pushDate(self.tasks[0].startDate())
            disp.pushDate(self.tasks[0].dueDate())
            disp.pushDate(self.tasks[0].completionDate())
            disp.pushInteger(len(self.tasks[0].categories()))
            for category in self.tasks[0].categories():
                disp.pushString(category.id())
            self.index = 0
            disp.set_terminator(4)
        else:
            disp.pushString(disp.window.taskFile.guid())
            self.setState(EndState, disp)

    def handleData(self, disp, data):
        code, = struct.unpack('!i', data)

        self.count += 1
        self.dlg.SetProgress(self.count, self.total)

        self.index += 1
        if self.index < len(self.tasks):
            disp.pushString(self.tasks[self.index].subject())
            disp.pushString(self.tasks[self.index].id())
            disp.pushString(self.tasks[self.index].description())
            disp.pushDate(self.tasks[self.index].startDate())
            disp.pushDate(self.tasks[self.index].dueDate())
            disp.pushDate(self.tasks[self.index].completionDate())
            disp.pushInteger(len(self.tasks[self.index].categories()))
            for category in self.tasks[self.index].categories():
                disp.pushString(category.id())
            disp.set_terminator(4)
        else:
            disp.pushString(disp.window.taskFile.guid())
            self.setState(EndState, disp)


class FullFromDeviceState(BaseState):
    def init(self, disp):
        disp.window.clearTasks()
        disp.set_terminator(8)

    def handleData(self, disp, data):
        self.categoryCount, self.taskCount = struct.unpack('!ii', data)
        self.total = self.categoryCount + self.taskCount
        self.count = 0
        self.setState(FullFromDeviceCategoryState, disp)


class FullFromDeviceCategoryState(BaseState):
    def init(self, disp):
        self.length = None
        self.categoryMap = {}
        self.state = 0
        self.parent = None

        if self.categoryCount:
            disp.set_terminator(4)
        else:
            self.setState(FullFromDeviceTaskState, disp)

    def finalize(self, disp):
        if self.parent is None:
            category = Category(self.categoryName)
        else:
            category = self.parent.newChild(self.categoryName)

        disp.window.addIPhoneCategory(category)
        disp.pushString(category.id())
        self.categoryMap[category.id()] = category

        self.categoryCount -= 1
        self.count += 1
        self.dlg.SetProgress(self.count, self.total)

        if self.categoryCount:
            self.state = 0
            self.length = None
            disp.set_terminator(4)
        else:
            self.setState(FullFromDeviceTaskState, disp)

    def handleData(self, disp, data):
        if self.length is None:
            self.length, = struct.unpack('!i', data)
            if self.length == 0:
                self.handleData(disp, '')
            else:
                disp.set_terminator(self.length)
        else:
            if self.state == 0:
                self.categoryName = data.decode('UTF-8')

                if disp.protocolVersion >= 3:
                    self.length = None
                    disp.set_terminator(4)
                    self.state = 1
                    return

                # Version < 3

                self.finalize(disp)
            elif self.state == 1:
                if data:
                    self.parent = self.categoryMap[data.decode('UTF-8')]
                else:
                    self.parent = None

                self.finalize(disp)


class FullFromDeviceTaskState(BaseState):
    def init(self, disp):
        if self.taskCount:
            self.length = None
            self.state = 0
            disp.set_terminator(4)
        else:
            disp.pushString(disp.window.taskFile.guid())
            self.setState(EndState, disp)

    def handleData(self, disp, data):
        if self.length is None:
            self.length, = struct.unpack('!i', data)
            if self.length == 0:
                self.handleData(disp, '')
            else:
                disp.set_terminator(self.length)
        else:
            if self.state == 0:
                self.subject = data.decode('UTF-8')
            elif self.state == 1:
                self.description = data.decode('UTF-8')
            elif self.state == 2:
                self.startDate = parseDate(data)
            elif self.state == 3:
                self.dueDate = parseDate(data)
            elif self.state == 4:
                task = Task(subject=self.subject,
                            description=self.description,
                            startDate=self.startDate,
                            dueDate=self.dueDate,
                            completionDate=parseDate(data))

                self.setState(FullFromDeviceTaskCategoryCountState, disp, task)

            if self.state != 4:
                self.length = None
                self.state += 1
                disp.set_terminator(4)

class FullFromDeviceTaskCategoryCountState(BaseState):
    def init(self, disp, task):
        self.task = task
        disp.set_terminator(4)

    def handleData(self, disp, data):
        self.taskCategoryCount, = struct.unpack('!i', data)
        if self.taskCategoryCount:
            self.setState(FullFromDeviceTaskCategoriesState, disp)
        else:
            disp.pushString(self.task.id())
            self.taskCount -= 1
            self.count += 1
            self.dlg.SetProgress(self.count, self.total)

            if self.taskCount:
                self.setState(FullFromDeviceTaskState, disp)
            else:
                disp.pushString(disp.window.taskFile.guid())
                self.setState(EndState, disp)


class FullFromDeviceTaskCategoriesState(BaseState):
    def init(self, disp):
        self.categories = []
        self.length = None
        disp.set_terminator(4)

    def handleData(self, disp, data):
        if self.length is None:
            self.length, = struct.unpack('!i', data)
            disp.set_terminator(self.length)
        else:
            self.categories.append(self.categoryMap[data.decode('UTF-8')])

            self.taskCategoryCount -= 1
            if self.taskCategoryCount:
                self.length = None
                disp.set_terminator(4)
            else:
                disp.window.addIPhoneTask(self.task, self.categories)
                disp.pushString(self.task.id())
                self.taskCount -= 1
                self.count += 1
                self.dlg.SetProgress(self.count, self.total)

                if self.taskCount:
                    self.setState(FullFromDeviceTaskState, disp)
                else:
                    disp.pushString(disp.window.taskFile.guid())
                    self.setState(EndState, disp)


class TwoWayState(BaseState):
    def init(self, disp):
        if disp.protocolVersion >= 3:
            disp.set_terminator(24)
        else:
            disp.set_terminator(16)

        self.categoryMap = dict()
        for category in disp.window.taskFile.categories():
            self.categoryMap[category.id()] = category

        self.taskMap = dict()
        for task in disp.window.taskFile.tasks():
            self.taskMap[task.id()] = task

    def handleData(self, disp, data):
        if disp.protocolVersion >= 3:
            (self.newCategoriesCount, self.newTasksCount,
             self.deletedTasksCount, self.modifiedTasksCount,
             self.deletedCategoriesCount, self.modifiedCategoriesCount) = struct.unpack('!iiiiii', data)
        else:
            (self.newCategoriesCount, self.newTasksCount,
             self.deletedTasksCount, self.modifiedTasksCount) = struct.unpack('!iiii', data)

        self.setState(TwoWayNewCategoriesState, disp)


class TwoWayNewCategoriesState(BaseState):
    def init(self, disp):
        if self.newCategoriesCount:
            self.parent = None
            self.state = 0
            self.length = None
            disp.set_terminator(4)
        else:
            if disp.protocolVersion >= 3:
                self.setState(TwoWayDeletedCategoriesState, disp)
            else:
                self.setState(TwoWayNewTasksState, disp)

    def finalize(self, disp):
        if self.parent is None:
            category = Category(self.categoryName)
        else:
            category = self.parent.newChild(self.categoryName)

        disp.window.addIPhoneCategory(category)
        disp.pushString(category.id())
        self.categoryMap[category.id()] = category

        self.newCategoriesCount -= 1
        if self.newCategoriesCount:
            self.parent = None
            self.state = 0
            self.length = None
            disp.set_terminator(4)
        else:
            if disp.protocolVersion >= 3:
                self.setState(TwoWayDeletedCategoriesState, disp)
            else:
                self.setState(TwoWayNewTasksState, disp)

    def handleData(self, disp, data):
        if self.length is None:
            self.length, = struct.unpack('!i', data)
            if self.length == 0:
                self.handleData('')
            else:
                disp.set_terminator(self.length)
        else:
            if self.state == 0:
                self.categoryName = data.decode('UTF-8')

                if disp.protocolVersion < 3:
                    self.finalize(disp)
                else:
                    self.state = 1
                    self.length = None
                    disp.set_terminator(4)
            elif self.state == 1:
                if data:
                    self.parent = self.categoryMap[data.decode('UTF-8')]
                else:
                    self.parent = None

                self.finalize(disp)


class TwoWayDeletedCategoriesState(BaseState):
    def init(self, disp):
        if self.deletedCategoriesCount:
            self.length = None
            disp.set_terminator(4)
        else:
            self.setState(TwoWayModifiedCategoriesState, disp)

    def handleData(self, disp, data):
        if self.length is None:
            self.length, = struct.unpack('!i', data)
            disp.set_terminator(self.length)
        else:
            try:
                category = self.categoryMap[data.decode('UTF-8')]
            except KeyError:
                # Probably deleted on the desktop side as well
                pass
            else:
                del self.categoryMap[data.decode('UTF-8')]
                disp.window.removeIPhoneCategory(category)

            self.deletedCategoriesCount -= 1
            if self.deletedCategoriesCount:
                self.length = None
                disp.set_terminator(4)
            else:
                self.setState(TwoWayModifiedCategoriesState, disp)


class TwoWayModifiedCategoriesState(BaseState):
    def init(self, disp):
        print 'MODIFIED', self.modifiedCategoriesCount

        if self.modifiedCategoriesCount:
            self.length = None
            self.state = 0
            disp.set_terminator(4)
        else:
            self.setState(TwoWayNewTasksState, disp)

    def handleData(self, disp, data):
        if self.length is None:
            self.length, = struct.unpack('!i', data)
            if self.length == 0:
                self.handleData('')
            else:
                disp.set_terminator(self.length)
        else:
            if self.state == 0:
                self.categoryName = data.decode('UTF-8')
                self.state = 1
                self.length = None
                disp.set_terminator(4)
            elif self.state == 1:
                try:
                    category = self.categoryMap[data.decode('UTF-8')]
                except KeyError:
                    pass
                else:
                    disp.window.modifyIPhoneCategory(category, self.categoryName)

                    self.modifiedCategoriesCount -= 1
                    if self.modifiedCategoriesCount:
                        self.state = 0
                        self.length = None
                        disp.set_terminator(4)
                    else:
                        self.setState(TwoWayNewTasksState, disp)


class TwoWayNewTasksState(BaseState):
    def init(self, disp):
        if self.newTasksCount:
            self.length = None
            self.state = 0
            disp.set_terminator(4)
        else:
            self.setState(TwoWayDeletedTasksState, disp)

    def handleData(self, disp, data):
        if self.length is None:
            self.length, = struct.unpack('!i', data)
            if self.length == 0:
                self.handleData(disp, '')
            else:
                disp.set_terminator(self.length)
        else:
            if self.state == 0:
                self.subject = data.decode('UTF-8')
            elif self.state == 1:
                self.description = data.decode('UTF-8')
            elif self.state == 2:
                self.startDate = parseDate(data)
            elif self.state == 3:
                self.dueDate = parseDate(data)
            elif self.state == 4:
                task = Task(subject=self.subject,
                            description=self.description,
                            startDate=self.startDate,
                            dueDate=self.dueDate,
                            completionDate=parseDate(data))

                self.setState(TwoWayNewTasksCategoryCountState, disp, task)

            if self.state != 4:
                self.state += 1
                self.length = None
                disp.set_terminator(4)


class TwoWayNewTasksCategoryCountState(BaseState):
    def init(self, disp, task):
        self.task = task
        disp.set_terminator(4)

    def handleData(self, disp, data):
        self.taskCategoryCount, = struct.unpack('!i', data)

        if self.taskCategoryCount:
            self.setState(TwoWayNewTasksCategoriesState, disp)
        else:
            disp.window.addIPhoneTask(self.task, [])
            disp.pushString(self.task.id())
            self.newTasksCount -= 1
            if self.newTasksCount:
                self.setState(TwoWayNewTasksState, disp)
            else:
                self.setState(TwoWayDeletedTasksState, disp)


class TwoWayNewTasksCategoriesState(BaseState):
    def init(self, disp):
        self.categories = []
        self.length = None
        disp.set_terminator(4)

    def handleData(self, disp, data):
        if self.length is None:
            self.length, = struct.unpack('!i', data)
            if self.length == 0:
                self.handleData('')
            else:
                disp.set_terminator(self.length)
        else:
            self.categories.append(self.categoryMap[data.decode('UTF-8')])
            self.taskCategoryCount -= 1
            if self.taskCategoryCount:
                self.length = None
                disp.set_terminator(4)
            else:
                disp.window.addIPhoneTask(self.task, self.categories)
                disp.pushString(self.task.id())
                self.newTasksCount -= 1
                if self.newTasksCount:
                    self.setState(TwoWayNewTasksState, disp)
                else:
                    self.setState(TwoWayDeletedTasksState, disp)


class TwoWayDeletedTasksState(BaseState):
    def init(self, disp):
        if self.deletedTasksCount:
            self.length = None
            disp.set_terminator(4)
        else:
            self.setState(TwoWayModifiedTasks, disp)

    def handleData(self, disp, data):
        if self.length is None:
            self.length, = struct.unpack('!i', data)
            disp.set_terminator(self.length)
        else:
            try:
                task = self.taskMap[data.decode('UTF-8')]
            except KeyError:
                # Probably deleted on the desktop side as well
                pass
            else:
                del self.taskMap[data.decode('UTF-8')]
                disp.window.removeIPhoneTask(task)

            self.deletedTasksCount -= 1
            if self.deletedTasksCount:
                self.length = None
                disp.set_terminator(4)
            else:
                self.setState(TwoWayModifiedTasks, disp)


class TwoWayModifiedTasks(BaseState):
    def init(self, disp):
        if self.modifiedTasksCount:
            self.length = None
            self.state = 0
            disp.set_terminator(4)
        else:
            self.setState(FullFromDesktopState, disp)

    def finalize(self, disp):
        try:
            task = self.taskMap[self.id_]
        except KeyError:
            # Probably deleted on desktop
            pass
        else:
            disp.window.modifyIPhoneTask(task,
                                         self.subject,
                                         self.description,
                                         self.startDate,
                                         self.dueDate,
                                         self.completionDate,
                                         self.categories)

    def handleData(self, disp, data):
        if self.length is None:
            self.length, = struct.unpack('!i', data)
            if self.state == 6: # Protocol version 2 only
                if self.length:
                    self.categoryCount = self.length
                    self.length = None
                    self.state = 7
                    disp.set_terminator(4)
                else:
                    self.finalize(disp)
                    self.modifiedTasksCount -= 1
                    if self.modifiedTasksCount == 0:
                        self.setState(FullFromDesktopState, disp)
                    else:
                        self.state = 0
                        self.length = None
                        disp.set_terminator(4)
            else:
                if self.length == 0:
                    self.handleData(disp, '')
                else:
                    disp.set_terminator(self.length)
        else:
            if self.state == 0:
                self.categories = None
                self.subject = data.decode('UTF-8')
            elif self.state == 1:
                self.id_ = data.decode('UTF-8')
            elif self.state == 2:
                self.description = data.decode('UTF-8')
            elif self.state == 3:
                self.startDate = parseDate(data)
            elif self.state == 4:
                self.dueDate = parseDate(data)
            elif self.state == 5:
                self.completionDate = parseDate(data)

                if disp.protocolVersion == 1:
                    self.finalize(disp)
                    self.modifiedTasksCount -= 1
                else:
                    self.categories = []
                    self.state = 6
            elif self.state == 7:
                self.categories.append(self.categoryMap[data.decode('UTF-8')])
                self.categoryCount -= 1
                if self.categoryCount == 0:
                    self.finalize(disp)
                    self.modifiedTasksCount -= 1
                    if self.modifiedTasksCount == 0:
                        self.setState(FullFromDesktopState, disp)
                    else:
                        self.state = 0
                        self.length = None
                        disp.set_terminator(4)
                        return

            if disp.protocolVersion == 1 or (disp.protocolVersion >= 2 and self.state < 5):
                if self.state == 5 and self.modifiedTasksCount == 0:
                    self.setState(FullFromDesktopState, disp)
                else:
                    self.state = (self.state + 1) % 6

            self.length = None
            disp.set_terminator(4)


class EndState(BaseState):
    def init(self, disp):
        disp.set_terminator(4)

    def handleData(self, disp, data):
        code, = struct.unpack('!i', data) # We don't care right now
        disp.close_when_done()
        self.dlg.Finished()

    def handleClose(self, disp):
        pass
