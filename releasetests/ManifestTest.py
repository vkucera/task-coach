import os, test

class ManifestTest(test.TestCase):
    def setUp(self):
        manifestLines = file('MANIFEST').readlines()
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
