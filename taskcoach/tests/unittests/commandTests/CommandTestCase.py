'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2008 Frank Niessink <frank@niessink.com>

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

import test
from unittests import asserts
from taskcoachlib import patterns


class TestCommand(patterns.Command):
    def __init__(self):
        self.done = False
        self.undone = False
        self.redone = False

    def do(self):
        super(TestCommand, self).do()
        self.done = True

    def undo(self):
        self.undone = True

    def redo(self):
        self.redone = True


class CommandTestCase(test.wxTestCase, asserts.CommandAsserts):
    def tearDown(self):
        super(CommandTestCase, self).tearDown()
        patterns.CommandHistory().clear()

    def push(self):
        patterns.CommandHistory().push()

    def pop(self, keep=True):
        patterns.CommandHistory().pop(keep)

    def hasHistory(self):
        return patterns.CommandHistory().hasHistory()

    def hasFuture(self):
        return patterns.CommandHistory().hasFuture()

    def undo(self):
        patterns.CommandHistory().undo()

    def redo(self):
        patterns.CommandHistory().redo()

    def cut(self, items=None):
        if items == 'all':
            items = list(self.list)
        command.CutCommand(self.list, items or []).do()

    def paste(self):        
        command.PasteCommand(self.list).do()
