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