import os, test

class ManifestTest(test.TestCase):
    def setUp(self):
        manifestFile = file(os.path.join(test.projectRoot, 'MANIFEST'))
        manifestLines = manifestFile.readlines()
        manifestFile.close()
        self.manifest = [os.path.join(test.projectRoot, filename[:-1]) 
                         for filename in manifestLines]

    def missingPyFiles(self, *dir):
        missing = []
        for root, dirs, files in os.walk(os.path.join(test.projectRoot, *dir)):
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
        self.assertEqual([], self.missingPyFiles('tests', 'unittests'))
    
    def testAllReleasetestPyFilesAreInManifest(self):
        self.assertEqual([], self.missingPyFiles('tests', 'releasetests'))

    def testAllIntegrationtestPyFilesAreInManifest(self):
        self.assertEqual([], self.missingPyFiles('tests', 'integrationtests'))
