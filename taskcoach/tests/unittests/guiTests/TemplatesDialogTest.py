'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2010 Task Coach developers <developers@taskcoach.org>

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

import test, os, shutil
from taskcoachlib import gui, command, config, persistence
from taskcoachlib.domain import note, attachment

 
class TemplatesDialogTestCase(test.wxTestCase):
    def setUp(self):
        super(TemplatesDialogTestCase, self).setUp()
        self.settings = config.Settings(load=False)

        # Monkey-patching
        path = os.path.join(os.path.split(__file__)[0], 'tmpl')
        try:
            shutil.rmtree(path)
        except OSError:
            pass
        os.mkdir(path)

        self.settings.pathToTemplatesDir = lambda: path

        self.taskFile = persistence.TaskFile()
        self.editor = gui.dialog.templates.TemplatesDialog(self.settings, self.frame, 
            'title', raiseDialog=False)

    def testTwoDefaultTemplates(self):
        self.assertEqual(0, len(self.editor._templates.tasks()))
