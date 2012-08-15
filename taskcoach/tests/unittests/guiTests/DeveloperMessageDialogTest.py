'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2012 Task Coach developers <developers@taskcoach.org>

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

from taskcoachlib import config
from taskcoachlib.gui.dialog import developer_message
from unittests import dummy
import test


class DeveloperMessageDialogTest(test.TestCase):
    def setUp(self):
        self.settings = config.Settings(load=False)
        self.dialog = developer_message.MessageDialog(None, message='Message',
                                                      url='http://a.b',
                                                      settings=self.settings)
        
    def testUserPreferenceForMessagesIsSavedInTheSettings(self):
        self.dialog.check_view_developer_messages(False)
        self.dialog.on_close(dummy.Event())
        self.failIf(self.settings.getboolean('view', 'developermessages'))
        
    def testDialogContainsMessage(self):
        self.assertEqual('Message', 
            self.dialog.GetChildren()[0].GetChildren()[0].GetLabel())

    def testDialogContainsURL(self):
        self.assertEqual('http://a.b', self.dialog.GetChildren()[0]. \
                         GetChildren()[1].GetChildren()[1].GetURL())
