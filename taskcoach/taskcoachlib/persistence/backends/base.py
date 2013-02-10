'''
Task Coach - Your friendly task manager
Copyright (C) 2013 Task Coach developers <developers@taskcoach.org>

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


from taskcoachlib.changes import ChangeMonitor
from taskcoachlib.domain import task, category, note, effort, attachment


class Backend(object):
    def __init__(self, store):
        super(Backend, self).__init__()

        self.__monitor = ChangeMonitor()
        for collection in [store.tasks(), store.categories(), store.notes()]:
            self.__monitor.monitorCollection(collection)
        for domainClass in [task.Task, category.Category, note.Note, effort.Effort,
                            attachment.FileAttachment, attachment.URIAttachment,
                            attachment.MailAttachment]:
            self.__monitor.monitorClass(domainClass)

    def __repr__(self):
        return 'FileBackend(%s)' % self.__monitor.guid()

    def monitor(self):
        return self.__monitor

    def guid(self):
        return self.__monitor.guid()

    def clear(self, store):
        pass

    def stop(self, store):
        for collection in [store.tasks(), store.categories(), store.notes()]:
            self.__monitor.unmonitorCollection(collection)
        for domainClass in [task.Task, category.Category, note.Note, effort.Effort,
                            attachment.FileAttachment, attachment.URIAttachment,
                            attachment.MailAttachment]:
            self.__monitor.unmonitorClass(domainClass)

    def reset(self):
        self.__monitor.resetAllChanges()

    def dirty(self):
        return any([changes is None or changes for changes in self.__monitor.allChanges().values()])

    def lock(self):
        pass

    def unlock(self):
        pass
