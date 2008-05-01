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
from taskcoachlib import config, meta
#from taskcoachlib.meta import versionchecker


class VersionCheckerUnderTest(meta.VersionChecker):
    def __init__(self, *args, **kwargs):
        self.version = kwargs.pop('version')
        self.fail = kwargs.pop('fail', False)
        self.userNotified = False
        super(VersionCheckerUnderTest, self).__init__(*args, **kwargs)
        
    def retrievePadFile(self):
        if self.fail:
            import urllib2
            raise urllib2.HTTPError(None, None, None, None, None)
        else:
            import StringIO
            return StringIO.StringIO('<?xml version="1.0" encoding="UTF-8" ?>\n'
                                     '<XML_DIZ_INFO><Program_Info>'
                                     '<Program_Version>%s</Program_Version>'
                                     '</Program_Info></XML_DIZ_INFO>'%self.version)
            
    def notifyUser(self, *args, **kwargs):
        self.userNotified = True
    

class VersionCheckerTest(test.TestCase):
    def setUp(self):
        self.settings = config.Settings(load=False)
        
    def checkVersion(self, version, fail=False):
        checker = VersionCheckerUnderTest(self.settings, version=version, 
                                          fail=fail)
        checker.run()
        return checker
        
    def assertLastVersionNotified(self, version, fail=False):
        self.checkVersion(version, fail)
        self.assertEqual(version, self.settings.get('version', 'notified'))
        
    def testLatestVersionIsNewerThanLastVersionNotified(self):
        self.assertLastVersionNotified('99.99')
        
    def testLatestVersionEqualsLastVersionNotified(self):
        self.assertLastVersionNotified(meta.data.version)
        
    def testErrorWhileGettingPadFile(self):
        self.assertLastVersionNotified(meta.data.version, True)
        
    def testDontNotifyWhenCurrentVersionIsNewerThanLastVersionNotified(self):
        self.settings.set('version', 'notified', '0.0')
        checker = self.checkVersion(meta.data.version)
        self.failIf(checker.userNotified)

