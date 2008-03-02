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

import sys, os, test, meta
sys.path.append(os.path.join(test.projectRoot, 'changes.in'))
import changes

class ChangeHistoryTestCase(test.TestCase):
    def setUp(self):
        self.latestRelease = changes.releases[0]
        
    def testLatestReleaseNumberEqualsMetaDataReleaseNumber(self):
        self.assertEqual(self.latestRelease.number, meta.data.version)

    def testLatestReleaseDateEqualsMetaDataReleaseDate(self):
        self.assertEqual(self.latestRelease.date, meta.data.date)
        
    def testLatestReleaseHasDate(self):
        self.failIf('?' in self.latestRelease.date)
        
    def testLatestReleaseHasBugsFixedOrFeaturesAdded(self):
        self.failUnless(self.latestRelease.bugsFixed or \
                        self.latestRelease.featuresAdded)
        
    def testLatestReleaseNumberIsHigherThanPreviousReleaseNumber(self):
        self.failUnless(self.latestRelease.number > changes.releases[1].number)
        
    def testLatestReleaseSummaryLength(self):
        self.failUnless(25 <= len(self.latestRelease.summary) < 600)

