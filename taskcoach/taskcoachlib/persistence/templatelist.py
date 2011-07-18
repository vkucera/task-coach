'''
Task Coach - Your friendly task manager
CCopyright (C) 2004-2011 Task Coach developers <developers@taskcoach.org>

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

import os, pickle, tempfile, codecs, shutil

from taskcoachlib.persistence import TemplateXMLWriter, TemplateXMLReader
from taskcoachlib import patterns


class TemplateList(object):
    def __init__(self, path):
        self._path = path

        fileList = [name for name in os.listdir(self._path) if \
                    name.endswith('.tsktmpl') and os.path.exists(os.path.join(self._path, name))]

        listName = os.path.join(self._path, 'list.pickle')
        if os.path.exists(listName):
            try:
                fileList = pickle.load(file(listName, 'rb'))
            except:
                pass
        
        self._tasks = []
        for filename in fileList:
            try:
                fd = file(os.path.join(self._path, filename), 'rU')
                self._tasks.append((TemplateXMLReader(fd).read(), filename))
            except IOError:
                pass
            finally:
                fd.close()

        self._toDelete = []

    def _copyTask(self, task):
        copy = task.copy()
        for name in ['startdatetmpl', 'duedatetmpl', 'completiondatetmpl', 'remindertmpl']:
            if hasattr(task, name):
                setattr(copy, name, getattr(task, name))
        return copy

    def save(self):
        pickle.dump([name for task, name in self._tasks], file(os.path.join(self._path, 'list.pickle'), 'wb'))

        for task, name in self._tasks:
            templateFile = codecs.open(os.path.join(self._path, name), 'w', 'utf-8')
            writer = TemplateXMLWriter(templateFile)
            writer.write(self._copyTask(task))

        for task, name in self._toDelete:
            os.remove(os.path.join(self._path, name))
        self._toDelete = []
        patterns.Event('templates.saved', self).send()

    def addTemplate(self, task):
        handle, filename = tempfile.mkstemp('.tsktmpl', dir=self._path)
        os.close(handle)
        templateFile = codecs.open(filename, 'w', 'utf-8')
        writer = TemplateXMLWriter(templateFile)
        writer.write(task.copy())
        templateFile.close()
        self._tasks.append((TemplateXMLReader(file(filename, 'rU')).read(), os.path.split(filename)[-1]))

    def deleteTemplate(self, idx):
        self._toDelete.append(self._tasks[idx])
        del self._tasks[idx]

    def copyTemplate(self, filename):
        shutil.copyfile(filename,
                        os.path.join(self._path, os.path.split(filename)[-1]))
        patterns.Event('templates.saved', self).send()
        
    def swapTemplates(self, i, j):
        self._tasks[i], self._tasks[j] = self._tasks[j], self._tasks[i]

    def __len__(self):
        return len(self._tasks)

    def tasks(self):
        return [task for task, name in self._tasks]

    def names(self):
        return [name for task, name in self._tasks]
