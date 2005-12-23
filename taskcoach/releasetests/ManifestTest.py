import os, test

class ManifestTest(test.TestCase):
    def testAllPyFilesAreInManifest(self):
        manifest = file('MANIFEST').readlines()
        manifest = [filename[:-1] for filename in manifest]
        missing = []
        for root, dirs, files in os.walk('taskcoachlib'):
            pyfiles = [os.path.join(root, filename) for filename in files 
                       if filename.endswith('.py')]
            for filename in pyfiles:
                if filename not in manifest:
                    missing.append(filename)
            if 'CVS' in dirs:
                dirs.remove('CVS')
        self.assertEqual([], missing)
