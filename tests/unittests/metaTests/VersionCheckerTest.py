import test, config, meta
import meta.versionchecker as vc

class VersionCheckerUnderTest(vc.VersionChecker):
    def __init__(self, *args, **kwargs):
        self.version = kwargs.pop('version')
        self.fail = kwargs.pop('fail')
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
        pass
    

class VersionCheckerTest(test.TestCase):
    def setUp(self):
        self.settings = config.Settings(load=False)
        
    def assertLastVersionNotified(self, version, fail=False):
        checker = VersionCheckerUnderTest(self.settings, version=version, 
                                          fail=fail)
        checker.run()
        self.assertEqual(version, self.settings.get('version', 'notified'))
        
    def testLatestVersionIsNewerThanLastVersionNotified(self):
        self.assertLastVersionNotified('99.99')
        
    def testLatestVersionEqualsLastVersionNotified(self):
        self.assertLastVersionNotified(meta.data.version)
        
    def testErrorWhileGettingPadFile(self):
        self.assertLastVersionNotified(meta.data.version, True)
        