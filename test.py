#!/usr/bin/env python

import unittest, sys, os, wx, taskcoach

projectRoot = os.path.split(taskcoach.libpath)[0]
if projectRoot not in sys.path:
    sys.path.insert(0, projectRoot)
if taskcoach.libpath not in sys.path:
    sys.path.insert(0, taskcoach.libpath)
    

class TestCase(unittest.TestCase):
    pass

class wxTestCase(TestCase):
    app = wx.App(0)
    frame = wx.Frame(None, -1, 'Frame')
    from taskcoachlib import gui
    gui.init()


def cvsCommit():
    os.system('cvs ci -m "Automatic commit due to green-bar"')

class AllTests(unittest.TestSuite):
    def __init__(self, options, testFiles):
        super(AllTests, self).__init__()
        self._options = options
        self.loadAllTests(testFiles)

    def filenameToModuleName(self, filename):
        module = filename.replace(os.sep, '.')
        module = module.replace('/', '.')  
        return module[:-3] # strip '.py'

    def loadAllTests(self, testFiles):
        testloader = unittest.TestLoader()
        if not testFiles:
            import glob
            testFiles = glob.glob('unittests/*Test.py')
        for filename in testFiles:
            moduleName = self.filenameToModuleName(filename)
            # Importing the module is not strictly necessary because
            # loadTestsFromName will do that too as a side effect. But if the test 
            # module contains errors our import will raise an exception
            # while loadTestsFromName ignores exceptions when importing from 
            # modules.
            module = __import__(moduleName)
            suite = testloader.loadTestsFromName(moduleName)
            self.addTests(suite._tests)
            self.registerDesiredCoverage(module, moduleName)
        if self._options.coverage:
            self.addTests(self.createCoverageTest()._tests)
   
    def registerDesiredCoverage(self, module, moduleName):
        import unittests.coverage
        for submoduleName in moduleName.split('.')[1:]:
            module = getattr(module, submoduleName)
        if hasattr(module, '__coverage__'):
            for itemToWatch in module.__coverage__:
                unittests.coverage.watch(itemToWatch)
        
    def createCoverageTest(self):
        import unittests.coverage
        class CoverageTest(TestCase):
                def testCoverage(self):
                    self.assertEqual([], unittests.coverage.uncovered())
        return unittest.TestLoader().loadTestsFromTestCase(CoverageTest)
            
    def run(self):       
        testrunner = unittest.TextTestRunner(verbosity=self._options.verbosity)
        result = testrunner.run(self)
        if self._options.commit and result.wasSuccessful():
            cvsCommit()
        return result

import config
class TestOptionParser(config.OptionParser):
    def __init__(self):
        super(TestOptionParser, self).__init__(usage='usage: %prog [options] [testfiles]')

    def testrunOptionGroup(self):
        testrun = config.OptionGroup(self, 'test run options',
            'Options to determine the amount of output while running the '
            'tests.')
        testrun.add_option('-q', '--quiet', action='store_const', default=1,
            const=0, dest='verbosity', help='show only the final test result')
        testrun.add_option('--progress', action='store_const', const=1,
            dest='verbosity', help='show progress [default]')
        testrun.add_option('-v', '--verbose', action='store_const',
            const=2, dest='verbosity', help='show all tests')
        return testrun
 
    def cvsOptionGroup(self):
        cvs = config.OptionGroup(self, 'CVS options', 
            'Options to interact with CVS.')
        cvs.add_option('-c', '--commit', default=False, action='store_true', 
            help='commit if all the tests succeed')
        return cvs

    def profileOptionGroup(self):
        profile = config.OptionGroup(self, 'profile options', 
            'Options to profile the tests to see what test code or production '
            'code is taking the most time. Each of these options imply '
            '--no-commit.')
        profile.add_option('-p', '--profile', default=False, 
            action='store_true', help='profile the running of all the tests')
        profile.add_option('-r', '--report-only', dest='profile_report_only', 
            action='store_true', default=False,
            help="don't make a new profile, report only on the last profile")
        profile.add_option('-s', '--sort', dest='profile_sort', 
            action='append', default=[],
            help="sort key to be used for reporting the profile data. "
            "Possible sort keys are: 'calls', 'cumulative' [default], "
            "'file', 'line', 'module', 'name', 'nfl', 'pcalls', 'stdname', "
            "and 'time'. This option may be repeated")
        profile.add_option('-l', '--limit', dest='profile_limit', default=25, 
            type="int", help="limit the number of calls to show in the "
            "profile reports [defaults to 25]")
        profile.add_option('--regex', dest='profile_regex',
            help='Regular expression to limit the functions shown in the '
           'profile reports')
        return profile

    def coverageOptionGroup(self):
        coverage = config.OptionGroup(self, 'coverage options',
            'Options to test the coverage of the unittests. Requires a '
            '__coverage__ attribute in the unittest file. __coverage__ is '
            'a list of classes or modules to watch for being covered by the '
            'unittests.')
        coverage.add_option('-C', '--coverage', default=True, 
            action='store_true', help='Add one unittest to test for coverage')
        return coverage
        
    def parse_args(self):
        options, args = super(TestOptionParser, self).parse_args()
        if options.profile_report_only:
            options.profile = True
        if not options.profile_sort:
            options.profile_sort.append('cumulative')
        if options.profile or args:
            options.commit = False
        return options, args


class TestProfiler:
    def __init__(self, options, logfile='.profile'):
        self._logfile = logfile
        self._options = options

    def reportLastRun(self):
        import hotshot.stats
        stats = hotshot.stats.load(self._logfile)
        stats.strip_dirs()
        for sortKey in self._options.profile_sort:
            stats.sort_stats(sortKey)
            stats.print_stats(self._options.profile_regex, 
                self._options.profile_limit)
        stats.print_callers()

    def run(self, command, *args, **kwargs):
        if self._options.profile_report_only or self.profile(command, *args, **kwargs):
            self.reportLastRun()

    def profile(self, command, *args, **kwargs):
        import hotshot
        profiler = hotshot.Profile(self._logfile)
        result = profiler.runcall(command, *args, **kwargs)
        if not result.wasSuccessful():
            self.cleanup()
        return result.wasSuccessful()
            
    def cleanup(self, result):
        import os
        os.remove(self._logfile)

    
if __name__ == '__main__':
    options, testFiles = TestOptionParser().parse_args()
    allTests = AllTests(options, testFiles)
    if options.profile:
        TestProfiler(options).run(allTests.run)
    else:
        allTests.run()
