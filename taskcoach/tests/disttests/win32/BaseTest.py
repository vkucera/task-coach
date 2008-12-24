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

import os, time, base


class TestLaunch(base.Win32TestCase):
    def test_launch(self):
        window = self.findWindow(r'^Task Coach$')
        self.failIf(window is None,
                    'Cannot find main window')


class TestWithTaskFile(base.Win32TestCase):
    def setUp(self):
        self.args = [os.path.join(self.basepath, 'testfile.tsk')]
        super(TestWithTaskFile, self).setUp()

    def test_launch(self):
        self.failUnless(self.findWindow(r'^Task Coach file error$') is None,
                        'Error dialog appeared')
        window = self.findWindow(r'^Task Coach')
        self.failIf(window is None,
                    'Cannot find main window')
        self.failUnless(window.title.endswith('testfile.tsk'),
                        'Wrong window title')

    def test_save(self):
        timestamp = os.stat(self.args[0]).st_mtime

        mainwindow = self.findWindow(r'^Task Coach')
        w = mainwindow.findChildren('wxWindowClassNR', 'treelistctrl')

        w[1].clickAt(5, 30)
        w[1].clickAt(5, 30)

        editor = self.findWindow(r'^Edit task')
        self.failIf(editor is None, 'Task editor not found')
        editor.waitFocus()

        editor.findChildren('Button', 'OK')[0].clickAt(5, 5)

        mainwindow.waitFocus()
        mainwindow.clickAt(58, 15) # Save button

        time.sleep(2)

        if os.path.exists(self.logfilename):
            self.fail('Exception occurred while saving:\n' + file(self.logfilename, 'rb').read())

        self.failUnless(os.stat(self.args[0]).st_mtime > timestamp,
                        'File was not written')
        self.assertNotEqual(os.path.getsize(self.args[0]), 0)
