import os, test

class ManifestTest(test.TestCase):
    def setUp(self):
        manifestFile = file(os.path.join(test.projectRoot, 'MANIFEST'))
        manifestLines = manifestFile.readlines()
        manifestFile.close()
        self.manifest = [filename[:-1] for filename in manifestLines]

    def missingPyFiles(self, dir):
        missing = []
        for root, dirs, files in os.walk(dir):
            pyfiles = [os.path.join(root, filename) for filename in files 
                       if filename.endswith('.py')]
            for filename in pyfiles:
                if filename not in self.manifest:
                    missing.append(filename)
            if 'CVS' in dirs:
                dirs.remove('CVS')
        return missing

    def testAllSourcePyFilesAreInManifest(self):
        self.assertEqual([], self.missingPyFiles('taskcoachlib'))

    def testAllUnittestPyFilesAreInManifest(self):
        self.assertEqual([], self.missingPyFiles('unittests'))
    
    def testAllReleasetestPyFilesAreInManifest(self):
        self.assertEqual([], self.missingPyFiles('releasetests'))

    def testAllIntegrationtestPyFilesAreInManifest(self):
        self.assertEqual([], self.missingPyFiles('integrationtests'))
