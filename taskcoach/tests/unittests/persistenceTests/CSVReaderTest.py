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

import test
from taskcoachlib import persistence

class CSVReaderTestCase(test.TestCase):
    def test_splitline_basic(self):
        self.assertEqual(persistence.splitLines(u'foobar,spam,eggs'), [[u'foobar', u'spam', u'eggs']])

    def test_splitline_quotes(self):
        self.assertEqual(persistence.splitLines(u'foobar,"spam, eggs"'), [[u'foobar', u'spam, eggs']])

    def test_splitline_quoteunquoted(self):
        self.assertEqual(persistence.splitLines(u'foobar,spam"eggs,dummy'), [[u'foobar', u'spam"eggs', u'dummy']])

    def test_splitline_quotequoted(self):
        self.assertEqual(persistence.splitLines(u'foobar,"spam""eggs",dummy'), [[u'foobar', u'spam"eggs', u'dummy']])

    def test_splitline_other_escaped(self):
        self.assertEqual(persistence.splitLines(u'foobar,"spam\\neggs"'), [[u'foobar', u'spam\\neggs']])

    def test_splitline_other_escaped_unquoted(self):
        self.assertEqual(persistence.splitLines(u'foobar,spam\\neggs'), [[u'foobar', u'spam\\neggs']])

    def test_splitline_multiline(self):
        self.assertEqual(persistence.splitLines(u'foobar,"spam\neggs",dummy'), [[u'foobar', u'spam\neggs', u'dummy']])

    def test_splitlines_noeol(self):
        self.assertEqual(persistence.splitLines(u'a,b\nc,d'), [['a', 'b'], ['c', 'd']])

    def test_splitlines_eol(self):
        self.assertEqual(persistence.splitLines(u'a,b\nc,d\n'), [['a', 'b'], ['c', 'd']])

    def test_splitlines_noeol_crlf(self):
        self.assertEqual(persistence.splitLines(u'a,b\r\nc,d'), [['a', 'b'], ['c', 'd']])

    def test_splitlines_eol_crlf(self):
        self.assertEqual(persistence.splitLines(u'a,b\r\nc,d\r\n'), [['a', 'b'], ['c', 'd']])
