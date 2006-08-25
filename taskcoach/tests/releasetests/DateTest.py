import test

class DateTest(test.TestCase):
    def testNoQuestionMarkInMetaDataDate(self):
        import meta
        self.failIf('?' in meta.date)

    def testNoQuestionMarkInChangeLog(self):
        import sys, os.path
        sys.path.insert(0, os.path.join(test.projectRoot, 'changes.in'))
        import changes
        self.failIf('?' in changes.releases[0].date)
