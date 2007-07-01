import os, test, setup


class LineEndingsTest(test.TestCase):
    def testNoDOSLineEndingsInPythonScripts(self):
        ''' On Linux, scripts won't work if they have DOS line endings. '''
        scripts = [os.path.join(test.projectRoot, script) \
                   for script in setup.setupOptions['scripts'] \
                   if script.endswith('.py')]
        for script in scripts:
            self.failIf('\r\n' in file(script, 'rb').read(), 
                        '%s contains DOS line endings'%script)
