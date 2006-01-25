#!/usr/bin/env python

import unittest, sys, os, taskcoach, wx, time, glob

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


class TestResultWithTimings(unittest._TextTestResult):
    def __init__(self, *args, **kwargs):
        super(TestResultWithTimings, self).__init__(*args, **kwargs)
        self._timings = {}

    def startTest(self, test):
        super(TestResultWithTimings, self).startTest(test)
        self._timings[test] = time.time()
        
    def stopTest(self, test):
        super(TestResultWithTimings, self).stopTest(test)
        self._timings[test] = time.time() - self._timings[test]


class TextTestRunnerWithTimings(unittest.TextTestRunner):
    def __init__(self, nrTestsToReport, timeTests=False, *args, **kwargs):
        super(TextTestRunnerWithTimings, self).__init__(*args, **kwargs)
        self._timeTests = timeTests
        self._nrTestsToReport = nrTestsToReport

    def _makeResult(self):
        return TestResultWithTimings(self.stream, self.descriptions, 
            self.verbosity)

    def run(self, *args, **kwargs):
        result = super(TextTestRunnerWithTimings, self).run(*args, **kwargs)
        if self._timeTests:
            sortableTimings = [(time, test) for test, time in result._timings.items()]
            sortableTimings.sort(reverse=True)
            print '\n%d slowest tests:'%self._nrTestsToReport
            for time, test in sortableTimings[:self._nrTestsToReport]:
                print '%s (%.2f)'%(test, time)
        return result


class AllTests(unittest.TestSuite):
    def __init__(self, options=None, testFiles=None):
        super(AllTests, self).__init__()
        self._options = options or TestOptionParser().parse_args()[0]
        self.loadAllTests(testFiles or [])

    def filenameToModuleName(self, filename):
        module = filename.replace(os.sep, '.')
        module = module.replace('/', '.')  
        return module[:-3] # strip '.py'

    def getTestFilesFromDir(self, directory):
        return glob.glob(os.path.join(directory, '*Test.py')) + \
            glob.glob(os.path.join(directory, '*', '*Test.py'))

    def loadAllTests(self, testFiles):
        testloader = unittest.TestLoader()
        if not testFiles:
            testfiles = []
            if self._options.unittests:
                testFiles.extend(self.getTestFilesFromDir('unittests'))
            if self._options.integrationtests:
                testFiles.extend(self.getTestFilesFromDir('integrationtests'))
            if self._options.releasetests:
                testFiles.extend(self.getTestFilesFromDir('releasetests'))
        for filename in testFiles:
            moduleName = self.filenameToModuleName(filename)
            # Importing the module is not strictly necessary because
            # loadTestsFromName will do that too as a side effect. But if the 
            # test module contains errors our import will raise an exception
            # while loadTestsFromName ignores exceptions when importing from 
            # modules.
            module = __import__(moduleName)
            suite = testloader.loadTestsFromName(moduleName)
            self.addTests(suite._tests)
   
    def runTests(self):       
        testrunner = TextTestRunnerWithTimings(
            verbosity=self._options.verbosity,
            timeTests=self._options.time,
            nrTestsToReport=self._options.time_reports)
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
        testrun.add_option('-t', '--time', default=False, action='store_true', 
            help='time the tests and report the slowest tests')
        testrun.add_option('--time-reports', default=10, type='int',
            help='the number of slow tests to report [%default]')
        return testrun

    def cvsOptionGroup(self):
        cvs = config.OptionGroup(self, 'CVS options', 
            'Options to interact with CVS.')
        cvs.add_option('-c', '--commit', default=False, action='store_true', 
            help='commit if all the tests succeed'
                 ' (implies --unittests and --integrationtests)')
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
            "profile reports [%default]")
        profile.add_option('--regex', dest='profile_regex',
            help='Regular expression to limit the functions shown in the '
           'profile reports')
        return profile

    def coverageOptionGroup(self):
        coverage = config.OptionGroup(self, 'coverage options',
            'Options to determine which tests to run.')

        coverage.add_option('--unittests', default=True,
            action='store_true', help='run the unit tests [default]')
        coverage.add_option('--no-unittests', action='store_false', 
            help="don't run the unit tests", dest='unittests')

        coverage.add_option('--integrationtests', default=False,
            action='store_true', help='run the integration tests')
        coverage.add_option('--no-integrationtests', action='store_false', 
            help="don't run the integration tests [default]",
            dest='integrationtests')

        coverage.add_option('--releasetests', default=False,
            action='store_true', help='run the release tests')
        coverage.add_option('--no-releasetests', action='store_false', 
            help="don't run the release tests [default]", dest='releasetests')

        coverage.add_option('--alltests', default=False,
            action='store_true', help='run all tests')
        return coverage
        
    def parse_args(self):
        options, args = super(TestOptionParser, self).parse_args()
        if options.profile_report_only:
            options.profile = True
        if not options.profile_sort:
            options.profile_sort.append('cumulative')
        if options.alltests:
            options.unittests = True
            options.integrationtests = True
            options.releasetests = True
        if options.profile or args:
            options.commit = False
        if options.commit:
            options.unittests = True
            options.integrationtests = True
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
        #stats.print_callers()

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
        TestProfiler(options).run(allTests.runTests)
    else:
        allTests.runTests()
