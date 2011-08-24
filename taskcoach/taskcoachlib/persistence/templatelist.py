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

import os, pickle, tempfile, shutil
from taskcoachlib import patterns
from xml import TemplateXMLWriter, TemplateXMLReader


class TemplateList(object):
    def __init__(self, path, TemplateXMLReader=TemplateXMLReader, file=file):
        self._path = path
        self._templates = self._readTemplates(TemplateXMLReader, file)
        self._toDelete = []

    def _readTemplates(self, TemplateXMLReader, file):
        templates = []
        for filename in self._templateFilenames():
            template = self._readTemplate(filename, TemplateXMLReader, file)
            if template:
                templates.append((template, filename))
        return templates
    
    def _readTemplate(self, filename, TemplateXMLReader, file):
        try:
            fd = file(os.path.join(self._path, filename), 'rU')
        except IOError:
            return
        try:
            return TemplateXMLReader(fd).read()
        except:
            pass
        finally:
            fd.close()

    def _templateFilenames(self):
        filenames = [name for name in os.listdir(self._path) if \
                    name.endswith('.tsktmpl') and os.path.exists(os.path.join(self._path, name))]
        listName = os.path.join(self._path, 'list.pickle')
        if os.path.exists(listName):
            try:
                filenames = pickle.load(file(listName, 'rb'))
            except:
                pass
        return filenames
    
    def save(self):
        pickle.dump([name for task, name in self._templates], file(os.path.join(self._path, 'list.pickle'), 'wb'))

        for task, name in self._templates:
            templateFile = file(os.path.join(self._path, name), 'w')
            writer = TemplateXMLWriter(templateFile)
            writer.write(task)
            templateFile.close()

        for task, name in self._toDelete:
            os.remove(os.path.join(self._path, name))
        self._toDelete = []
        patterns.Event('templates.saved', self).send()

    def addTemplate(self, task):
        handle, filename = tempfile.mkstemp('.tsktmpl', dir=self._path)
        os.close(handle)
        templateFile = file(filename, 'w')
        writer = TemplateXMLWriter(templateFile)
        writer.write(task.copy())
        templateFile.close()
        self._templates.append((TemplateXMLReader(file(filename, 'rU')).read(), os.path.split(filename)[-1]))

    def deleteTemplate(self, idx):
        self._toDelete.append(self._templates[idx])
        del self._templates[idx]

    def copyTemplate(self, filename):
        shutil.copyfile(filename,
                        os.path.join(self._path, os.path.split(filename)[-1]))
        patterns.Event('templates.saved', self).send()
        
    def swapTemplates(self, i, j):
        self._templates[i], self._templates[j] = self._templates[j], self._templates[i]

    def __len__(self):
        return len(self._templates)

    def tasks(self):
        return [task for task, name in self._templates]

    def names(self):
        return [name for task, name in self._templates]
