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

import os
import test
from taskcoachlib.domain import attachment

        
class FileAttachmentTest(test.TestCase):
    def setUp(self):
        self.attachment = attachment.FileAttachment('filename')
        
    def openAttachment(self, filename):
        self.filename = filename
        
    def testCreateFileAttachment(self):
        self.assertEqual('filename', self.attachment.data())
        
    def testOpenFileAttachmentWithRelativeFilename(self):
        self.attachment.open(openAttachment=self.openAttachment)
        self.assertEqual('filename', self.filename)
        
    def testOpenFileAttachmentWithRelativeFilenameAndWorkingDir(self):
        self.attachment.open('/home', openAttachment=self.openAttachment)
        self.assertEqual(os.path.normpath(os.path.join('/home', 'filename')), 
                         self.filename)
        
    def testOpenFileAttachmentWithAbsoluteFilenameAndWorkingDir(self):
        att = attachment.FileAttachment('/home/frank/attachment.txt')
        att.open('/home/jerome', openAttachment=self.openAttachment)
        self.assertEqual(os.path.normpath(os.path.join('/home/frank/attachment.txt')), 
                         self.filename)
        